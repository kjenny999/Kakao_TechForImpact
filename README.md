# Kakao_TechForImpact

📅 Week 1 — 환경 세팅 및 데이터 파악
목표
개발 환경 구축
데이터 구조 이해
기본 동작 확인
작업
Data (A)
기후 데이터 형식 및 컬럼 확인
결측값 / 이상값 탐색 (EDA)
OSMnx로 수지구 도로 네트워크 추출
QGIS로 레이어 정합성 확인
Backend (B)
GitHub 레포 및 브랜치 전략 설정
FastAPI 프로젝트 초기화
SQLite 스키마 설계
/healthcheck API 구현
Frontend (C)
카카오맵 SDK 설정 및 지도 렌더링
와이어프레임 작성
/healthcheck API 연동 테스트
완료 기준
데이터 구조 공유 완료
FastAPI 서버 실행 가능
지도 렌더링 확인
📅 Week 2 — Heat Score 및 경로 탐색
목표
Heat Score 계산
경로 탐색 로직 구현
API → 지도 연결
작업
Data (A)
기후 데이터 → 도로 노드 공간 조인
Heat Score 계산 구현
프리셋 가중치 정의
노드별 Score GeoJSON 생성
Backend (B)
GeoJSON → NetworkX 그래프 변환
Dijkstra + Score 기반 경로 탐색
POST /route API 구현
Frontend (C)
/route API 연동
경로 Polyline 렌더링
Heat Score 기반 색상 표현
모드 선택 UI 및 로딩 처리
완료 기준
경로 요청 → 지도 표시까지 전체 흐름 동작
모드별 경로 정상 반환
📅 Week 3 — 추천 경로 및 UI 완성
목표
추천 경로 13개 생성
사용자 UI 완성
작업
Data (A)
반려동물/노약자 조건 반영 로직 구현
쉼터 데이터 수집
경로 13개 좌표 확정 및 GeoJSON 생성
구간별 상세 데이터 생성
Backend (B)
경로 13개 생성 및 DB 저장
GET /routes API 구현
Frontend (C)
경로 목록 UI 구현
지도 강조 및 인터랙션 처리
툴팁 및 쉼터 마커 표시
완료 기준
13개 경로 모두 조회 및 시각화 가능
툴팁 및 쉼터 기능 정상 동작
Summary
Week 1: 환경 구축 및 데이터 이해
Week 2: 핵심 로직 구현 (Heat Score, Routing)
Week 3: 결과물 생성 및 UI 완성
