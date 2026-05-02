from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import networkx as nx

from app.services.geo import Coordinate, haversine_m
from app.services.geojson_loader import load_graph_from_geojson

MODES = ("노약자", "반려동물", "일반")
BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH_PATH = BASE_DIR / "data/geojson/nodes_with_score.geojson"
ROUTE_SPECS_PATH = BASE_DIR / "data/route_specs.json"
PET_GROUND_TEMP_LIMIT = 28.0


def build_dummy_graph() -> nx.Graph:
    graph = nx.Graph()
    nodes = {
        "suji_office": (37.3219, 127.0972),
        "library": (37.3232, 127.1010),
        "shade_walk": (37.3250, 127.1052),
        "direct_hot": (37.3262, 127.1090),
        "pet_safe": (37.3198, 127.1055),
        "windy_road": (37.3221, 127.1117),
        "jukjeon": (37.3247, 127.1245),
    }
    for node_id, (lat, lng) in nodes.items():
        graph.add_node(node_id, lat=lat, lng=lng)

    add_edge(graph, "suji_office", "direct_hot", heat_score=0.82, temperature=34.0, uv=0.88, shade_ratio=0.10, wind=0.20, ground_temp=35.5)
    add_edge(graph, "direct_hot", "jukjeon", heat_score=0.78, temperature=33.5, uv=0.84, shade_ratio=0.12, wind=0.22, ground_temp=34.0)

    add_edge(graph, "suji_office", "library", heat_score=0.32, temperature=29.5, uv=0.61, shade_ratio=0.55, wind=0.45, ground_temp=28.4, shelter_name="수지도서관", shelter_node="library")
    add_edge(graph, "library", "shade_walk", heat_score=0.25, temperature=28.8, uv=0.48, shade_ratio=0.72, wind=0.36, ground_temp=27.5, shelter_name="수지도서관", shelter_node="library")
    add_edge(graph, "shade_walk", "jukjeon", heat_score=0.38, temperature=30.0, uv=0.55, shade_ratio=0.64, wind=0.30, ground_temp=28.1)

    add_edge(graph, "suji_office", "pet_safe", heat_score=0.45, temperature=30.5, uv=0.58, shade_ratio=0.48, wind=0.42, ground_temp=26.9)
    add_edge(graph, "pet_safe", "windy_road", heat_score=0.36, temperature=30.2, uv=0.52, shade_ratio=0.40, wind=0.75, ground_temp=26.4)
    add_edge(graph, "windy_road", "jukjeon", heat_score=0.42, temperature=30.8, uv=0.56, shade_ratio=0.36, wind=0.80, ground_temp=26.8)

    return graph


def load_route_graph() -> tuple[nx.Graph, bool]:
    if DEFAULT_GRAPH_PATH.exists():
        return load_graph_from_geojson(DEFAULT_GRAPH_PATH), False
    return build_dummy_graph(), True


def add_edge(graph: nx.Graph, source: str, target: str, **attrs: float | str) -> None:
    source_coord = (graph.nodes[source]["lat"], graph.nodes[source]["lng"])
    target_coord = (graph.nodes[target]["lat"], graph.nodes[target]["lng"])
    graph.add_edge(source, target, distance_m=haversine_m(source_coord, target_coord), **attrs)


def edge_weight(mode: str, attrs: dict) -> float:
    heat = float(attrs["heat_score"])
    distance = float(attrs["distance_m"])
    shade = float(attrs["shade_ratio"])
    wind = float(attrs["wind"])
    ground_temp = float(attrs["ground_temp"])
    shelter_bonus = 0.25 if attrs.get("shelter_name") else 0.0

    if mode == "노약자":
        comfort_penalty = heat * 1.8 - shade * 0.35 - shelter_bonus
    elif mode == "반려동물":
        hot_ground_penalty = 2.5 if ground_temp > 28.0 else 0.0
        comfort_penalty = heat * 1.4 + hot_ground_penalty - shade * 0.15
    else:
        comfort_penalty = heat * 1.2 - shade * 0.20 - wind * 0.15

    return distance * max(0.1, 1 + comfort_penalty)


def graph_for_mode(graph: nx.Graph, mode: str) -> nx.Graph:
    if mode != "반려동물":
        return graph

    filtered = graph.copy()
    hot_edges = [
        (source, target)
        for source, target, attrs in filtered.edges(data=True)
        if float(attrs.get("ground_temp", 0)) > PET_GROUND_TEMP_LIMIT
    ]
    filtered.remove_edges_from(hot_edges)
    if filtered.number_of_edges() == 0:
        return graph
    return filtered


def nearest_node(graph: nx.Graph, coord: Coordinate) -> str:
    return min(
        graph.nodes,
        key=lambda node_id: haversine_m(
            coord,
            (graph.nodes[node_id]["lat"], graph.nodes[node_id]["lng"]),
        ),
    )


