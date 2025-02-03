import geopandas as gpd
import pandas as pd


def get_listings():
    listings_df = pd.read_csv("data/listings.csv.gz")
    listings_gdf = gpd.GeoDataFrame(
        listings_df,
        geometry=gpd.points_from_xy(listings_df["longitude"], listings_df["latitude"]),
        crs="EPSG:4326",
    )
    return listings_gdf


if __name__ == "__main__":
    listings_gdf = get_listings()
