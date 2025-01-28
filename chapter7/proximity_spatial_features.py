import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def plot_manhattan_listings(manhattan_listings: gpd.GeoDataFrame) -> None:
    manhattan_listings_wm = manhattan_listings.to_crs(epsg=3857)
    ax = manhattan_listings_wm.plot(figsize=(10, 10), alpha=0.5, edgecolor="k")
    cx.add_basemap(ax, crs=manhattan_listings_wm.crs, zoom=12)
    ax.set_axis_off()
    plt.show()


def get_gdf_from_csv(csv_path: str) -> gpd.GeoDataFrame:
    df = pd.read_csv(csv_path)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326",
    )
    return gdf


def get_manhattan() -> gpd.GeoDataFrame:
    boroughs = gpd.read_file("data/new_york/nybb.shp")
    manhattan = boroughs[boroughs["BoroName"] == "Manhattan"]
    manhattan = manhattan.to_crs("EPSG:4326")
    return manhattan


def get_manhattan_listings() -> gpd.GeoDataFrame:
    listings_gdf = get_gdf_from_csv("data/listings.csv.gz")
    manhattan = get_manhattan()
    listings_mask = listings_gdf.within(manhattan.loc[3, "geometry"])
    manhattan_listings = listings_gdf.loc[listings_mask]
    return manhattan_listings


if __name__ == "__main__":
    manhattan_listings = get_manhattan_listings()
    nyc_attractions = get_gdf_from_csv("data/new_york/nyc_attactions.csv")
    plot_manhattan_listings(manhattan_listings)
