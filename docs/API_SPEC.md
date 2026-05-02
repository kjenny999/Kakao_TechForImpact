# API Spec

공유 기준 파일은 `docs/api-spec.json`입니다. 프론트와 백엔드는 이 JSON 필드명을 기준으로 맞춥니다.

## Local Server

```bash
python3 run_server.py
```

Base URL: `http://127.0.0.1:8000`

## Fixed Contract

- `mode`: `"노약자" | "반려동물" | "일반"`
- Request 좌표: `[lat, lng]`
- GeoJSON 좌표: `[lng, lat]`
- 응답의 `is_dummy: true`: 실데이터 전 더미 응답

## Endpoints

- `GET /healthcheck`
- `POST /route`
- `GET /routes`
- `GET /routes?mode=노약자`
- 데이터 계약: `docs/DATA_CONTRACT.md`
- 라우팅 정책: `docs/ROUTING_POLICY.md`
- 추천 경로 정의: `data/route_specs.json`

## Frontend Example

```js
const API_BASE_URL = "http://127.0.0.1:8000";

const health = await fetch(`${API_BASE_URL}/healthcheck`).then((res) => res.json());

const route = await fetch(`${API_BASE_URL}/route`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    mode: "일반",
    start: [37.3219, 127.0972],
    end: [37.3247, 127.1245]
  })
}).then((res) => res.json());

const params = new URLSearchParams({ mode: "노약자" });
const routes = await fetch(`${API_BASE_URL}/routes?${params}`).then((res) => res.json());
```
