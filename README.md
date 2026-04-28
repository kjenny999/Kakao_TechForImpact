# Kakao_TechForImpact

## Week 1 — Setup & Data Understanding

### Goal
개발 환경 구축 및 데이터 구조 파악

### Tasks
- **Data**
  - 데이터 형식 및 컬럼 확인
  - EDA (결측값 / 이상값)
  - 수지구 도로 네트워크 추출 (`OSMnx`)
- **Backend**
  - GitHub 레포 및 브랜치 전략 설정
  - FastAPI 프로젝트 초기화
  - SQLite 스키마 설계
  - `/healthcheck` API 구현
- **Frontend**
  - 카카오맵 SDK 설정 및 지도 렌더링
  - 와이어프레임 작성
  - `/healthcheck` API 연동

### Deliverables
- `sujiku_roads.geojson`
- FastAPI 서버 실행
- 기본 지도 화면

---

## Week 2 — Heat Score & Routing

### Goal
Heat Score 계산 및 경로 탐색 기능 구현

### Tasks
- **Data**
  - 기후 데이터 → 도로 노드 매핑
  - Heat Score 계산 로직 구현
  - 프리셋(노약자/반려동물/일반) 정의
- **Backend**
  - GeoJSON → 그래프 변환
  - Dijkstra 기반 경로 탐색 구현
  - `POST /route` API 개발
- **Frontend**
  - 경로 API 연동
  - 지도 Polyline 렌더링
  - 모드 선택 UI 및 색상 표현

### Deliverables
- `nodes_with_score.geojson`
- `/route` API
- 경로 시각화 UI

---

## Week 3 — Predefined Routes & UI

### Goal
추천 경로 13개 생성 및 UI 완성

### Tasks
- **Data**
  - 경로 13개 좌표 정의
  - 쉼터 데이터 수집
  - 경로 GeoJSON 생성
- **Backend**
  - 경로 DB 저장
  - `GET /routes` API 구현
- **Frontend**
  - 경로 목록 UI
  - 지도 하이라이트 및 툴팁
  - 쉼터 마커 표시

### Deliverables
- `routes/*.geojson`
- `shelters.json`
- `/routes` API
- 완성된 UI

---

## Summary

- **Week 1:** 환경 구축 및 데이터 파악  
- **Week 2:** Heat Score 기반 경로 탐색 구현  
- **Week 3:** 추천 경로 및 UI 완성  
