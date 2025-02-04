import os

import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def plot_average_temperature(mean_temperature_gdf: gpd.GeoDataFrame) -> None:
    _, ax = plt.subplots(1, figsize=(15, 15))
    mean_temperature_gdf_wm = mean_temperature_gdf.to_crs(epsg=3857)
    mean_temperature_gdf_wm.plot(ax=ax, alpha=0.5, edgecolor="k")
    cx.add_basemap(
        ax,
        crs=mean_temperature_gdf_wm.crs,
        zoom=16,
        source=cx.providers.OpenStreetMap.Mapnik,
    )
    ax.set_axis_off()
    plt.show()


def get_weather_data():
    weather_dir = "data/weather/processed_stations/2025/2025-02"
    weather_files = os.listdir(weather_dir)
    dfs = []
    for weather_file in weather_files:
        dfs.append(pd.read_csv(f"{weather_dir}/{weather_file}"))
    weather_df = pd.concat(dfs)
    weather_df = weather_df[weather_df["Date"] == "2025-02-01"]
    weather_df = weather_df.dropna()
    mean_temperature_df = (
        weather_df.groupby(["Longitude", "Latitude"])["Temperature"]
        .mean()
        .reset_index()
    )
    mean_temperature_gdf = gpd.GeoDataFrame(
        mean_temperature_df,
        geometry=gpd.points_from_xy(
            mean_temperature_df["Longitude"], mean_temperature_df["Latitude"]
        ),
        crs="EPSG:4326",
    )
    plot_average_temperature(mean_temperature_gdf)


if __name__ == "__main__":
    get_weather_data()
