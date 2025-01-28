import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pointpats import distance_statistics


def plot_places_of_worship(places_of_worship_gdf: gpd.GeoDataFrame) -> None:
    places_of_worship_wm = places_of_worship_gdf.to_crs(epsg=3857)
    ax = places_of_worship_wm.plot(figsize=(10, 10), alpha=0.5, edgecolor="k")
    cx.add_basemap(ax, crs=places_of_worship_wm.crs, zoom=12)
    ax.set_axis_off()
    plt.show()


def get_places_of_worship_gdf() -> gpd.GeoDataFrame:
    places_of_worship_df = pd.read_csv("data/osm/nairobi_worship_places.csv")
    places_of_worship_gdf = gpd.GeoDataFrame(
        places_of_worship_df,
        geometry=gpd.points_from_xy(places_of_worship_df.lon, places_of_worship_df.lat),
        crs="EPSG:4326",
    )
    return places_of_worship_gdf


def get_and_plot_ripleys_g(places_of_worship_gdf: gpd.GeoDataFrame) -> None:
    g_test = distance_statistics.g_test(
        places_of_worship_gdf[["lon", "lat"]].values, support=40, keep_simulations=True
    )
    plt.plot(
        g_test.support,
        np.median(g_test.simulations, axis=0),
        color="k",
        label="Simulated Data",
    )
    plt.plot(
        g_test.support,
        g_test.statistic,
        marker="x",
        color="orangered",
        label="Observed Data",
    )
    plt.legend()
    plt.xlabel("Distance")
    plt.ylabel("Ripleys G Function")
    plt.title("Ripleys G Function Plot")
    plt.show()


def get_and_plot_ripleys_k(places_of_worship_gdf: gpd.GeoDataFrame) -> None:
    k_test = distance_statistics.k_test(
        places_of_worship_gdf[["lon", "lat"]].values, support=40, keep_simulations=True
    )
    plt.plot(k_test.support, k_test.simulations.T, color="k", alpha=0.01)
    plt.plot(k_test.support, k_test.statistic, color="orange")
    plt.scatter(
        k_test.support,
        k_test.statistic,
        cmap="viridis",
        c=k_test.pvalue < 0.05,
        zorder=4,
    )
    plt.xlabel("Distance")
    plt.ylabel("Ripleys K Function")
    plt.title("Ripleys K Function Plot")
    plt.show()


if __name__ == "__main__":
    places_of_worship_gdf = get_places_of_worship_gdf()
    plot_places_of_worship(places_of_worship_gdf)
    get_and_plot_ripleys_g(places_of_worship_gdf)
    get_and_plot_ripleys_k(places_of_worship_gdf)
