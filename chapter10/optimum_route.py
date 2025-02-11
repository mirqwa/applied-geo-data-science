import argparse
import random

import geopandas as gpd
import matplotlib.pyplot as plt
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


def prepare_cities_data(g_maps_client) -> gpd.GeoDataFrame:
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
    cities_locations_gpf = gpd.GeoDataFrame(
        cities_locations_df,
        geometry=gpd.points_from_xy(
            cities_locations_df["lng"], cities_locations_df["lat"]
        ),
        crs="EPSG:4326",
    )
    cities_locations_gpf.to_file("data/kenya/cities.geojson")
    return cities_locations_gpf


def main(api_key: str) -> None:
    g_maps_client = utils.get_gmaps_client(api_key)
    cities_locations_gpf = prepare_cities_data(g_maps_client)
    plot_cities(cities_locations_gpf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
