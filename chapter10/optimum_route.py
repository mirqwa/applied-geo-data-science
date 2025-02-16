import argparse
from datetime import datetime
from pathlib import Path
import random
import time

import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp

import utils


random.seed(32)
np.random.seed(32)

CITIES = [
    "Nairobi",
    "Kitale",
    "Kisumu",
    "Machakos",
    "Thika",
    "Nakuru",
    "Bungoma",
    "Naivasha",
    "Kakamega",
    "Webuye",
    "Iten",
    "Eldoret",
    "Busia",
    "Kericho",
    "Thika",
    "Narok",
    "Malaba",
    "Narok",
    "Kericho",
    "Kampala",
    "Jinja",
    "Busia",
    "Mbale",
    "Tororo",
    "Lwakhakha",
    "Suam",
    "Entebbe",
    "Siaya",
    "Eldama Ravine",
    "Bomet",
    "Bondo",
    "Ahero",
    "Muhoroni",
    "Butere",
    "Ugunja",
    "Chwele",
]
CITIES_TO_LABEL = {"Nairobi": "ORIGIN", "Kampala": "DESTINATION"}
EPSILON = 0.2
LEARNING_RATE = 0.8
DISCOUNT_FACTOR = 0.95


def plot_cities(cities_gdf: gpd.GeoDataFrame, path: list = []) -> None:
    _, ax = plt.subplots(1, figsize=(15, 15))
    cities_gdf["markersize"] = np.where(
        cities_gdf["Label"].isin(["Nairobi", "Kampala"]), 150, 50
    )
    cities_gdf["color"] = np.where(
        cities_gdf["Label"].isin(["Nairobi", "Kampala"]), "red", "purple"
    )

    cities_gdf.plot(
        ax=ax, color=cities_gdf["color"], markersize=cities_gdf["markersize"], alpha=0.5
    )

    # Add basemap
    cx.add_basemap(
        ax, crs=cities_gdf.crs, zoom=8, source=cx.providers.OpenStreetMap.Mapnik
    )

    for lon, lat, label in zip(
        cities_gdf.geometry.x, cities_gdf.geometry.y, cities_gdf.Label
    ):
        city_label = CITIES_TO_LABEL.get(label)
        if city_label:
            ax.annotate(
                city_label,
                xy=(lon, lat),
                xytext=(-20, -20),
                textcoords="offset points",
                size=15,
                color="blue"
            )
    for i, j in path:
        utils.annotate_route(ax, cities_gdf, i, j, "darkblue")
    ax.set_axis_off()
    plt.show()


def prepare_cities_data(g_maps_client, use_saved_coordinates=False) -> gpd.GeoDataFrame:
    file_name = "data/east_africa/cities.geojson"
    if Path(file_name).is_file() and use_saved_coordinates:
        return gpd.read_file(file_name)
    cities_locations = []
    for city in CITIES:
        geocode_result = g_maps_client.geocode(city)
        location = {
            "Label": city,
            "colors": random.choice(
                ["black", "red", "green", "blue", "purple", "orange"]
            ),
        }
        try:
            location.update(geocode_result[0]["geometry"]["location"])
            cities_locations.append(location)
        except Exception:
            print(f"Failed to get coordinates for {city}")
    cities_locations_df = pd.DataFrame(cities_locations)
    cities_locations_gdf = gpd.GeoDataFrame(
        cities_locations_df,
        geometry=gpd.points_from_xy(
            cities_locations_df["lng"], cities_locations_df["lat"]
        ),
        crs="EPSG:4326",
    )
    cities_locations_gdf.to_file(file_name)
    return cities_locations_gdf


def get_intercity_distances(
    cities_locations_gdf: gpd.GeoDataFrame, g_maps_client, use_saved_distances=False
) -> np.ndarray:
    file_name = f"data/east_africa/distances_{len(cities_locations_gdf) - 1}.npy"
    if Path(file_name).is_file() and use_saved_distances:
        return np.load(file_name)
    distances = np.zeros((len(cities_locations_gdf), len(cities_locations_gdf)))
    cities_locations_gdf["coord"] = (
        cities_locations_gdf.lat.astype(str)
        + ","
        + cities_locations_gdf.lng.astype(str)
    )
    for lat in range(len(cities_locations_gdf)):
        for lon in range(len(cities_locations_gdf)):
            origin = cities_locations_gdf["Label"][lat]
            destination = cities_locations_gdf["Label"][lon]
            print(f"Getting distance for {origin} -> {destination}")
            maps_api_result = g_maps_client.directions(
                cities_locations_gdf["coord"].iloc[lat],
                cities_locations_gdf["coord"].iloc[lon],
                mode="driving",
            )
            distances[lat][lon] = maps_api_result[0]["legs"][0]["distance"]["value"]
    np.save(file_name, distances)
    return distances


def select_next_action(
    distances: np.ndarray, current_city: int, q_table: np.ndarray
) -> int:
    possible_actions = (
        np.where(distances[current_city, :] > 0)[0]  # exploration
        if np.random.uniform(0, 1) < EPSILON
        else np.where(
            q_table[current_city, :] == np.max(q_table[current_city, :])  # exploitation
        )[0]
    )
    if len(possible_actions) == 0:
        return
    return np.random.choice(possible_actions)