def shortest_path_for_mode(graph: nx.Graph, mode: str, source: str, target: str) -> list[str]:
    mode_graph = graph_for_mode(graph, mode)
    if mode == "노약자":
        return shortest_path_via_shelter(mode_graph, mode, source, target)

    try:
        return nx.shortest_path(
            mode_graph,
            source=source,
            target=target,
            weight=lambda _u, _v, attrs: edge_weight(mode, attrs),
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return nx.shortest_path(
            graph,
            source=source,
            target=target,
            weight=lambda _u, _v, attrs: edge_weight(mode, attrs),
        )


def shortest_path_via_shelter(graph: nx.Graph, mode: str, source: str, target: str) -> list[str]:
    shelter_nodes = sorted(
        {
            str(attrs["shelter_node"])
            for _source, _target, attrs in graph.edges(data=True)
            if attrs.get("shelter_node") in graph.nodes
        }
    )
    if not shelter_nodes or source in shelter_nodes or target in shelter_nodes:
        return nx.shortest_path(
            graph,
            source=source,
            target=target,
            weight=lambda _u, _v, attrs: edge_weight(mode, attrs),
        )

    best_path = None
    best_weight = None
    for shelter_node in shelter_nodes:
        try:
            first = nx.shortest_path(
                graph,
                source=source,
                target=shelter_node,
                weight=lambda _u, _v, attrs: edge_weight(mode, attrs),
            )
            second = nx.shortest_path(
                graph,
                source=shelter_node,
                target=target,
                weight=lambda _u, _v, attrs: edge_weight(mode, attrs),
            )
        except nx.NetworkXNoPath:
            continue

        candidate = first + second[1:]
        weight = path_weight(graph, mode, candidate)
        if best_weight is None or weight < best_weight:
            best_path = candidate
            best_weight = weight

    if best_path is not None:
        return best_path

    return nx.shortest_path(
        graph,
        source=source,
        target=target,
        weight=lambda _u, _v, attrs: edge_weight(mode, attrs),
    )


def path_weight(graph: nx.Graph, mode: str, path: list[str]) -> float:
    return sum(edge_weight(mode, graph.edges[source, target]) for source, target in pairwise(path))


def shortest_cool_route(mode: str, start: Coordinate, end: Coordinate) -> dict:
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    graph, is_dummy = load_route_graph()
    source = nearest_node(graph, start)
    target = nearest_node(graph, end)
    path = shortest_path_for_mode(graph, mode, source, target)
    edges = list(pairwise(path))
    edge_attrs = [graph.edges[u, v] for u, v in edges]
    distance_m = sum(float(attrs["distance_m"]) for attrs in edge_attrs)
    heat_score_avg = sum(float(attrs["heat_score"]) for attrs in edge_attrs) / len(edge_attrs)
    shelters = unique_shelters(edge_attrs, graph)

    return {
        "path": to_feature_collection(graph, edges, edge_attrs, mode),
        "heat_score_avg": round(heat_score_avg, 3),
        "distance_m": round(distance_m, 1),
        "shelters": shelters,
        "is_dummy": is_dummy,
    }


def get_recommended_routes(mode: str | None = None) -> list[dict]:
    routes = []
    for spec in load_route_specs():
        route_mode = spec["mode"]
        if mode is not None and route_mode != mode:
            continue
        start = tuple(spec["start"])
        end = tuple(spec["end"])
        result = shortest_cool_route(route_mode, start, end)
        routes.append(
            {
                "id": spec["id"],
                "name": spec["name"],
                "mode": route_mode,
                "heat_score_avg": result["heat_score_avg"],
                "distance_m": result["distance_m"],
                "geojson": result["path"],
                "shelters": result["shelters"],
                "is_dummy": result["is_dummy"],
            }
        )
    return routes


def load_route_specs(path: Path = ROUTE_SPECS_PATH) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        specs = json.load(file)

    if not isinstance(specs, list):
        raise ValueError("route_specs.json must be a JSON array")
    for spec in specs:
        missing = {"id", "mode", "name", "start", "end"} - set(spec)
        if missing:
            raise ValueError(f"route spec is missing required fields: {sorted(missing)}")
        if spec["mode"] not in MODES:
            raise ValueError(f"unsupported route mode in route_specs.json: {spec['mode']}")
    return specs


def pairwise(items: list[str]) -> Iterable[tuple[str, str]]:
    for index in range(len(items) - 1):
        yield items[index], items[index + 1]


def to_feature_collection(graph: nx.Graph, edges: list[tuple[str, str]], edge_attrs: list[dict], mode: str) -> dict:
    features = []
    for (source, target), attrs in zip(edges, edge_attrs):
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [graph.nodes[source]["lng"], graph.nodes[source]["lat"]],
                        [graph.nodes[target]["lng"], graph.nodes[target]["lat"]],
                    ],
                },
                "properties": {
                    "mode": mode,
                    "heat_score": attrs["heat_score"],
                    "distance_m": round(float(attrs["distance_m"]), 1),
                    "temperature": attrs["temperature"],
                    "uv": attrs.get("uv"),
                    "shade_ratio": attrs["shade_ratio"],
                    "wind": attrs["wind"],
                    "ground_temp": attrs["ground_temp"],
                    "shelter_name": attrs.get("shelter_name"),
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def unique_shelters(edge_attrs: list[dict], graph: nx.Graph) -> list[dict]:
    shelters = []
    seen = set()
    for attrs in edge_attrs:
        name = attrs.get("shelter_name")
        node_id = attrs.get("shelter_node")
        if not name or not node_id or name in seen:
            continue
        seen.add(name)
        shelters.append(
            {
                "name": name,
                "lat": graph.nodes[node_id]["lat"],
                "lng": graph.nodes[node_id]["lng"],
                "operating_hours": "09:00-18:00",
            }
        )
    return shelters
