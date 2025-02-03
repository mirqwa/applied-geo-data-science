import argparse

import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pulp

import constants
import utils


def get_optimal_distances(distances: np.array):
    tsp_problem = pulp.LpProblem("tsp_mip", pulp.LpMinimize)
    x = pulp.LpVariable.dicts(
        "x",
        (
            (i, j)
            for i in range(constants.CUSTOMERS + 1)
            for j in range(constants.CUSTOMERS + 1)
        ),
        lowBound=0,
        upBound=1,
        cat="Binary",
    )
    u = pulp.LpVariable.dicts(
        "u",
        (i for i in range(constants.CUSTOMERS + 1)),
        lowBound=1,
        upBound=(constants.CUSTOMERS + 1),
        cat="Integer",
    )
    tsp_problem += pulp.lpSum(
        distances[i][j] * x[i, j]
        for i in range(constants.CUSTOMERS + 1)
        for j in range(constants.CUSTOMERS + 1)
    )
    for i in range(constants.CUSTOMERS + 1):
        tsp_problem += x[i, i] == 0
    for i in range(constants.CUSTOMERS + 1):
        tsp_problem += pulp.lpSum(x[i, j] for j in range(constants.CUSTOMERS + 1)) == 1
        tsp_problem += pulp.lpSum(x[j, i] for j in range(constants.CUSTOMERS + 1)) == 1
    for i in range(constants.CUSTOMERS + 1):
        for j in range(constants.CUSTOMERS + 1):
            if i != j and (i != 0 and j != 0):
                tsp_problem += (
                    u[i] - u[j] <= (constants.CUSTOMERS + 1) * (1 - x[i, j]) - 1
                )
    status = tsp_problem.solve()
    return x


def main(api_key: str) -> None:
    g_maps_client = utils.get_gmaps_client(api_key)
    data_gdf = utils.generate_data()
    distances = utils.get_origin_destination_cost_matrix(data_gdf, g_maps_client)
    x = get_optimal_distances(distances)
    utils.plot_solution(data_gdf, x)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
