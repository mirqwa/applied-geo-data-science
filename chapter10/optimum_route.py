import argparse
from datetime import datetime
from pathlib import Path
import random

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
    "Kisii",
    "Kakamega",
    "Webuye",
    "Kabarnet",
    "Iten",
    "Eldoret",
    "Busia",
    "Mau Summit",
    "Kericho",
    "Kapsabet",
    "Chemelil",
    "Muhoroni",
    "Burnt Forest",
    "Thika",
    "Maai Mahiu",
    "Longonot",
    "Narok",
    "Malaba",
    "Nyeri",
    "Embu",
    "Narok",
    "Ruiru",
    "Ngong",
    "Kapenguria",
    "Kericho",
    "Kimende",
    "Kampala",
    "Jinja",
    "Busia",
    "Mbale",
    "Tororo",
    "Lwakhakha",
    "Suam",
    "Turbo",
    "Entebbe",
]
CITIES_TO_LABEL = [
    "Nairobi",
    "Kitale",
]
EPSILON = 0.2
LEARNING_RATE = 0.8
DISCOUNT_FACTOR = 0.95


def plot_cities(cities_gdf: gpd.GeoDataFrame, path: list = []) -> None:
    _, ax = plt.subplots(1, figsize=(15, 15))

    cities_gdf.plot(ax=ax, color="black", markersize=30)

    # Add basemap
    cx.add_basemap(
        ax, crs=cities_gdf.crs, zoom=8, source=cx.providers.OpenStreetMap.Mapnik
    )

    for lon, lat, label in zip(
        cities_gdf.geometry.x, cities_gdf.geometry.y, cities_gdf.Label
    ):
        if label in CITIES_TO_LABEL:
            ax.annotate(
                label,
                xy=(lon, lat),
                xytext=(3, -3),
                textcoords="offset points",
                size=12,
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


def get_origin_destination_cost_matrix(
    cities_locations_gdf: gpd.GeoDataFrame, g_maps_client, use_saved_distances=False
) -> np.ndarray:
    file_name = f"data/east_africa/distances_{len(cities_locations_gdf) - 1}.npy"
    if Path(file_name).is_file() and use_saved_distances:
        distances = np.load(file_name)
        distances = distances.astype(int)
        distances = np.where(distances == 0, float("inf"), distances)
        return distances
    distances = np.zeros((len(cities_locations_gdf), len(cities_locations_gdf)))
    cities_locations_gdf["coord"] = (
        cities_locations_gdf.lat.astype(str)
        + ","
        + cities_locations_gdf.lng.astype(str)
    )
    for lat in range(len(cities_locations_gdf)):
        for lon in range(len(cities_locations_gdf)):
            maps_api_result = g_maps_client.directions(
                cities_locations_gdf["coord"].iloc[lat],
                cities_locations_gdf["coord"].iloc[lon],
                mode="driving",
            )
            distances[lat][lon] = maps_api_result[0]["legs"][0]["distance"]["value"]
    distances = distances.astype(int)
    distances = np.where(distances == 0, float("inf"), distances)
    np.save(file_name, distances)
    return distances


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
            possible_actions = (
                np.where(distances[current_city, :] > 0)[0]
                if np.random.uniform(0, 1) < EPSILON
                else np.where(
                    q_table[current_city, :] == np.max(q_table[current_city, :])
                )[0]
            )
            if len(possible_actions) == 0:
                break
            action = np.random.choice(possible_actions)
            next_node = action
            reward = -distances[current_city, next_node]
            q_table[current_city, next_node] = (1 - LEARNING_RATE) * q_table[
                current_city, next_node
            ] + LEARNING_RATE * (
                reward + DISCOUNT_FACTOR * np.max(q_table[next_node, :])
            )
            current_city = next_node
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


def get_optimum_path(
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
        cities_locations_gdf, 10000, start_city_index, end_city_index, distances
    )
    shortest_path, route = get_shortest_path(q_table, start_city_index, end_city_index)
    shortest_path = [
        cities_locations_gdf["Label"][city_index] for city_index in shortest_path
    ]
    return shortest_path, route


def get_solution(problem_variables: list):
    cities_in_path = []
    for v in problem_variables:
        if v.varValue == 1:
            cities_in_path.append(v.name)
    breakpoint()


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
    distances = get_origin_destination_cost_matrix(
        cities_locations_gdf, g_maps_client, use_saved_distances=True
    )
    breakpoint()
    shortest_path, route = get_optimum_path(
        cities_locations_gdf, distances, "Nairobi", "Malaba"
    )
    plot_cities(cities_locations_gdf, route)
    shortest_path_using_pulp(cities_locations_gdf, distances, "Nairobi", "Malaba")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=True)

    args = parser.parse_args()
    main(args.api_key)
