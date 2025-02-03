import argparse

import utils


def main(api_key: str) -> None:
    g_maps_client = utils.get_gmaps_client(api_key)
    data_gdf = utils.generate_data_for_vrp()
    print("The number of packages:", data_gdf["customer_demand"].sum())
    distances = utils.get_origin_destination_cost_matrix(data_gdf, g_maps_client, True)
    x = utils.get_optimal_distances_for_vapacitated_vrp(data_gdf, distances, 5, 40)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
