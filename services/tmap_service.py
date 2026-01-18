import httpx

from core.config import settings


def _base_headers() -> dict:
    if not settings.tmap_app_key:
        raise RuntimeError("TMAP_APP_KEY is not set")
    return {
        "Accept": "application/json",
        "appKey": settings.tmap_app_key
    }


async def fetch_routes(payload: dict) -> dict:
    headers = _base_headers()
    headers["Content-Type"] = "application/json"

    url = f"{settings.tmap_base_url}/transit/routes"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        raise RuntimeError(f"TMAP API error {resp.status_code}: {resp.text}")

    return resp.json()


async def search_poi(payload: dict) -> dict:
    headers = _base_headers()

    search_keyword = payload.get("searchKeyword")
    if not search_keyword:
        raise RuntimeError("searchKeyword is required")

    params = {
        "version": "1",
        "format": "json",
        "searchKeyword": search_keyword,
        "count": payload.get("count", 5),
        "page": payload.get("page", 1)
    }

    if payload.get("searchType"):
        params["searchType"] = payload["searchType"]
    if payload.get("radius"):
        params["radius"] = payload["radius"]
    if payload.get("centerLon") and payload.get("centerLat"):
        params["centerLon"] = payload["centerLon"]
        params["centerLat"] = payload["centerLat"]

    url = f"{settings.tmap_base_url}/tmap/pois"

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params, headers=headers)

    if resp.status_code != 200:
        raise RuntimeError(f"TMAP POI error {resp.status_code}: {resp.text}")

    return resp.json()
