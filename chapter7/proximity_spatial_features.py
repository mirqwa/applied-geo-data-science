import geopandas as gpd
import pandas as pd


def get_listings_gdf() -> gpd.GeoDataFrame:
    listings = pd.read_csv("data/listings.csv.gz", compression="gzip")
    listings_gdf = gpd.GeoDataFrame(
        listings,
        geometry=gpd.points_from_xy(listings["longitude"], listings["latitude"]),
        crs="EPSG:4326",
    )
    return listings_gdf


def get_manhattan() -> gpd.GeoDataFrame:
    boroughs = gpd.read_file("data/new_york/nybb.shp")
    manhattan = boroughs[boroughs["BoroName"] == "Manhattan"]
    manhattan = manhattan.to_crs("EPSG:4326")
    return manhattan


if __name__ == "__main__":
    listings_gdf = get_listings_gdf()
    manhattan = get_manhattan()
