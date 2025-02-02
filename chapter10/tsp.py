import argparse

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
    breakpoint()


def main(api_key: str) -> None:
    get_gmaps_client(api_key)
    generate_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
