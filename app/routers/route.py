from typing import Literal

import networkx as nx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.routing import MODES, get_recommended_routes, shortest_cool_route


router = APIRouter(tags=["routes"])
Mode = Literal["노약자", "반려동물", "일반"]


class RouteRequest(BaseModel):
    mode: Mode = Field(..., description="노약자 | 반려동물 | 일반")
    start: tuple[float, float] = Field(..., description="[lat, lng]")
    end: tuple[float, float] = Field(..., description="[lat, lng]")


@router.post("/route")
def create_route(request: RouteRequest) -> dict:
    try:
        return shortest_cool_route(
            mode=request.mode,
            start=request.start,
            end=request.end,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except nx.NetworkXNoPath as exc:
        raise HTTPException(status_code=404, detail="No route found for the requested coordinates") from exc
    except nx.NodeNotFound as exc:
        raise HTTPException(status_code=404, detail="Nearest graph node was not found") from exc


@router.get("/routes")
def list_routes(mode: Mode | None = Query(default=None)) -> list[dict]:
    if mode is not None and mode not in MODES:
        return []
    return get_recommended_routes(mode=mode)
