import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def plot_places_of_worship(places_of_worship_gdf: gpd.GeoDataFrame) -> None:
    places_of_worship_wm = places_of_worship_gdf.to_crs(epsg=3857)
    ax = places_of_worship_wm.plot(figsize=(10, 10), alpha=0.5, edgecolor="k")
    cx.add_basemap(ax, crs=places_of_worship_wm.crs, zoom=12)
    ax.set_axis_off()
    plt.show()


def get_places_of_worship_gdf() -> gpd.GeoDataFrame:
    places_of_worship_df = pd.read_csv("data/osm/nairobi_worship_places.csv")
    places_of_worship_gdf = gpd.GeoDataFrame(
        places_of_worship_df,
        geometry=gpd.points_from_xy(places_of_worship_df.lon, places_of_worship_df.lat),
        crs="EPSG:4326",
    )
    return places_of_worship_gdf


if __name__ == "__main__":
    places_of_worship_gdf = get_places_of_worship_gdf()
    plot_places_of_worship(places_of_worship_gdf)
