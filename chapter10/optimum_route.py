import argparse
from datetime import datetime
from pathlib import Path
import random

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import utils


random.seed(32)

CITIES = [
    "Nairobi",
    "Mombasa",
    "Kitale",
    "Kisumu",
    "Machakos",
    "Thika",
    "Nakuru",
    "Bungoma",
    "Naivasha",
    "Kisii",
    "Kakamega",
    "Webuye",
    "Kabarnet",
    "Iten",
    "Eldoret",
    "Busia",
    "Mau Summit",
    "Kericho",
    "Kapsabet",
    "Chemelil",
    "Muhoroni",
    "Burnt Forest",
    "Thika",
    "Maai Mahiu",
    "Longonot",
    "Narok",
    "Malaba",
]


def plot_cities(cities_gdf: gpd.GeoDataFrame) -> None:
    ax = utils.plot_data_with_basemap(cities_gdf)
    plt.show()


def prepare_cities_data(g_maps_client, use_saved_coordinates=False) -> gpd.GeoDataFrame:
    file_name = "data/kenya/cities.geojson"
    if Path(file_name).is_file() and use_saved_coordinates:
        return gpd.read_file(file_name)
    cities_locations = []
    for city in CITIES:
        geocode_result = g_maps_client.geocode(city)
        location = {
            "Label": city,
            "colors": random.choice(
                ["black", "red", "green", "blue", "purple", "orange"]
            ),
        }
        try:
            location.update(geocode_result[0]["geometry"]["location"])
            cities_locations.append(location)
        except Exception:
            print(f"Failed to get coordinates for {city}")
    cities_locations_df = pd.DataFrame(cities_locations)
    cities_locations_gdf = gpd.GeoDataFrame(
        cities_locations_df,
        geometry=gpd.points_from_xy(
            cities_locations_df["lng"], cities_locations_df["lat"]
        ),
        crs="EPSG:4326",
    )
    cities_locations_gdf.to_file(file_name)
    return cities_locations_gdf


def get_origin_destination_cost_matrix(
    cities_locations_gdf: gpd.GeoDataFrame, g_maps_client, use_saved_distances=False
) -> np.ndarray:
    file_name = f"data/kenya/distances_{len(cities_locations_gdf) - 1}.npy"
    if Path(file_name).is_file() and use_saved_distances:
        return np.load(file_name)
    distances = np.zeros((len(cities_locations_gdf), len(cities_locations_gdf)))
    cities_locations_gdf["coord"] = (
        cities_locations_gdf.lat.astype(str)
        + ","
        + cities_locations_gdf.lng.astype(str)
    )
    for lat in range(len(cities_locations_gdf)):
        for lon in range(len(cities_locations_gdf)):
            maps_api_result = g_maps_client.directions(
                cities_locations_gdf["coord"].iloc[lat],
                cities_locations_gdf["coord"].iloc[lon],
                mode="driving",
            )
            distances[lat][lon] = maps_api_result[0]["legs"][0]["distance"]["value"]
    distances = distances.astype(int)
    np.save(file_name, distances)
    return distances


def main(api_key: str) -> None:
    g_maps_client = utils.get_gmaps_client(api_key)
    cities_locations_gdf = prepare_cities_data(g_maps_client, use_saved_coordinates=True)
    plot_cities(cities_locations_gdf)
    distances = get_origin_destination_cost_matrix(
        cities_locations_gdf, g_maps_client, use_saved_distances=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
