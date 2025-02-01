from pathlib import Path

import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import pulp


def plot_nodes_and_edges(
    gdf_nodes: gpd.GeoDataFrame, gdf_edges: gpd.GeoDataFrame
) -> None:
    _, ax = plt.subplots(figsize=(15, 15))
    gdf_nodes_wm = gdf_nodes.to_crs(epsg=3857)
    gdf_nodes_wm.plot(ax=ax, alpha=0.5, edgecolor="k")
    gdf_edges_wm = gdf_edges.to_crs(epsg=3857)
    gdf_edges_wm.plot(ax=ax, alpha=0.5, color="red", edgecolor="k")
    cx.add_basemap(ax, crs=gdf_nodes_wm.crs, zoom=12)
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
    DC_BGs = gpd.read_file(
        "data/tiger/TIGER2019/tl_2019_11_tract.zip", compression="zip"
    )
    DC_BGs_Sel = DC_BGs[
        DC_BGs["TRACTCE"].isin(
            [
                "980000",
                "010202",
                "005900",
                "000102",
                "000202",
                "010800",
                "005801",
                "005802",
                "010500",
                "005602",
                "006600",
                "008200",
            ]
        )
    ]
    DC_BGs_Sel_D = DC_BGs_Sel.dissolve()
    DC_BGs_Sel_D = DC_BGs_Sel_D.to_crs("EPSG:4326")
    mask = gdf_edges.within(DC_BGs_Sel_D.loc[0, "geometry"])
    gdf_edges_clipped = gdf_edges.loc[mask]
    gdf_edges_clipped = gdf_edges_clipped[["osmid", "geometry"]]
    gdf_edges_clipped_p = gdf_edges_clipped.to_crs(5070)
    return gdf_edges_clipped_p


if __name__ == "__main__":
    patients = 150
    medical_centers = 4
    service_area = 5500

    patient_seed = 54321
    medical_centers_seed = 54321

    solver = pulp.PULP_CBC_CMD(msg=False, warmStart=True)
    gdf_nodes, gdf_edges = get_network_data(True)
    plot_nodes_and_edges(gdf_nodes, gdf_edges)
    gdf_edges_clipped_p = get_edges_subset(gdf_edges)
    plot_nodes_and_edges(gdf_nodes, gdf_edges_clipped_p)
