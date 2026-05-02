# Data Contract

이 문서는 A가 B에게 넘길 파일 형식을 고정합니다. DB 없이도 백엔드에서 바로 `NetworkX` 그래프로 읽을 수 있는 최소 계약입니다.

## Files

- `data/geojson/nodes_with_score.geojson`
- `data/shelters.json`

샘플 파일:

- `data/sample/nodes_with_score.geojson`
- `data/sample/shelters.json`

## nodes_with_score.geojson

GeoJSON `FeatureCollection`이어야 합니다. 각 feature는 도로 구간 하나를 나타내는 `LineString`입니다.

좌표 순서:

```text
[lng, lat]
```

필수 properties:

```json
{
  "source": "suji_office",
  "target": "library",
  "heat_score": 0.32,
  "temperature": 29.5,
  "uv": 0.61,
  "shade_ratio": 0.55,
  "wind": 0.45,
  "ground_temp": 28.4
}
```

선택 properties:

```json
{
  "distance_m": 365.8,
  "shelter_name": "수지도서관",
  "shelter_node": "library"
}
```

주의:

- `source`, `target`은 도로 구간 양 끝 노드 ID입니다.
- `distance_m`이 없으면 백엔드가 LineString 시작점과 끝점 기준으로 계산합니다.
- `heat_score`는 낮을수록 시원한 값으로 해석합니다.
- `shade_ratio`, `wind`, `uv`는 0부터 1 사이 정규화 값을 권장합니다.
- `temperature`, `ground_temp`는 섭씨 기준 숫자입니다.

## shelters.json

무더위 쉼터 배열입니다.

필수 필드:

```json
[
  {
    "name": "수지도서관",
    "lat": 37.3232,
    "lng": 127.101
  }
]
```

선택 필드:

```json
{
  "operating_hours": "09:00-18:00",
  "address": "경기도 용인시 수지구"
}
```

## Backend Loader

백엔드 로더 위치:

```text
app/services/geojson_loader.py
```

사용 예:

```python
from app.services.geojson_loader import load_graph_from_geojson, load_shelters

graph = load_graph_from_geojson("data/geojson/nodes_with_score.geojson")
shelters = load_shelters("data/shelters.json")
```

현재 `/route`는 `data/geojson/nodes_with_score.geojson` 파일이 있으면 이 파일을 먼저 사용합니다. 파일이 없으면 더미 그래프로 동작하고, 응답에 `is_dummy: true`가 표시됩니다.

## Validation

샘플 파일 검증:

```bash
python3 scripts/validate_inputs.py
```

실제 A 전달 파일 검증:

```bash
python3 scripts/validate_inputs.py \
  --nodes data/geojson/nodes_with_score.geojson \
  --shelters data/shelters.json \
  --routes data/route_specs.json
```
