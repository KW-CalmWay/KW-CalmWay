from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.tmap_service import fetch_routes
from parsers.tmap_parser import parse_routes

router = APIRouter()

class RouteRequest(BaseModel):
    startX: str = Field(..., description="Start longitude")
    startY: str = Field(..., description="Start latitude")
    endX: str = Field(..., description="End longitude")
    endY: str = Field(..., description="End latitude")
    lang: Optional[int] = 0
    format: Optional[str] = "json"
    count: Optional[int] = 10
    searchDttm: Optional[str] = None

@router.post("/api/routes")
async def get_routes(req: RouteRequest):
    try:
        payload = req.model_dump(exclude_none=True)
        raw = await fetch_routes(payload)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    routes = parse_routes(raw, req.searchDttm)
    return {"routes": routes}
