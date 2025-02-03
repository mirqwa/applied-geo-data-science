import geopandas as gpd
import pandas as pd


def get_listings() -> gpd.GeoDataFrame:
    listings_df = pd.read_csv("data/listings.csv.gz")
    listings_gdf = gpd.GeoDataFrame(
        listings_df,
        geometry=gpd.points_from_xy(listings_df["longitude"], listings_df["latitude"]),
        crs="EPSG:4326",
    )
    return listings_gdf


def get_manhattan_boroughs() -> gpd.GeoDataFrame:
    boroughs = gpd.read_file("data/new_york/nybb.shp")
    manhattan_boroughs = boroughs[boroughs["BoroName"] == "Manhattan"]
    manhattan_boroughs = manhattan_boroughs.to_crs("EPSG:4326")
    return manhattan_boroughs


if __name__ == "__main__":
    listings_gdf = get_listings()
    manhattan_boroughs = get_manhattan_boroughs()
