import geopandas as gpd
import geoplot.crs as gcrs
import geoplot as gplt
import matplotlib.pyplot as plt
import pandas as pd


if __name__ == "__main__":
    listings = pd.read_csv("data/listings.csv.gz", compression="gzip")
    listings_sub = listings[
        [
            "id",
            "property_type",
            "neighbourhood_cleansed",
            "neighbourhood_group_cleansed",
            "beds",
            "bathrooms",
            "price",
            "latitude",
            "longitude",
        ]
    ]
    listings_sub["price"] = (
        listings_sub["price"].replace("[$,]", "", regex=True).astype(float)
    )

    listings_sub_gpd = gpd.GeoDataFrame(
        listings_sub,
        geometry=gpd.points_from_xy(
            listings_sub.longitude, listings_sub.latitude, crs=4326
        ),
    )

    boroughs = gpd.read_file("data/new_york/nybb.shp")
    boroughs = boroughs.to_crs(4326)

    ax = gplt.kdeplot(
        listings_sub_gpd,
        shade=True,
        cmap="Reds",
        clip=boroughs.geometry,
        projection=gcrs.WebMercator(),
    )
    gplt.polyplot(boroughs, ax=ax, zorder=1)

    plt.show()
