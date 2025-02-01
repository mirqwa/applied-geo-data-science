from pathlib import Path

import contextily as cx
import geopandas as gpd
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import osmnx as ox
import pulp
import spaghetti

from libpysal import weights
from matplotlib.patches import Patch
from spopt.locate.coverage import LSCP
from spopt.locate.util import simulated_geo_points


TRACTS = 3
MEDICAL_CENTERS = 2
PATIENTS = 20
SERVICE_AREA = 3000


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


def get_serviced_points_and_selected_sites(lscp_from_cost_matrix) -> tuple[list]:
    serviced_points = []
    selected_sites = []
    for i in range(MEDICAL_CENTERS):
        if lscp_from_cost_matrix.fac2cli[i]:
            geom = patient_locs.iloc[lscp_from_cost_matrix.fac2cli[i]]["geometry"]
            serviced_points.append(geom)
            selected_sites.append(i)
    return serviced_points, selected_sites


def plot_serving_locations(
    ax, medical_center_locs, serviced_points, legend_elements, colors_ops
):
    for i in range(len(serviced_points)):
        gdf = gpd.GeoDataFrame(serviced_points[i])

        l = f"y{selected_sites[i]}"

        label = f"coverage_points by y{selected_sites[i]}"
        legend_elements.append(
            Patch(facecolor=colors_ops[l], edgecolor="k", label=label)
        )

        gdf.plot(
            ax=ax, zorder=3, alpha=0.7, edgecolor="k", color=colors_ops[l], label=label
        )
        medical_center_locs.iloc[[selected_sites[i]]].plot(
            ax=ax,
            marker="P",
            markersize=150 * 4.0,
            alpha=0.7,
            zorder=4,
            edgecolor="k",
            facecolor=colors_ops[l],
        )

        legend_elements.append(
            mlines.Line2D(
                [],
                [],
                color=colors_ops[l],
                marker="P",
                ms=20 / 2,
                markeredgecolor="k",
                linewidth=0,
                alpha=0.8,
                label=f"y{selected_sites[i]} medical center selected",
            )
        )


def plot_unselected_locations(ax, medical_center_locs, selected_sites, legend_elements):
    mc_not_selected = medical_center_locs.drop(selected_sites)
    mc_not_selected.plot(ax=ax, color="darkgrey", marker="P", markersize=80, zorder=3)
    legend_elements.append(
        mlines.Line2D(
            [],
            [],
            color="brown",
            marker="P",
            linewidth=0,
            label=f"Medical Centers Not Selected ($n$={len(mc_not_selected)})",
        )
    )


def plot_optimal_solution(
    serviced_points: list,
    selected_sites: list,
    streets_gpd: gpd.GeoDataFrame,
) -> None:
    colors_arr = [
        "darkslateblue",
        "forestgreen",
        "firebrick",
        "peachpuff",
        "saddlebrown",
        "cornflowerblue",
    ]
    colors_ops = {f"y{i}": colors_arr[i] for i in range(len(colors_arr))}
    _, ax = plt.subplots(figsize=(6, 6))
    legend_elements = []

    # Plot the street network
    streets_gpd.plot(ax=ax, alpha=1, color="lightblue", zorder=1)
    legend_elements.append(
        mlines.Line2D(
            [],
            [],
            color="lightblue",
            label="streets",
        )
    )
    plot_serving_locations(
        ax, medical_center_locs, serviced_points, legend_elements, colors_ops
    )
    # Plot locations of unselected medical centers
    plot_unselected_locations(ax, medical_center_locs, selected_sites, legend_elements)

    plt.title("LSCP - Cost Matrix Solution", fontweight="bold")
    plt.legend(
        handles=legend_elements,
        loc="upper right",
        bbox_to_anchor=(0, 1),
        borderaxespad=2.5,
    )
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
    knn = weights.KNN.from_dataframe(DC_BGs, k=TRACTS)
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
    patient_locs = simulated_geo_points(street_buffer, needed=PATIENTS, seed=12345)
    ntw.snapobservations(patient_locs, "patients", attribute=True)
    patient_locs = spaghetti.element_as_gdf(ntw, pp_name="patients", snapped=True)
    patient_locs.crs = "EPSG:5070"
    medical_center_locs = simulated_geo_points(
        street_buffer, needed=MEDICAL_CENTERS, seed=12345
    )
    ntw.snapobservations(medical_center_locs, "medical_centers", attribute=True)
    medical_center_locs = spaghetti.element_as_gdf(
        ntw, pp_name="medical_centers", snapped=True
    )
    medical_center_locs.crs = "EPSG:5070"
    return patient_locs, medical_center_locs


def get_the_serving_locations_for_patients(ntw: spaghetti.Network):
    cost_matrix = ntw.allneighbordistances(
        sourcepattern=ntw.pointpatterns["patients"],
        destpattern=ntw.pointpatterns["medical_centers"],
    )
    lscp_from_cost_matrix = LSCP.from_cost_matrix(cost_matrix, SERVICE_AREA)
    solver = pulp.PULP_CBC_CMD(msg=False, warmStart=True)
    lscp_from_cost_matrix = lscp_from_cost_matrix.solve(solver)
    lscp_from_cost_matrix.facility_client_array()
    return lscp_from_cost_matrix


if __name__ == "__main__":
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
    lscp_from_cost_matrix = get_the_serving_locations_for_patients(ntw)
    serviced_points, selected_sites = get_serviced_points_and_selected_sites(
        lscp_from_cost_matrix
    )
    plot_optimal_solution(serviced_points, selected_sites, streets_gpd)
