import geopandas as gpd
import numpy as np
import json
from heat_score import heat_score
import folium
from shapely.geometry import Point

# 1. 노드 불러오기
nodes = gpd.read_file("sujiku_nodes.geojson")

# 2. 더미 데이터
nodes["utci"] = np.random.uniform(25, 40, len(nodes))
nodes["heat"] = np.random.uniform(20, 50, len(nodes))
nodes["shade"] = np.random.uniform(0, 1, len(nodes))
nodes["wind"] = np.random.uniform(0, 5, len(nodes))

# 3. 가중치
with open("data/presets.json") as f:
    presets = json.load(f)

w = presets["normal"]

# 4. score 계산
nodes["score"] = nodes.apply(
    lambda row: heat_score(
        row["utci"],
        row["heat"],
        row["shade"],
        row["wind"],
        w
    ),
    axis=1
)

# 5. 저장
nodes.to_file("nodes_with_score.geojson", driver="GeoJSON")

# --------------------------------
# ⚠️ 여기부터 sjoin 테스트
# --------------------------------

climate_points = gpd.GeoDataFrame({
    "utci": [30, 35, 32],
    "geometry": [
        Point(127.09, 37.32),
        Point(127.1, 37.33),
        Point(127.08, 37.31)
    ]
}, crs="EPSG:4326")

# 👉 좌표계 맞추기 (중요)
nodes_proj = nodes.to_crs(epsg=5179)
climate_proj = climate_points.to_crs(epsg=5179)

joined = gpd.sjoin_nearest(nodes_proj, climate_proj)

print(joined.head())

# --------------------------------
# 지도 시각화
# --------------------------------

m = folium.Map(location=[37.32, 127.09], zoom_start=13)

for _, row in nodes.sample(200).iterrows():
    color = "blue" if row["score"] < 30 else "red"

    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=2,
        color=color
    ).add_to(m)

m.save("score_map.html")