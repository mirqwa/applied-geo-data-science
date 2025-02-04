import os

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pykrige.ok import OrdinaryKriging
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


def get_weather_data() -> gpd.GeoDataFrame:
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
    return mean_temperature_gdf


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


def plot_interpolated_values(
    temps_array: np.array,
    z: np.array,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
) -> None:
    im = plt.imshow(
        z,
        extent=[min_x - 0.05, max_x + 0.05, min_y - 0.05, max_y + 0.05],
        origin="lower",
        cmap="coolwarm",
    )
    plt.scatter(
        temps_array[:, 0],
        temps_array[:, 1],
        c=temps_array[:, 2],
        alpha=0.5,
        marker="o",
        s=20,
        edgecolors="black",
        linewidth=1,
        cmap="coolwarm",
    )
    cbar = plt.colorbar(im)
    plt.title("Interpolated Temperature")
    plt.show()


def ordinary_kriging_interpolation(mean_temperature_gdf: gpd.GeoDataFrame) -> None:
    min_x = min(mean_temperature_gdf["Longitude"])
    max_x = max(mean_temperature_gdf["Longitude"])
    min_y = min(mean_temperature_gdf["Latitude"])
    max_y = max(mean_temperature_gdf["Latitude"])
    gridx = np.arange(min_x, max_x, 0.05, dtype="float64")
    gridy = np.arange(min_y, max_y, 0.05, dtype="float64")

    temps_nogeom = mean_temperature_gdf.drop(["geometry"], axis=1)
    temps_array = temps_nogeom.to_numpy()

    Orid_Krig = OrdinaryKriging(
        temps_array[:, 0],  # Longitude vector
        temps_array[:, 1],  # Latitude vector
        temps_array[:, 2],  # Temperatures vector
        variogram_model="gaussian",  # The semivariogram model
        verbose=True,  # True writes out the steps as they're being performed
        enable_plotting=True,  # True plots the emperical semivariogram
    )

    z, _ = Orid_Krig.execute("grid", gridx, gridy)
    plot_interpolated_values(temps_array, z, min_x, max_x, min_y, max_y)


if __name__ == "__main__":
    mean_temperature_gdf = get_weather_data()
    # get_region()
    # idw_interpolation()
    ordinary_kriging_interpolation(mean_temperature_gdf)
