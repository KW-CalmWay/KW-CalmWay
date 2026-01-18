import pandas as pd
import numpy as np

bus_info_df = pd.read_excel('static/data/bus_data/서울시버스정류소위치정보(20260108).xlsx')

_bus_name_groups = dict(tuple(bus_info_df.groupby('정류소명', sort=False)))

def _normalize_stop_name(name: str) -> str:
    if not name:
        return ""
    return str(name).strip()

def get_busStationID(api_response):
    bus_stops = []

    for itinerary in api_response["metaData"]["plan"]["itineraries"]:
        for leg in itinerary["legs"]:
            if leg.get("mode") == "BUS":
                stations = (
                    leg.get("passStopList", {}).get("stations")
                    or leg.get("passStopList", {}).get("stationList")
                    or []
                )
                for s in stations:
                    try:
                        bus_stops.append({
                            "stationName": _normalize_stop_name(s.get("stationName")),
                            "lat": float(s["lat"]),
                            "lon": float(s["lon"])
                        })
                    except Exception:
                        continue


    print(f"[BUS] collected bus_stops count = {len(bus_stops)}")

    res = {}

    for i, stop in enumerate(bus_stops, start=1):
        name = stop['stationName']
        if not name:
            print(f"[{i:02d}/37] [SKIP] empty stationName", flush=True)
            continue

        x = stop['lon']
        y = stop['lat']

        filtered = _bus_name_groups.get(name)

        if filtered is None:
            tmp = bus_info_df[bus_info_df['정류소명'].str.contains(name, na=False, regex=False)]
            if tmp.empty:
                print(f"[{i:02d}/37] [MISS] no match for stop='{name}'", flush=True)
                continue
            print(f"[{i:02d}/37] [FALLBACK] '{name}', candidates={len(tmp)}", flush=True)
            filtered = tmp
        else:
            print(f"[{i:02d}/37] [EXACT] '{name}', candidates={len(filtered)}", flush=True)
            filtered = filtered.copy()

        filtered.loc[:, '오차'] = np.sqrt((filtered['X좌표'] - x)**2 + (filtered['Y좌표'] - y)**2)
        if filtered['오차'].isna().all():
            print(f"[{i:02d}/37] [MISS] distance calc failed for '{name}'", flush=True)
            continue

        best_match = filtered.loc[filtered['오차'].idxmin(), 'ARS_ID']
        if pd.isna(best_match):
            print(f"[{i:02d}/37] [MISS] ARS_ID NaN for '{name}'", flush=True)
            continue

        res[name] = int(best_match)

    print(f"[{i:02d}/37] [OK] '{name}' -> {int(best_match)}", flush=True)

    print("====== BUS ARS RESULT ======")
    print(f"total matched = {len(res)}")
    for k, v in list(res.items())[:10]:
        print(f"  {k} -> {v}")
    print("============================")

    return res