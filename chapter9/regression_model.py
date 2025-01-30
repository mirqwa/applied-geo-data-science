import geopandas as gpd
import numpy as np


def one_hot_encode_room_types(manhattan_listings: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    manhattan_listings["rt_entire_home_apartment"] = np.where(
        manhattan_listings["room_type"] == "Entire home/apt", 1, 0
    )
    manhattan_listings["rt_private_room"] = np.where(
        manhattan_listings["room_type"] == "Private room", 1, 0
    )
    manhattan_listings["rt_shared_room"] = np.where(
        manhattan_listings["room_type"] == "Shared room", 1, 0
    )
    return manhattan_listings


def format_price(manhattan_listings: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    manhattan_listings["price"] = manhattan_listings["price"].str.replace("$", "")
    manhattan_listings["price"] = manhattan_listings["price"].str.replace(",", "")
    manhattan_listings["price"] = manhattan_listings["price"].astype(float)
    return manhattan_listings


def get_train_data() -> gpd.GeoDataFrame:
    manhattan_listings = gpd.read_file("data/new_york/manhattan_listings.geojson")
    variables = [
        "id",  # Unique identifier for the listing
        "room_type",  # Type of room
        "accommodates",  # The maximum capacity of the listing
        "bedrooms",  # The number of bedrooms
        "beds",  # The number of beds
        "review_scores_rating",  # The rating
        "price",  # The nightly rental rate, dependent variable (Y)
    ]
    manhattan_listings = manhattan_listings[variables]
    manhattan_listings = one_hot_encode_room_types(manhattan_listings)
    manhattan_listings = format_price(manhattan_listings)


if __name__ == "__main__":
    manhattan_listings = get_train_data()
