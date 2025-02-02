import argparse

import contextily as cx
import geopandas as gpd
import gmaps
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp

from googlemaps import Client


np.random.seed(32)

CUSTOMERS = 15
WH_LAT = 40.749587
WH_LON = -73.985441


def get_gmaps_client(api_key: str) -> Client:
    gmaps.configure(api_key=api_key)
    g_maps_client = Client(key=api_key)
    return g_maps_client


def generate_data() -> gpd.GeoDataFrame:
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


def get_origin_destination_cost_matrix(
    data_gdf: gpd.GeoDataFrame, g_maps_client: Client
) -> np.array:
    distances = np.zeros((len(data_gdf), len(data_gdf)))
    data_gdf["coord"] = (
        data_gdf.latitude.astype(str) + "," + data_gdf.longitude.astype(str)
    )
    for lat in range(len(data_gdf)):
        for lon in range(len(data_gdf)):
            maps_api_result = g_maps_client.directions(
                data_gdf["coord"].iloc[lat], data_gdf["coord"].iloc[lon], mode="driving"
            )
            distances[lat][lon] = maps_api_result[0]["legs"][0]["distance"]["value"]
    return distances.astype(int)


def get_optimal_distances(distances: np.array):
    tsp_problem = pulp.LpProblem("tsp_mip", pulp.LpMinimize)
    x = pulp.LpVariable.dicts(
        "x",
        ((i, j) for i in range(CUSTOMERS + 1) for j in range(CUSTOMERS + 1)),
        lowBound=0,
        upBound=1,
        cat="Binary",
    )
    u = pulp.LpVariable.dicts(
        "u",
        (i for i in range(CUSTOMERS + 1)),
        lowBound=1,
        upBound=(CUSTOMERS + 1),
        cat="Integer",
    )
    tsp_problem += pulp.lpSum(
        distances[i][j] * x[i, j]
        for i in range(CUSTOMERS + 1)
        for j in range(CUSTOMERS + 1)
    )
    for i in range(CUSTOMERS + 1):
        tsp_problem += x[i, i] == 0
    for i in range(CUSTOMERS + 1):
        tsp_problem += pulp.lpSum(x[i, j] for j in range(CUSTOMERS + 1)) == 1
        tsp_problem += pulp.lpSum(x[j, i] for j in range(CUSTOMERS + 1)) == 1
    for i in range(CUSTOMERS + 1):
        for j in range(CUSTOMERS + 1):
            if i != j and (i != 0 and j != 0):
                tsp_problem += u[i] - u[j] <= (CUSTOMERS + 1) * (1 - x[i, j]) - 1
    status = tsp_problem.solve()
    return x


def plot_solution(data_gdf: gpd.GeoDataFrame, x: dict):
    f, ax = plt.subplots(1, figsize=(10, 10))

    data_gdf.plot(ax=ax, color=data_gdf["colors"])

    # Add basemap
    cx.add_basemap(ax, crs=data_gdf.crs, zoom=16)

    for lon, lat, label in zip(
        data_gdf.geometry.x, data_gdf.geometry.y, data_gdf.Label
    ):
        ax.annotate(label, xy=(lon, lat), xytext=(3, 3), textcoords="offset points")

    # Plot the optimal route between stops
    routes = [
        (i, j)
        for i in range(CUSTOMERS + 1)
        for j in range(CUSTOMERS + 1)
        if pulp.value(x[i, j]) == 1
    ]

    arrowprops = dict(arrowstyle="->", connectionstyle="arc3", edgecolor="darkblue")

    for i, j in routes:
        ax.annotate(
            "",
            xy=[data_gdf.iloc[j].geometry.x, data_gdf.iloc[j].geometry.y],
            xytext=[data_gdf.iloc[i].geometry.x, data_gdf.iloc[i].geometry.y],
            arrowprops=arrowprops,
        )

    plt.show()


def main(api_key: str) -> None:
    g_maps_client = get_gmaps_client(api_key)
    data_gdf = generate_data()
    distances = get_origin_destination_cost_matrix(data_gdf, g_maps_client)
    x = get_optimal_distances(distances)
    plot_solution(data_gdf, x)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
