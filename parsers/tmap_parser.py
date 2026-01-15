from __future__ import annotations

from datetime import datetime, timedelta
import re

MODE_TO_TYPE = {
    "WALK": "walk",
    "BUS": "bus",
    "SUBWAY": "subway",
    "EXPRESS BUS": "bus",
    "TRAIN": "train",
    "AIRPLANE": "air",
    "FERRY": "ferry"
}

LINE_FALLBACK = {
    "walk": "walk"
}

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

    normalized = []
    for lon, lat in points:
        x = scale(lon, min_lon, max_lon)
        y = scale(lat, min_lat, max_lat)
        normalized.append((x, y))

    return normalized

def parse_routes(raw: dict, search_dttm: str | None = None) -> list[dict]:
    itineraries = raw.get("metaData", {}).get("plan", {}).get("itineraries", [])
    routes: list[dict] = []
    start_dt = _parse_search_time(search_dttm)
    placeholder_names = {"출발지", "도착지"}

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
        crowd_score = None
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
                    "congestionColor": _congestion_color(crowd_score) if crowd_score is not None else "#9ca3af",
                    "line": line,
                    "type": _mode_type(mode)
                })

        path_summary = " - ".join([s["name"] for s in stops]) or "Route"
        arrival_time = _format_arrival(start_dt, total_time_sec)

        walk_min = max(0, int(round(total_walk_time_sec / 60)))
        total_min = max(0, int(round(total_time_sec / 60)))

        segments = []
        markers = []
        map_markers = []
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
                    "congestionColor": _congestion_color(crowd_score) if crowd_score is not None else "#9ca3af",
                    "line": _line_for_leg(leg),
                    "label": ""
                })

            if start_points:
                (sx, sy), _ = start_points[0]
                markers.append({"x": sx, "y": sy, "type": "start", "label": stops[0]["name"] if stops else "Start"})

                for mid_idx in range(1, len(start_points) - 1):
                    _, (mx, my) = start_points[mid_idx]
                    label = stops[mid_idx]["name"] if mid_idx < len(stops) else "Transfer"
                    markers.append({"x": mx, "y": my, "type": "transfer", "label": label})

                _, (ex, ey) = start_points[-1]
                end_label = stops[-1]["name"] if stops else "End"
                markers.append({"x": ex, "y": ey, "type": "end", "label": end_label})

        if legs:
            first_start = legs[0].get("start", {})
            if "lon" in first_start and "lat" in first_start:
                map_markers.append({
                    "type": "start",
                    "label": "출발",
                    "lat": float(first_start["lat"]),
                    "lon": float(first_start["lon"])
                })

            for leg in transit_legs[1:]:
                transfer = leg.get("start", {})
                if "lon" in transfer and "lat" in transfer:
                    transfer_name, _ = resolve_leg_names(leg)
                    map_markers.append({
                        "type": "transfer",
                        "label": transfer_name or "환승",
                        "line": _line_for_leg(leg),
                        "lineType": _mode_type(leg.get("mode", "")),
                        "lat": float(transfer["lat"]),
                        "lon": float(transfer["lon"])
                    })

            last_end = legs[-1].get("end", {})
            if "lon" in last_end and "lat" in last_end:
                map_markers.append({
                    "type": "end",
                    "label": "도착",
                    "lat": float(last_end["lat"]),
                    "lon": float(last_end["lon"])
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
            "crowdScore": crowd_score,
            "fare": fare,
            "segments": segments,
            "markers": markers,
            "mapSegments": map_segments,
            "mapMarkers": map_markers,
            "mapPoints": map_points
        })

    return routes
