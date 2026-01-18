from __future__ import annotations

from datetime import datetime, timedelta
import re
import csv
import glob

MODE_TO_TYPE = {
    "WALK": "walk",
    "BUS": "bus",
    "SUBWAY": "subway",
    "EXPRESS BUS": "bus",
    "TRAIN": "train",
    "AIRPLANE": "air",
    "FERRY": "ferry"
}

LINE_FALLBACK = {"walk": "walk"}

def _parse_search_time(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y%m%d%H%M", "%Y%m%d%H%M%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None

def _format_arrival(start_dt: datetime | None, total_sec: int) -> str:
    if not start_dt:
        return ""
    arrival = start_dt + timedelta(seconds=total_sec)
    return arrival.strftime("%H:%M")

def _mode_type(mode: str) -> str:
    return MODE_TO_TYPE.get(mode, "walk")

_SUBWAY_STATION_BY_LINE: dict[int, set[str]] | None = None
_SUBWAY_NAME_BY_LINE_AND_ID: dict[tuple[int, int], str] | None = None

def _safe_int(value: str | int | None) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None

def _load_subway_station_lookup() -> tuple[dict[int, set[str]], dict[tuple[int, int], str]]:
    global _SUBWAY_STATION_BY_LINE, _SUBWAY_NAME_BY_LINE_AND_ID
    if _SUBWAY_STATION_BY_LINE is not None and _SUBWAY_NAME_BY_LINE_AND_ID is not None:
        return _SUBWAY_STATION_BY_LINE, _SUBWAY_NAME_BY_LINE_AND_ID

    lookup: dict[int, set[str]] = {}
    id_lookup: dict[tuple[int, int], str] = {}

    for path in glob.glob("static/data/subway_data/*.csv"):
        try:
            with open(path, "r", encoding="EUC-KR") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    line_num = _safe_int(row.get("호선"))
                    name = row.get("출발역")
                    station_id = _safe_int(row.get("역번호"))
                    if line_num is None or not name:
                        continue
                    cleaned = name.strip()
                    lookup.setdefault(line_num, set()).add(cleaned)
                    if station_id is not None:
                        id_lookup[(line_num, station_id)] = cleaned
        except OSError:
            continue

    _SUBWAY_STATION_BY_LINE = lookup
    _SUBWAY_NAME_BY_LINE_AND_ID = id_lookup
    return lookup, id_lookup

def _parse_line_number(line: str) -> int | None:
    match = re.search(r"\d+", str(line))
    if not match:
        return None
    return _safe_int(match.group(0))

def _direction_from_route(route: str, line_num: int | None) -> str:
    if route:
        if "상선" in route: return "상선"
        if "하선" in route: return "하선"
        if "내선" in route: return "내선"
        if "외선" in route: return "외선"
    if line_num == 2:
        return "내선"
    return "상선"

def _line_for_leg(leg: dict) -> str:
    mode = leg.get("mode", "")
    leg_type = _mode_type(mode)
    if leg_type in LINE_FALLBACK:
        return LINE_FALLBACK[leg_type]

    route = leg.get("route", "")
    if leg_type == "bus":
        return route or leg_type

    match = re.search(r"\d+", route)
    if match:
        return match.group(0)
    return leg_type

def _congestion_color(score: int) -> str:
    if score >= 80:
        return "#ef4444"
    if score >= 40:
        return "#eab308"
    return "#22c55e"

def _normalize_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not points:
        return []
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    def scale(val: float, min_val: float, max_val: float) -> float:
        if max_val == min_val:
            return 50.0
        return 10.0 + (val - min_val) * 80.0 / (max_val - min_val)

    return [(scale(lon, min_lon, max_lon), scale(lat, min_lat, max_lat)) for lon, lat in points]

def parse_routes(raw: dict, search_dttm: str | None = None) -> list[dict]:
    itineraries = raw.get("metaData", {}).get("plan", {}).get("itineraries", [])
    routes: list[dict] = []
    start_dt = _parse_search_time(search_dttm)
    placeholder_names = {"출발지", "도착지"}

    # BUS 정류장: TMAP stationID -> (우리 데이터 ARS_ID) 변환 맵
    bus_ars_by_name = {}
    if start_dt:
        try:
            from parsers.bus_id_parser import get_busStationID
            bus_ars_by_name = get_busStationID(raw)  # {stationName: ARS_ID}
        except Exception:
            bus_ars_by_name = {}

    def resolve_leg_names(leg: dict) -> tuple[str | None, str | None]:
        mode = leg.get("mode", "")
        start = leg.get("start", {})
        end = leg.get("end", {})
        start_name = start.get("name")
        end_name = end.get("name")
        distance = float(leg.get("distance", 0) or 0)

        if mode == "WALK" and distance == 0:
            if start_name in placeholder_names and end_name and end_name not in placeholder_names:
                start_name = end_name
            if end_name in placeholder_names and start_name and start_name not in placeholder_names:
                end_name = start_name

        if mode == "SUBWAY":
            stations = leg.get("passStopList", {}).get("stations", [])
            if start_name in placeholder_names and stations:
                start_name = stations[0].get("stationName") or start_name
            if end_name in placeholder_names and stations:
                end_name = stations[-1].get("stationName") or end_name

        return start_name, end_name

    for idx, item in enumerate(itineraries, start=1):
        total_time_sec = int(item.get("totalTime", 0) or 0)
        legs = item.get("legs", [])

        transit_modes = ("BUS", "SUBWAY", "TRAIN", "EXPRESS BUS", "AIRPLANE", "FERRY")
        transit_legs = [l for l in legs if l.get("mode") in transit_modes]

        # 환승 횟수 계산
        transfer_count = 0
        previous_transit = None
        for leg in transit_legs:
            transit_mode = _mode_type(leg.get("mode", ""))
            transit_line = _line_for_leg(leg)
            current = {"mode": transit_mode, "line": transit_line}
            if previous_transit and previous_transit != current:
                transfer_count += 1
            previous_transit = current

        total_walk_time_sec = int(item.get("totalWalkTime", 0) or 0)
        if not total_walk_time_sec:
            total_walk_time_sec = sum(int(l.get("sectionTime", 0) or 0) for l in legs if l.get("mode") == "WALK")

        fare = item.get("fare", {}).get("regular", {}).get("totalFare", 0)

        crowd_score = None
        if start_dt:
            has_subway = False
            has_bus = False
            subway_time_sec = 0
            bus_time_sec = 0
            elapsed_sec = 0

            station_lookup, _ = _load_subway_station_lookup()
            missing_subway_station = False
            missing_bus_stop = False

            # 각 point에 "datetime"까지 저장해서 뒤에서 시간 꼬임 방지
            subway_points = []  # (station_name, line_num, dt, direction)
            bus_points = []     # (bus_route_str, ars_id, dt)

            for leg in legs:
                mode = leg.get("mode", "")
                section_sec = int(leg.get("sectionTime", 0) or 0)
                leg_start_dt = start_dt + timedelta(seconds=elapsed_sec)

                if mode == "SUBWAY":
                    line_num = _parse_line_number(_line_for_leg(leg))
                    if line_num is None:
                        missing_subway_station = True
                    else:
                        direction = _direction_from_route(leg.get("route", ""), line_num)
                        valid_stations = station_lookup.get(line_num, set())
                        stations = leg.get("passStopList", {}).get("stations") or []
                        if not stations:
                            missing_subway_station = True

                        for st in stations:
                            raw_name = (st.get("stationName") or "").strip()
                            if not raw_name:
                                missing_subway_station = True
                                continue

                            candidate = raw_name

                            if candidate not in valid_stations:
                                missing_subway_station = True
                                continue

                            subway_points.append((candidate, line_num, leg_start_dt, direction))

                        has_subway = True
                        subway_time_sec += section_sec

                elif mode == "BUS":
                    stations = (
                        leg.get("passStopList", {}).get("stations")
                        or leg.get("passStopList", {}).get("stationList")
                        or []
                    )
                    bus_route = leg.get("route", "")

                    bus_route_raw = leg.get("route", "")

                    # 숫자 노선번호만 추출 (예: "간선:3216" -> 3216)
                    m = re.search(r"\d+", str(bus_route_raw))
                    bus_num = int(m.group(0)) if m else None

                    if bus_num is None or not stations:
                        missing_bus_stop = True
                    else:
                        for st in stations:
                            stop_name = (st.get("stationName") or "").strip()
                            if not stop_name:
                                missing_bus_stop = True
                                continue

                            ars_id = bus_ars_by_name.get(stop_name)
                            if not ars_id:
                                missing_bus_stop = True
                                continue

                            # pred_bus에 bus_num(int) 넘기도록 저장
                            bus_points.append((bus_num, int(ars_id), leg_start_dt))

                        has_bus = True
                        bus_time_sec += section_sec

                elapsed_sec += section_sec

            # 경로 내 역/정류장 하나라도 학습 데이터 없으면 -> crowdScore None
            if missing_subway_station or missing_bus_stop:
                crowd_score = None
            else:
                try:
                    # 버스만 / 지하철만이면 해당 모델로 평균
                    if has_subway and not has_bus:
                        from services.subway_service import pred_subway
                        preds = []
                        for (st_name, line_num, dt, direction) in subway_points:
                            r = pred_subway(st_name, line_num, dt, direction)
                            if r == -1:
                                preds = None
                                break
                            preds.append(r)
                        crowd_score = (sum(preds) / len(preds)) if preds else None

                    elif has_bus and not has_subway:
                        from services.bus_service import pred_bus
                        preds = []
                        for (bus_route, ars_id, dt) in bus_points:
                            r = pred_bus(bus_num, ars_id, dt)
                            if r == -1:
                                preds = None
                                break
                            preds.append(r)
                        crowd_score = (sum(preds) / len(preds)) if preds else None

                    else:
                        # 혼합은 integrate로 가되, integrate가 -1이면 None
                        from services.intergrate_service import pred_intergrate
                        subway_min = subway_time_sec / 60.0
                        bus_min = bus_time_sec / 60.0
                        
                        from services.subway_service import pred_subway
                        from services.bus_service import pred_bus

                        preds = []
                        for (st_name, line_num, dt, direction) in subway_points:
                            r = pred_subway(st_name, line_num, dt, direction)
                            if r == -1:
                                preds = None
                                break
                            preds.append(r)

                        if preds is not None:
                            for (bus_route, ars_id, dt) in bus_points:
                                r = pred_bus(bus_route, ars_id, dt)
                                if r == -1:
                                    preds = None
                                    break
                                preds.append(r)

                        crowd_score = (sum(preds) / len(preds)) if preds else None

                except Exception:
                    crowd_score = None

                if crowd_score == -1:
                    crowd_score = None

        # ---------- 이하: UI 표시용 pathDisplay / mapSegments 구성 ----------
        stops = []
        def add_stop(name: str | None, mode: str, line: str):
            if not name:
                return
            new_type = _mode_type(mode)
            if stops and stops[-1]["name"] == name:
                if stops[-1]["type"] == "walk" and new_type != "walk":
                    stops[-1]["type"] = new_type
                    stops[-1]["line"] = line
                return
            stops.append({"type": new_type, "line": line, "name": name})

        coords = []
        map_points = []
        map_segments = []
        for leg in legs:
            mode = leg.get("mode", "")
            line = _line_for_leg(leg)
            start = leg.get("start", {})
            end = leg.get("end", {})
            start_name, end_name = resolve_leg_names(leg)
            add_stop(start_name, mode, line)
            add_stop(end_name, mode, line)

            if "lon" in start and "lat" in start:
                coords.append((float(start["lon"]), float(start["lat"])))
                point = {"lat": float(start["lat"]), "lon": float(start["lon"])}
                if not map_points or map_points[-1] != point:
                    map_points.append(point)

            if "lon" in end and "lat" in end:
                coords.append((float(end["lon"]), float(end["lat"])))
                point = {"lat": float(end["lat"]), "lon": float(end["lon"])}
                if not map_points or map_points[-1] != point:
                    map_points.append(point)

                map_segments.append({
                    "start": {"lat": float(start.get("lat", end["lat"])), "lon": float(start.get("lon", end["lon"]))},
                    "end": {"lat": float(end["lat"]), "lon": float(end["lon"])},
                    "congestionColor": _congestion_color(int(crowd_score)) if crowd_score is not None else "#9ca3af",
                    "line": line,
                    "type": _mode_type(mode)
                })

        path_summary = " - ".join([s["name"] for s in stops]) or "Route"
        arrival_time = _format_arrival(start_dt, total_time_sec)

        walk_min = max(0, int(round(total_walk_time_sec / 60)))
        total_min = max(0, int(round(total_time_sec / 60)))

        segments = []
        markers = []
        if coords:
            normalized = _normalize_points(coords)
            start_points = []
            for i in range(0, len(coords), 2):
                try:
                    start_points.append((normalized[i], normalized[i + 1]))
                except IndexError:
                    break

            for leg_index, leg in enumerate(legs):
                if leg_index >= len(start_points):
                    break
                (sx, sy), (ex, ey) = start_points[leg_index]
                segments.append({
                    "start": [sx, sy],
                    "end": [ex, ey],
                    "congestionColor": _congestion_color(int(crowd_score)) if crowd_score is not None else "#9ca3af",
                    "line": _line_for_leg(leg),
                    "label": ""
                })

        routes.append({
            "id": idx,
            "type": "mix",
            "line": stops[0]["line"] if stops else "",
            "pathDisplay": stops,
            "pathSummary": path_summary,
            "totalTime": total_min,
            "arrivalTime": arrival_time,
            "walkTime": walk_min,
            "transferCount": int(transfer_count),
            "crowdScore": None if crowd_score is None else float(crowd_score),
            "fare": fare,
            "segments": segments,
            "markers": markers,
            "mapSegments": map_segments,
            "mapMarkers": [],
            "mapPoints": map_points
        })

    return routes
