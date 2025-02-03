import itertools

import geopandas as gpd
import gmaps
import numpy as np
import pandas as pd
import pulp

from googlemaps import Client

import constants


np.random.seed(32)


def generate_data() -> gpd.GeoDataFrame:
    locs = pd.DataFrame(
        {
            "latitude": np.random.normal(constants.WH_LAT, 0.008, constants.CUSTOMERS),
            "longitude": np.random.normal(constants.WH_LON, 0.008, constants.CUSTOMERS),
        }
    )
    cols = ["latitude", "longitude"]
    wh = pd.DataFrame([[constants.WH_LAT, constants.WH_LON]], columns=cols)
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


def generate_data_for_vrp() -> gpd.GeoDataFrame:
    demand = np.random.randint(2, 12, constants.CUSTOMERS).tolist()
    demand = [0] + demand
    data_gdf = generate_data()
    data_gdf["customer_demand"] = demand
    return data_gdf


def get_gmaps_client(api_key: str) -> Client:
    gmaps.configure(api_key=api_key)
    g_maps_client = Client(key=api_key)
    return g_maps_client


def get_optimal_distances_for_vrp(vehicles: int, distances: np.array):
    for vehicles in range(1, vehicles + 1):
        lp_problem = pulp.LpProblem("VRP", pulp.LpMinimize)
        x = [
            [
                [
                    pulp.LpVariable("x%s_%s,%s" % (i, j, k), cat="Binary")
                    if i != j
                    else None
                    for k in range(vehicles)
                ]
                for j in range(constants.CUSTOMERS + 1)
            ]
            for i in range(constants.CUSTOMERS + 1)
        ]
        lp_problem += pulp.lpSum(
            distances[i][j] * x[i][j][k] if i != j else 0
            for k in range(vehicles)
            for j in range(constants.CUSTOMERS + 1)
            for i in range(constants.CUSTOMERS + 1)
        )
        for j in range(1, constants.CUSTOMERS + 1):
            lp_problem += (
                pulp.lpSum(
                    x[i][j][k] if i != j else 0
                    for i in range(constants.CUSTOMERS + 1)
                    for k in range(vehicles)
                )
                == 1
            )
        for k in range(vehicles):
            lp_problem += (
                pulp.lpSum(x[0][j][k] for j in range(1, constants.CUSTOMERS + 1)) == 1
            )
            lp_problem += (
                pulp.lpSum(x[i][0][k] for i in range(1, constants.CUSTOMERS + 1)) == 1
            )
        for k in range(vehicles):
            for j in range(constants.CUSTOMERS + 1):
                lp_problem += (
                    pulp.lpSum(
                        x[i][j][k] if i != j else 0
                        for i in range(constants.CUSTOMERS + 1)
                    )
                    - pulp.lpSum(x[j][i][k] for i in range(constants.CUSTOMERS + 1))
                    == 0
                )
        subtours = []
        for i in range(2, constants.CUSTOMERS + 1):
            subtours += itertools.combinations(range(1, constants.CUSTOMERS + 1), i)
        for s in subtours:
            lp_problem += (
                pulp.lpSum(
                    x[i][j][k] if i != j else 0
                    for i, j in itertools.permutations(s, 2)
                    for k in range(vehicles)
                )
                <= len(s) - 1
            )

        if lp_problem.solve() == 1:
            print("# Required Vehicles:", vehicles)
            print("Distance:", pulp.value(lp_problem.objective))
            break
