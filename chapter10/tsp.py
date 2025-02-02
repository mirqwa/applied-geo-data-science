import argparse

import gmaps
import numpy as np

from googlemaps import Client


np.random.seed(32)

CUSTOMERS = 15
WH_LAT = 40.749587
WH_LON = -73.985441


def get_gmaps_client(api_key: str):
    gmaps.configure(api_key=api_key)
    client = Client(key=api_key)


def main(api_key: str) -> None:
    get_gmaps_client(api_key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
