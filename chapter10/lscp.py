from pathlib import Path

import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import pulp
import spaghetti

from libpysal import weights
from spopt.locate.util import simulated_geo_points


def plot_street(gdf_edges: gpd.GeoDataFrame) -> None:
    _, ax = plt.subplots(figsize=(15, 15))
    gdf_edges_wm = gdf_edges.to_crs(epsg=3857)
    gdf_edges_wm.plot(ax=ax, alpha=0.5, color="red", edgecolor="k")
    cx.add_basemap(ax, crs=gdf_edges_wm.crs, zoom=12)
    ax.set_axis_off()
    plt.show()


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


def get_edges_subset(gdf_edges: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf_edges.reset_index(inplace=True)
    DC_BGs = gpd.read_file("data/tiger/TIGER2019/tl_2019_11_tract.zip")
    knn = weights.KNN.from_dataframe(DC_BGs, k=10)
    neighboring_tracts = [150] + list(knn[150].keys())
    DC_BGs_Sel = DC_BGs.iloc[neighboring_tracts]
    DC_BGs_Sel_D = DC_BGs_Sel.dissolve()
    DC_BGs_Sel_D = DC_BGs_Sel_D.to_crs("EPSG:4326")
    mask = gdf_edges.within(DC_BGs_Sel_D.loc[0, "geometry"])
    gdf_edges_clipped = gdf_edges.loc[mask]
    gdf_edges_clipped = gdf_edges_clipped[["osmid", "geometry"]]
    gdf_edges_clipped_p = gdf_edges_clipped.to_crs(5070)
    return gdf_edges_clipped_p


def convert_gpd_to_spaghetti(gdf_edges: gpd.GeoDataFrame) -> tuple:
    ntw = spaghetti.Network(in_data=gdf_edges)
    streets_gpd = spaghetti.element_as_gdf(ntw, arcs=True)
    street_buffer = gpd.GeoDataFrame(
        gpd.GeoSeries(streets_gpd["geometry"].buffer(10).unary_union),
        crs=streets_gpd.crs,
        columns=["geometry"],
    )
    return street_buffer, streets_gpd


def simulate_patients_and_medical_centers(street_buffer: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame]:
    patient_locs = simulated_geo_points(street_buffer, needed=150, seed=32)
    medical_center_locs = simulated_geo_points(street_buffer, needed=4, seed=32)
    return patient_locs, medical_center_locs


if __name__ == "__main__":
    solver = pulp.PULP_CBC_CMD(msg=False, warmStart=True)
    _, gdf_edges = get_network_data(True)
    plot_street(gdf_edges)
    gdf_edges_clipped_p = get_edges_subset(gdf_edges)
    plot_street(gdf_edges_clipped_p)
    street_buffer, streets_gpd = convert_gpd_to_spaghetti(gdf_edges_clipped_p)
    patient_locs, medical_center_locs = simulate_patients_and_medical_centers(
        street_buffer
    )
