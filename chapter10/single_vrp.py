import argparse

import numpy as np
import pulp

import constants
import utils


def get_routes(x: np.array) -> list:
    routes = [
        (k, i, j)
        for k in range(1)
        for i in range(constants.CUSTOMERS + 1)
        for j in range(constants.CUSTOMERS + 1)
        if i != j and pulp.value(x[i][j][k]) == 1
    ]

    return routes


def main(api_key: str) -> None:
    g_maps_client = utils.get_gmaps_client(api_key)
    data_gdf = utils.generate_data_for_vrp()
    distances = utils.get_origin_destination_cost_matrix(data_gdf, g_maps_client, True)
    x = utils.get_optimal_distances_for_vrp(1, distances)
    routes = get_routes(x)
    utils.plot_vrp_solution(data_gdf, routes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
