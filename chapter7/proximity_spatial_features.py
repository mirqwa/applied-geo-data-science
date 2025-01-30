import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def plot_manhattan_listings_and_attactions(
    manhattan_listings: gpd.GeoDataFrame, attractions: gpd.GeoDataFrame
) -> None:
    _, ax = plt.subplots(figsize=(15, 15))
    manhattan_listings_wm = manhattan_listings.to_crs(epsg=3857)
    manhattan_listings_wm.plot(ax=ax, alpha=0.5, edgecolor="k")
    attractions_wm = attractions.to_crs(epsg=3857)
    attractions_wm.plot(ax=ax, alpha=0.5, color="red", edgecolor="k")
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
    # saving this, to be used in chapter 9
    manhattan_listings.to_file(
        "data/new_york/manhattan_listings.geojson", driver="GeoJSON"
    )
    return manhattan_listings


def get_distances_to_attactions(
    manhattan_listings: gpd.GeoDataFrame, nyc_attractions: gpd.GeoDataFrame
) -> None:
    attractions = nyc_attractions.attaction.unique()
    nyc_attractions_p = nyc_attractions.to_crs("EPSG:2263")
    manhattan_listings_p = manhattan_listings.to_crs("EPSG:2263")
    distances = manhattan_listings_p.geometry.apply(
        lambda g: nyc_attractions_p.distance(g)
    )
    distances.columns = attractions
    # convert feet to kilometers
    distances = distances.apply(lambda x: x / 3280.84, axis=1)
    distances_1km = distances.apply(lambda x: x <= 1, axis=1).sum(axis=1)
    distances_2km = distances.apply(lambda x: x <= 2, axis=1).sum(axis=1)
    distances_3km = distances.apply(lambda x: x <= 3, axis=1).sum(axis=1)
    distances_4km = distances.apply(lambda x: x <= 4, axis=1).sum(axis=1)
    distances_5km = distances.apply(lambda x: x <= 5, axis=1).sum(axis=1)
    distances_df = pd.concat(
        [distances_1km, distances_2km, distances_3km, distances_4km, distances_5km],
        axis=1,
    )
    distances_df.columns = [
        "Attractions 1KM",
        "Attractions 2KM",
        "Attractions 3KM",
        "Attractions 4KM",
        "Attractions 5KM",
    ]
    manhattan_listings = manhattan_listings.merge(
        distances, left_index=True, right_index=True
    )
    manhattan_listings = manhattan_listings.merge(
        distances_df, left_index=True, right_index=True
    )
    manhattan_listings.to_csv(
        "data/output/new_york/manhattan_listings.csv", index=False
    )


if __name__ == "__main__":
    manhattan_listings = get_manhattan_listings()
    nyc_attractions = get_gdf_from_csv("data/new_york/nyc_attactions.csv")
    get_distances_to_attactions(manhattan_listings, nyc_attractions)
    plot_manhattan_listings_and_attactions(manhattan_listings, nyc_attractions)
