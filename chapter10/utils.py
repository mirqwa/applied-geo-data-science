import geopandas as gpd
import gmaps
import numpy as np
import pandas as pd

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
