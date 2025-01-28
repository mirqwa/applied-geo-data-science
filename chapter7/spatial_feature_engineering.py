import geopandas as gpd
import pandas as pd


def get_gdf(csv_path: str) -> gpd.GeoDataFrame:
    df = pd.read_csv(csv_path)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df["lon"], df["lat"]
        ),
        crs="EPSG:4326",
    )
    gdf.reset_index(inplace=True)
    gdf.rename(columns={"index": "ID"}, inplace=True)
    return gdf


def get_counts_of_nearest_places_of_worship(
    places_of_worship_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    places_of_worship_gdf = places_of_worship_gdf.to_crs(3005)
    buffer_size = 500  # 500 metres
    places_of_worship_gdf_buffer = places_of_worship_gdf.copy()
    places_of_worship_gdf_buffer["buffer_500m"] = places_of_worship_gdf_buffer.buffer(
        buffer_size
    )
    joined = gpd.sjoin(
        places_of_worship_gdf,
        places_of_worship_gdf_buffer.set_geometry("buffer_500m")[["ID", "buffer_500m"]],
        predicate="within",
    )
    counts_gdf = joined.groupby("ID_left").count().reset_index()
    counts_gdf = counts_gdf[["ID_left", "ID_right"]]
    counts_gdf.columns = ["ID", "neighbouring_places_fo_worship_count"]
    return counts_gdf


if __name__ == "__main__":
    places_of_worship_gdf = get_gdf("data/osm/nairobi_worship_places.csv")
    places_of_worship_counts_gdf = get_counts_of_nearest_places_of_worship(
        places_of_worship_gdf
    )
    places_of_worship_gdf = pd.merge(
        places_of_worship_gdf, places_of_worship_counts_gdf, on="ID", how="inner"
    )
