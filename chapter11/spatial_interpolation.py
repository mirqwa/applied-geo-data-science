import os

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from pyidw import idw


def plot_average_temperature(mean_temperature_gdf: gpd.GeoDataFrame) -> None:
    temps_nogeom = mean_temperature_gdf.drop(["geometry"], axis=1)
    temps_array = temps_nogeom.to_numpy()
    obs = plt.scatter(
        temps_array[:, 0], temps_array[:, 1], c=temps_array[:, 2], cmap="coolwarm"
    )
    cbar = plt.colorbar(obs)
    plt.title("Observed Temperatures")
    plt.show()


def get_weather_data() -> None:
    weather_dir = "data/weather/processed_stations/2025/2025-02"
    weather_files = os.listdir(weather_dir)
    dfs = []
    for weather_file in weather_files:
        dfs.append(pd.read_csv(f"{weather_dir}/{weather_file}"))
    weather_df = pd.concat(dfs)
    weather_df = weather_df[weather_df["Date"] == "2025-02-01"]
    weather_df = weather_df.dropna()
    weather_df = weather_df.rename(columns={"Temperature": "Temp"})
    mean_temperature_df = (
        weather_df.groupby(["Longitude", "Latitude"])["Temp"].mean().reset_index()
    )
    mean_temperature_gdf = gpd.GeoDataFrame(
        mean_temperature_df,
        geometry=gpd.points_from_xy(
            mean_temperature_df["Longitude"], mean_temperature_df["Latitude"]
        ),
        crs="EPSG:4326",
    )
    print(mean_temperature_gdf.shape)
    plot_average_temperature(mean_temperature_gdf)
    mean_temperature_gdf.to_file("data/weather/2025-02-01/temperature.shp")


def get_region() -> None:
    path = "data/weather/regions/NUTS1_Jan_2018_UGCB_in_the_UK_2022_-1274845379350881254.geojson"
    uk_gdf = gpd.read_file(path)
    uk_gdf = uk_gdf.to_crs("EPSG:4326")
    england_gdf = uk_gdf[
        ~uk_gdf["nuts118nm"].isin(["Wales", "Scotland", "Northern Ireland"])
    ]
    uk_gdf = uk_gdf.dissolve()
    uk_gdf.to_file("data/weather/uk/uk.shp")
    england_gdf = england_gdf.dissolve()
    england_gdf.to_file("data/weather/england/england.shp")


def idw_interpolation() -> None:
    idw.idw_interpolation(
        input_point_shapefile="data/weather/2025-02-01/temperature.shp",
        extent_shapefile="data/weather/england/england.shp",
        column_name="Temp",
        power=2,
        search_radious=3,
        output_resolution=250,
    )


if __name__ == "__main__":
    get_weather_data()
    get_region()
    idw_interpolation()
