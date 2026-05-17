import osmnx as ox
import geopandas as gpd

# 1. 지역 이름 설정
place_name = "Suji-gu, Yongin-si, South Korea"

# 2. 도로 네트워크 가져오기
G = ox.graph_from_place(place_name, network_type="drive")

# 3. 노드/엣지로 변환
nodes, edges = ox.graph_to_gdfs(G)

# 4. 저장
nodes.to_file("sujiku_nodes.geojson", driver="GeoJSON")
edges.to_file("sujiku_edges.geojson", driver="GeoJSON")

print("완료!")


nodes = gpd.read_file("sujiku_nodes.geojson")
print(nodes.head())

# 확인용 위경도 값
# print(nodes.crs)

# 확인용 지도 출력
# import folium
#
# # 중심 좌표 (수지구청 근처)
# m = folium.Map(location=[37.32, 127.09], zoom_start=13)
#
# for _, row in nodes.head(100).iterrows():
#     folium.CircleMarker(
#         location=[row.geometry.y, row.geometry.x],
#         radius=2
#     ).add_to(m)
#
# m.save("map.html")