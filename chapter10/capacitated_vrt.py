import argparse

import utils


VEHICLES = 5
CAPACITY = 40


def main(api_key: str) -> None:
    g_maps_client = utils.get_gmaps_client(api_key)
    data_gdf = utils.generate_data_for_vrp()
    print("The number of packages:", data_gdf["customer_demand"].sum())
    distances = utils.get_origin_destination_cost_matrix(data_gdf, g_maps_client, True)
    x, vehicles = utils.get_optimal_distances_for_capacitated_vrp(
        data_gdf, distances, VEHICLES, CAPACITY
    )
    routes = utils.get_vrt_routes(x, vehicles)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
