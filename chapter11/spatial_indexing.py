import time

import contextily as cx
import h3
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from shapely import Polygon


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
    manhattan_boroughs.reset_index(inplace=True)
    return manhattan_boroughs


def filter_without_spatial_indexing(
    listings_gdf: gpd.GeoDataFrame, manhattan_boroughs: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    start = time.time()
    mask = listings_gdf.within(manhattan_boroughs.loc[0, "geometry"])
    manhattan_listings_gdf = listings_gdf.loc[mask]
    end = time.time()
    print("Time take to filter without masking:", round(end - start, 2), "seconds")
    return manhattan_listings_gdf


def run_intersection(
    listings_gdf: gpd.GeoDataFrame, geometry: gpd.GeoSeries
) -> gpd.GeoDataFrame:
    sindex = listings_gdf.sindex
    start = time.time()
    idex_possible_matches = list(sindex.intersection(geometry.bounds.values[0]))
    possible_matches_df = listings_gdf.iloc[idex_possible_matches]
    manhattan_listings_gdf = possible_matches_df[
        possible_matches_df.intersects(geometry, align=True)
    ]
    end = time.time()
    print("Time take to filter with masking:", round(end - start, 2), "seconds")
    return manhattan_listings_gdf


def filter_with_spatial_indexing(
    listings_gdf: gpd.GeoDataFrame, manhattan_boroughs: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    geometry = manhattan_boroughs.geometry
    manhattan_listings_gdf = run_intersection(listings_gdf, geometry)
    return manhattan_listings_gdf


def add_h3_id(row):
    h3_resolution = 8
    return h3.latlng_to_cell(row.geometry.y, row.geometry.x, h3_resolution)


def add_h3_geometry(row):
    points = h3.cell_to_boundary(row["h3"])
    return Polygon(points)


def plot_airbnbs_choropleth(gdf: gpd.GeoDataFrame) -> None:
    _, ax = plt.subplots(1, figsize=(15, 15))
    gdf_wm = gdf.to_crs(epsg=3857)
    gdf_wm.plot(
        ax=ax,
        column="count",
        cmap="coolwarm",
        scheme="quantiles",
        k=4,
        edgecolor="white",
        linewidth=0.1,
        alpha=0.5,
        legend=True,
    )
    cx.add_basemap(ax, crs=gdf_wm.crs, zoom=12)
    plt.show()


def h3_indexing(listings_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    listings_gdf["h3"] = listings_gdf.apply(add_h3_id, axis=1)
    airbnb_count = (
        listings_gdf.groupby(["h3"]).h3.agg("count").to_frame("count").reset_index()
    )
    airbnb_count["geometry"] = airbnb_count.apply(add_h3_geometry, axis=1)
    gdf = gpd.GeoDataFrame(airbnb_count, crs="EPSG:4326")
    plot_airbnbs_choropleth(gdf)


if __name__ == "__main__":
    listings_gdf = get_listings()
    manhattan_boroughs = get_manhattan_boroughs()
    manhattan_listings_gdf1 = filter_without_spatial_indexing(
        listings_gdf, manhattan_boroughs
    )
    listings_gdf.index = [0 for _ in range(37548)]
    manhattan_listings_gdf2 = filter_with_spatial_indexing(
        listings_gdf, manhattan_boroughs
    )
    h3_indexing(manhattan_listings_gdf1)
