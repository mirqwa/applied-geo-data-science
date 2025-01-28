import geopandas as gpd
import pandas as pd


def get_gdf(csv_path: str) -> gpd.GeoDataFrame:
    df = pd.read_csv(csv_path)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326",
    )
    gdf.reset_index(inplace=True)
    gdf.rename(columns={"index": "ID"}, inplace=True)
    return gdf


def get_counts_of_nearest_places_of_worship(
    left_gdf: gpd.GeoDataFrame,
    right_gdf: gpd.GeoDataFrame,
    count_column_name: str,
) -> gpd.GeoDataFrame:
    left_gdf = left_gdf.to_crs(3005)
    right_gdf = right_gdf.to_crs(3005)
    buffer_size = 500  # 500 metres
    right_gdf["buffer_500m"] = right_gdf.buffer(buffer_size)
    joined = gpd.sjoin(
        left_gdf,
        right_gdf.set_geometry("buffer_500m")[["ID", "buffer_500m"]],
        predicate="within",
    )
    counts_gdf = joined.groupby("ID_left").count().reset_index()
    counts_gdf = counts_gdf[["ID_left", "ID_right"]]
    counts_gdf.columns = ["ID", count_column_name]
    return counts_gdf


if __name__ == "__main__":
    places_of_worship_gdf = get_gdf("data/osm/nairobi_worship_places.csv")
    banks_gdf = get_gdf("data/osm/nairobi_banks.csv")
    places_of_worship_counts_gdf = get_counts_of_nearest_places_of_worship(
        places_of_worship_gdf,
        places_of_worship_gdf.copy(),
        "neighbouring_places_fo_worship_count",
    )
    places_of_worship_gdf = pd.merge(
        places_of_worship_gdf, places_of_worship_counts_gdf, on="ID", how="inner"
    )