def update_q_table(
    q_table: np.ndarray,
    distances: np.ndarray,
    current_city: int,
    action: int,
    next_city: int,
) -> None:
    # the reward is negative since the goal is to have minimum distance
    reward = -distances[current_city, next_city]
    current_state_action_value = q_table[current_city, action]
    next_state_action_value = np.max(q_table[next_city, :])

    q_table[current_city, action] = (
        1 - LEARNING_RATE
    ) * current_state_action_value + LEARNING_RATE * (
        reward + DISCOUNT_FACTOR * next_state_action_value
    )


def get_q_learning_cost_table(
    cities_locations_gdf: gpd.GeoDataFrame,
    num_episodes: int,
    start_city_index: str,
    end_city_index: str,
    distances: np.ndarray,
) -> np.ndarray:
    q_table = np.zeros((cities_locations_gdf.shape[0], cities_locations_gdf.shape[0]))
    for _ in range(num_episodes):
        current_city = start_city_index
        while current_city != end_city_index:
            action = select_next_action(distances, current_city, q_table)
            if action is None:
                break
            next_city = action
            update_q_table(q_table, distances, current_city, action, next_city)

            current_city = next_city
            if current_city == end_city_index:
                break
    return q_table


def get_shortest_path(
    q_table: np.ndarray, start_city_index: int, end_city_index: int
) -> list:
    shortest_path = [start_city_index]
    current_city = start_city_index
    while current_city != end_city_index:
        next_city = np.argmax(q_table[current_city, :])
        shortest_path.append(next_city)
        current_city = next_city
    route = [(start, dest) for start, dest in zip(shortest_path, shortest_path[1:])]
    return shortest_path, route


def get_distance(distances: np.array, route: list) -> int:
    route_distance = 0
    for origin, destination in route:
        route_distance += distances[origin][destination]
    return int(route_distance)


def get_optimal_path(
    cities_locations_gdf: gpd.GeoDataFrame,
    distances: np.ndarray,
    start_city: str,
    end_city: str,
) -> list:
    start_city_index = cities_locations_gdf[
        cities_locations_gdf["Label"] == start_city
    ].index[0]
    end_city_index = cities_locations_gdf[
        cities_locations_gdf["Label"] == end_city
    ].index[0]
    q_table = get_q_learning_cost_table(
        cities_locations_gdf, 1000, start_city_index, end_city_index, distances
    )
    q_table_df = pd.DataFrame(
        data=q_table,
        index=cities_locations_gdf["Label"],
        columns=cities_locations_gdf["Label"],
    )
    q_table_df.to_csv(f"data/east_africa/{start_city}_{end_city}_q_table.csv")
    shortest_path, route = get_shortest_path(q_table, start_city_index, end_city_index)
    route_distance = get_distance(distances, route)
    shortest_path = [
        cities_locations_gdf["Label"][city_index] for city_index in shortest_path
    ]
    shortest_path = " -> ".join(shortest_path)
    return shortest_path, route


def get_solution(problem_variables: list):
    cities_in_path = []
    for v in problem_variables:
        if v.varValue == 1:
            cities_in_path.append(v.name)


def shortest_path_using_pulp(
    cities_locations_gdf: gpd.GeoDataFrame,
    distances: np.ndarray,
    start_city: str,
    end_city: str,
):
    prob = pulp.LpProblem("prob", pulp.LpMinimize)
    N = cities_locations_gdf["Label"].tolist()
    C = {
        x: {
            N[i]: distances[index, i]
            for i in range(len(N))
            if i != index and distances[index, i] != float("inf")
        }
        for index, x in enumerate(N)
    }
    D = {node: 1 if node == start_city else -1 if node == end_city else 0 for node in N}
    E = [(i, j) for i in N for j in N if i in C.keys() if j in C[i].keys()]
    x = pulp.LpVariable.dicts("x", E, lowBound=0, upBound=1, cat=pulp.LpInteger)

    prob += pulp.lpSum([C[i][j] * x[i, j] for (i, j) in E])

    for i in N:
        prob += (
            pulp.lpSum([x[i, j] for j in N if (i, j) in E])
            - pulp.lpSum([x[k, i] for k in N if (k, i) in E])
        ) == D[i]

    status = prob.solve()
    get_solution(prob.variables())


def main(api_key: str) -> None:
    g_maps_client = utils.get_gmaps_client(api_key)
    cities_locations_gdf = prepare_cities_data(
        g_maps_client, use_saved_coordinates=True
    )
    plot_cities(cities_locations_gdf)
    distances = get_intercity_distances(
        cities_locations_gdf, g_maps_client, use_saved_distances=True
    )
    distances_df = pd.DataFrame(
        data=distances,
        columns=cities_locations_gdf["Label"],
        index=cities_locations_gdf["Label"],
    )
    distances_df.to_csv("data/east_africa/distances.csv")
    distances = distances / 1000
    distances = np.where(distances == 0, float("inf"), distances)
    shortest_path, route = get_optimal_path(
        cities_locations_gdf, distances, "Nairobi", "Kampala"
    )
    print(shortest_path)
    print(route)
    plot_cities(cities_locations_gdf, route)
    shortest_path_using_pulp(cities_locations_gdf, distances, "Nairobi", "Kampala")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
