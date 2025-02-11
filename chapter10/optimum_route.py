import argparse

import geopandas as gpd
import pandas as pd

import utils

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
]


def prepare_cities_data(g_maps_client):
    cities_locations = []
    for city in CITIES:
        geocode_result = g_maps_client.geocode(city)
        location = {"city": city}
        try:
            location.update(geocode_result[0]["geometry"]["location"])
            cities_locations.append(location)
        except Exception:
            print(f"Failed to get coordinates for {city}")
    cities_locations_df = pd.DataFrame(cities_locations)
    cities_locations_gpd = gpd.GeoDataFrame(
        cities_locations_df,
        geometry=gpd.points_from_xy(
            cities_locations_df["lng"], cities_locations_df["lat"]
        ),
        crs="EPSG:4326",
    )
    cities_locations_gpd.to_file("data/kenya/cities.geojson")


def main(api_key: str) -> None:
    g_maps_client = utils.get_gmaps_client(api_key)
    prepare_cities_data(g_maps_client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
