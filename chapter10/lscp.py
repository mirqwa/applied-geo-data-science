from pathlib import Path

import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import pulp
import spaghetti

from libpysal import weights
from spopt.locate.util import simulated_geo_points


def plot_data(data: list[dict]) -> None:
    _, ax = plt.subplots(figsize=(15, 15))
    for data_to_plot in data:
        data_to_plot_wm = data_to_plot["gdf"].to_crs(epsg=3857)
        data_to_plot_wm.plot(
            ax=ax,
            color=data_to_plot["color"],
            alpha=data_to_plot["alpha"],
            zorder=data_to_plot["zorder"],
            label=data_to_plot["label"],
            marker=data_to_plot.get("marker"),
            markersize=data_to_plot.get("markersize"),
        )
    cx.add_basemap(
        ax, crs=data_to_plot_wm.crs, zoom=12, source=cx.providers.OpenStreetMap.Mapnik
    )
    ax.set_axis_off()
    plt.legend(loc="upper right", bbox_to_anchor=(0, 1))
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
    streets_gpd.crs = "EPSG:5070"
    street_buffer = gpd.GeoDataFrame(
        gpd.GeoSeries(streets_gpd["geometry"].buffer(10).union_all()),
        crs=streets_gpd.crs,
        columns=["geometry"],
    )
    return street_buffer, streets_gpd, ntw


def simulate_patients_and_medical_centers(
    street_buffer: gpd.GeoDataFrame, ntw: spaghetti.Network
) -> tuple[gpd.GeoDataFrame]:
    patient_locs = simulated_geo_points(street_buffer, needed=150, seed=12345)
    ntw.snapobservations(patient_locs, "patients", attribute=True)
    patient_locs = spaghetti.element_as_gdf(ntw, pp_name="patients", snapped=True)
    patient_locs.crs = "EPSG:5070"
    medical_center_locs = simulated_geo_points(street_buffer, needed=4, seed=12345)
    ntw.snapobservations(medical_center_locs, "medical_centers", attribute=True)
    medical_center_locs = spaghetti.element_as_gdf(
        ntw, pp_name="medical_centers", snapped=True
    )
    medical_center_locs.crs = "EPSG:5070"
    return patient_locs, medical_center_locs


if __name__ == "__main__":
    solver = pulp.PULP_CBC_CMD(msg=False, warmStart=True)
    _, gdf_edges = get_network_data(True)
    plot_data(
        [
            {
                "gdf": gdf_edges,
                "color": "blue",
                "alpha": 0.5,
                "zorder": 1,
                "label": "Street Grid",
            }
        ]
    )
    gdf_edges_clipped_p = get_edges_subset(gdf_edges)
    plot_data(
        [
            {
                "gdf": gdf_edges_clipped_p,
                "color": "blue",
                "alpha": 0.5,
                "zorder": 1,
                "label": "Street Grid",
            }
        ]
    )
    street_buffer, streets_gpd, ntw = convert_gpd_to_spaghetti(gdf_edges_clipped_p)
    patient_locs, medical_center_locs = simulate_patients_and_medical_centers(
        street_buffer, ntw
    )
    plot_data(
        [
            {
                "gdf": streets_gpd,
                "color": "blue",
                "alpha": 0.5,
                "zorder": 1,
                "label": "Street Grid",
            },
            {
                "gdf": patient_locs,
                "color": "green",
                "alpha": 1,
                "zorder": 2,
                "marker": "o",
                "markersize": 20,
                "label": "Patients needing care $n=$150)",
            },
            {
                "gdf": medical_center_locs,
                "color": "red",
                "alpha": 1,
                "zorder": 3,
                "marker": "+",
                "markersize": 200,
                "label": "Medical Centers ($n=$4)",
            },
        ]
    )
