from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx

from app.services.geo import haversine_m


REQUIRED_EDGE_PROPERTIES = {
    "source",
    "target",
    "heat_score",
    "temperature",
    "uv",
    "shade_ratio",
    "wind",
    "ground_temp",
}


def load_graph_from_geojson(path: str | Path) -> nx.Graph:
    data = load_json(path)
    validate_feature_collection(data, path)

    graph = nx.Graph()
    for feature in data["features"]:
        geometry = feature.get("geometry") or {}
        properties = feature.get("properties") or {}
        validate_edge_feature(geometry, properties)

        source = str(properties["source"])
        target = str(properties["target"])
        coordinates = geometry["coordinates"]
        start_lng, start_lat = coordinates[0]
        end_lng, end_lat = coordinates[-1]

        graph.add_node(source, lat=float(start_lat), lng=float(start_lng))
        graph.add_node(target, lat=float(end_lat), lng=float(end_lng))
        graph.add_edge(
            source,
            target,
            distance_m=float(properties.get("distance_m") or haversine_m((start_lat, start_lng), (end_lat, end_lng))),
            heat_score=float(properties["heat_score"]),
            temperature=float(properties["temperature"]),
            uv=float(properties["uv"]),
            shade_ratio=float(properties["shade_ratio"]),
            wind=float(properties["wind"]),
            ground_temp=float(properties["ground_temp"]),
            shelter_name=properties.get("shelter_name"),
            shelter_node=properties.get("shelter_node"),
        )

    return graph


def load_shelters(path: str | Path) -> list[dict[str, Any]]:
    shelters = load_json(path)
    if not isinstance(shelters, list):
        raise ValueError("shelters.json must be a JSON array")

    required = {"name", "lat", "lng"}
    for shelter in shelters:
        missing = required - set(shelter)
        if missing:
            raise ValueError(f"shelter is missing required fields: {sorted(missing)}")
        shelter["lat"] = float(shelter["lat"])
        shelter["lng"] = float(shelter["lng"])
    return shelters


def load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def validate_feature_collection(data: Any, path: str | Path) -> None:
    if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
        raise ValueError(f"{path} must be a GeoJSON FeatureCollection")
    if not isinstance(data.get("features"), list):
        raise ValueError(f"{path} must include a features array")


def validate_edge_feature(geometry: dict, properties: dict) -> None:
    if geometry.get("type") != "LineString":
        raise ValueError("each route segment must be a LineString feature")
    if len(geometry.get("coordinates", [])) < 2:
        raise ValueError("each LineString feature must include at least two coordinates")

    missing = REQUIRED_EDGE_PROPERTIES - set(properties)
    if missing:
        raise ValueError(f"route segment is missing required properties: {sorted(missing)}")
