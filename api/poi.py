from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.tmap_service import search_poi
from parsers.poi_parser import parse_poi_items

router = APIRouter()


class PoiSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    count: Optional[int] = 5
    page: Optional[int] = 1
    radius: Optional[int] = None
    centerLon: Optional[str] = None
    centerLat: Optional[str] = None


@router.post("/api/poi/search")
async def search_poi_endpoint(req: PoiSearchRequest):
    try:
        raw = await search_poi({
            "searchKeyword": req.query,
            "count": req.count,
            "page": req.page,
            "radius": req.radius,
            "centerLon": req.centerLon,
            "centerLat": req.centerLat
        })
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"items": parse_poi_items(raw)}
