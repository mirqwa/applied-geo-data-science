import geopandas as gpd
import pandas as pd


def get_places_of_worship_gdf() -> gpd.GeoDataFrame:
    places_of_worship_df = pd.read_csv("data/osm/nairobi_worship_places.csv")
    places_of_worship_gdf = gpd.GeoDataFrame(
        places_of_worship_df,
        geometry=gpd.points_from_xy(
            places_of_worship_df["lon"], places_of_worship_df["lat"]
        ),
        crs=4326
    )
    return places_of_worship_gdf


if __name__ == "__main__":
    places_of_worship_gdf = get_places_of_worship_gdf()
