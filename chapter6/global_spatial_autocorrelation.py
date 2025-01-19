import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statistics
from pysal.lib import weights


def get_listings_df() -> gpd.GeoDataFrame:
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

    return listings_sub_gpd


def get_gdf_without_outliers(NY_Tracts_Agg: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    mean_price = statistics.mean(NY_Tracts_Agg["price"].dropna())
    stdev = statistics.stdev(NY_Tracts_Agg["price"].dropna())
    NY_Tracts_Agg_without_outliers = NY_Tracts_Agg[
        NY_Tracts_Agg["price"] < mean_price + stdev
    ]
    return NY_Tracts_Agg_without_outliers


def get_data() -> gpd.GeoDataFrame:
    NY_tracts_path = "data/tiger/tl_2021_36_tract.zip"
    NY_Tracts = gpd.read_file(NY_tracts_path)
    NY_Tracts = NY_Tracts.to_crs(4326)

    cbsa_path = "data/tiger/tl_2021_us_cbsa.zip"
    cbsas = gpd.read_file(cbsa_path)
    NY_cbsa = cbsas[cbsas["GEOID"] == "35620"]

    mask = NY_Tracts.intersects(NY_cbsa.loc[620, "geometry"])
    NY_Tracts_subset = NY_Tracts.loc[mask]

    listings_sub_gpd = get_listings_df()
    NY_Tracts_sj = gpd.sjoin(
        NY_Tracts_subset, listings_sub_gpd, how="left", op="contains"
    )
    NY_Tracts_sj = NY_Tracts_sj[["GEOID", "price", "geometry"]]
    NY_Tracts_Agg = NY_Tracts_sj.dissolve(by="GEOID", aggfunc="mean")
    NY_Tracts_Agg = NY_Tracts_Agg[NY_Tracts_Agg.geom_type != "MultiPolygon"]
    NY_Tracts_Agg_without_outliers = get_gdf_without_outliers(NY_Tracts_Agg)

    return NY_Tracts_Agg_without_outliers


def calculate_weight_and_lag(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    w = weights.Queen.from_dataframe(data)
    w.transform = "R"
    data["price_lag"] = weights.spatial_lag.lag_spatial(w, data["price"])
    data["price_std"] = data["price"] - data["price"].mean()
    data["price_lag_std"] = data["price_lag"] - data["price_lag"].mean()
    return data


def plot_moran_i(data: gpd.GeoDataFrame) -> None:
    f, ax = plt.subplots(1, figsize=(10, 10))
    sns.regplot(
        x="price_std", y="price_lag_std", ci=None, data=data, line_kws={"color": "r"}
    )
    ax.axvline(0, c="k", alpha=0.8)
    ax.axhline(0, c="k", alpha=0.8)
    ax.set_title("Moran Plot - NYC Airbnb Price")
    ax.set_xlabel("Standardized Price")
    ax.set_ylabel("Standardized Price Lag")
    plt.show()


if __name__ == "__main__":
    data = calculate_weight_and_lag(get_data())
    plot_moran_i(data)
