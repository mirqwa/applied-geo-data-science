import geopandas as gpd
import pandas as pd


def get_places_of_worship_gdf() -> gpd.GeoDataFrame:
    places_of_worship_df = pd.read_csv("data/osm/nairobi_worship_places.csv")
    places_of_worship_gdf = gpd.GeoDataFrame(
        places_of_worship_df,
        geometry=gpd.points_from_xy(
            places_of_worship_df["lon"], places_of_worship_df["lat"]
        ),
        crs="EPSG:4326",
    )
    places_of_worship_gdf.reset_index(inplace=True)
    places_of_worship_gdf.rename(columns={"index": "ID"}, inplace=True)
    return places_of_worship_gdf


if __name__ == "__main__":
    places_of_worship_gdf = get_places_of_worship_gdf()
