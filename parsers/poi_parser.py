from __future__ import annotations


def _safe_float(value: str | float | None):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_poi_items(raw: dict) -> list[dict]:
    search_info = raw.get("searchPoiInfo", {})
    pois = search_info.get("pois", {})
    poi_list = pois.get("poi", []) or []

    items = []
    for poi in poi_list:
        name = poi.get("name") or ""
        lat = _safe_float(poi.get("frontLat") or poi.get("noorLat") or poi.get("lat"))
        lon = _safe_float(poi.get("frontLon") or poi.get("noorLon") or poi.get("lon"))
        if lat is None or lon is None:
            continue

        addr = ""
        new_addr_list = poi.get("newAddressList", {})
        new_addr = new_addr_list.get("newAddress") or []
        if isinstance(new_addr, list) and new_addr:
            addr = new_addr[0].get("fullAddressRoad", "")
        if not addr:
            addr = poi.get("upperAddrName", "") + " " + poi.get("middleAddrName", "")
            addr = addr.strip()

        items.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "address": addr
        })

    return items
