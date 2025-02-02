import argparse

import geopandas as gpd
import gmaps
import numpy as np
import pandas as pd

from googlemaps import Client


np.random.seed(32)

CUSTOMERS = 15
WH_LAT = 40.749587
WH_LON = -73.985441


def get_gmaps_client(api_key: str):
    gmaps.configure(api_key=api_key)
    client = Client(key=api_key)


def generate_data():
    locs = pd.DataFrame(
        {
            "latitude": np.random.normal(WH_LAT, 0.008, CUSTOMERS),
            "longitude": np.random.normal(WH_LON, 0.008, CUSTOMERS),
        }
    )
    cols = ["latitude", "longitude"]
    wh = pd.DataFrame([[WH_LAT, WH_LON]], columns=cols)
    data = pd.concat([wh, locs])
    data.reset_index(inplace=True)
    data.drop(["index"], axis=1, inplace=True)
    data.reset_index(inplace=True)
    data.rename(columns={"index": "Label"}, inplace=True)
    data["Label"] = data["Label"].astype(str)
    data.at[0, "Label"] = "Warehouse"
    data["colors"] = np.where(
        data["Label"] == "Warehouse", "darkslateblue", "forestgreen"
    )
    data_gdf = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(data.longitude, data.latitude, crs="EPSG:4326"),
    )
    return data_gdf


def main(api_key: str) -> None:
    get_gmaps_client(api_key)
    data = generate_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
