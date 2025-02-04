import os

import geopandas as gpd
import pandas as pd


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


if __name__ == "__main__":
    get_weather_data()
