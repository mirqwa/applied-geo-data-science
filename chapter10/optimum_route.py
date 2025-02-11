import argparse

import utils


def main(api_key: str) -> None:
    g_maps_client = utils.get_gmaps_client(api_key)
    geocode_result = g_maps_client.geocode("Kitale")
    location = geocode_result[0]["geometry"]["location"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
