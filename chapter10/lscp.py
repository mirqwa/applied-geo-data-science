from pathlib import Path
import geopandas as gpd
import osmnx as ox
import pulp


def get_network_data(use_local_data: bool = False) -> tuple[gpd.GeoDataFrame]:
    nodes_path = "data/washington/network_nodes.geojson"
    edges_path = "data/washington/network_edges.geojson"
    if use_local_data and Path(nodes_path).is_file() and Path(edges_path).is_file():
        return gpd.read_file(nodes_path), gpd.read_file(edges_path)
    G = ox.graph_from_place("Washington, DC", network_type="drive")
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
    gdf_nodes.to_file(nodes_path, driver="GeoJSON")
    gdf_edges.to_file(edges_path, driver="GeoJSON")
    return gdf_nodes, gdf_edges


if __name__ == "__main__":
    patients = 150
    medical_centers = 4
    service_area = 5500

    patient_seed = 54321
    medical_centers_seed = 54321

    solver = pulp.PULP_CBC_CMD(msg=False, warmStart=True)
    gdf_nodes, gdf_edges = get_network_data()
