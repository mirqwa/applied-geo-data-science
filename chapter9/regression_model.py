import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

from libpysal import weights
from pysal.model import spreg


def one_hot_encode_room_types(
    manhattan_listings_subset: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    manhattan_listings_subset["rt_entire_home_apartment"] = np.where(
        manhattan_listings_subset["room_type"] == "Entire home/apt", 1, 0
    )
    manhattan_listings_subset["rt_private_room"] = np.where(
        manhattan_listings_subset["room_type"] == "Private room", 1, 0
    )
    manhattan_listings_subset["rt_shared_room"] = np.where(
        manhattan_listings_subset["room_type"] == "Shared room", 1, 0
    )
    return manhattan_listings_subset


def format_price(manhattan_listings_subset: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    manhattan_listings_subset["price"] = manhattan_listings_subset["price"].str.replace(
        "$", ""
    )
    manhattan_listings_subset["price"] = manhattan_listings_subset["price"].str.replace(
        ",", ""
    )
    manhattan_listings_subset["price"] = manhattan_listings_subset["price"].astype(
        float
    )
    return manhattan_listings_subset


def drop_missing_values(
    manhattan_listings_subset: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    for column in ["bedrooms", "beds", "review_scores_rating", "price"]:
        manhattan_listings_subset = manhattan_listings_subset[
            manhattan_listings_subset[column].notna()
        ]
    return manhattan_listings_subset


def get_train_data() -> gpd.GeoDataFrame:
    manhattan_listings = gpd.read_file("data/output/new_york/manhattan_listings.geojson")
    variables = [
        "id",  # Unique identifier for the listing
        "room_type",  # Type of room
        "accommodates",  # The maximum capacity of the listing
        "bedrooms",  # The number of bedrooms
        "beds",  # The number of beds
        "review_scores_rating",  # The rating
        "price",  # The nightly rental rate, dependent variable (Y)
    ]
    manhattan_listings_subset = manhattan_listings[variables]
    manhattan_listings_subset = one_hot_encode_room_types(manhattan_listings_subset)
    manhattan_listings_subset = format_price(manhattan_listings_subset)
    manhattan_listings_subset["log_price"] = np.log(manhattan_listings_subset["price"])
    manhattan_listings_subset = drop_missing_values(manhattan_listings_subset)
    return manhattan_listings, manhattan_listings_subset


def build_regression_model(manhattan_listings: gpd.GeoDataFrame) -> spreg.OLS:
    m_vars = [
        "accommodates",
        "bedrooms",
        "beds",
        "review_scores_rating",
        "rt_entire_home_apartment",
        "rt_private_room",
        "rt_shared_room",
    ]
    ols_m = spreg.OLS(
        manhattan_listings[["log_price"]].values,
        manhattan_listings[m_vars].values,
        name_y="price",
        name_x=m_vars,
    )
    return ols_m


def get_average_neighborhood_residual(
    manhattan_listings: gpd.GeoDataFrame,
    manhattan_listings_subset: gpd.GeoDataFrame,
    ols_m: spreg.OLS,
) -> tuple:
    manhattan_listings_subset["ols_m_r"] = ols_m.u
    manhattan_listings_subset = manhattan_listings_subset.merge(
        manhattan_listings[["id", "neighbourhood_cleansed"]], how="left", on="id"
    )
    mean = (
        manhattan_listings_subset.groupby("neighbourhood_cleansed")
        .ols_m_r.mean()
        .to_frame("neighborhood_residual")
    )
    residuals_neighborhood = manhattan_listings_subset.merge(
        mean, how="left", left_on="neighbourhood_cleansed", right_index=True
    ).sort_values("neighborhood_residual")
    nyc_neighborhoods = gpd.read_file(
        "data/new_york/neighborhoods/ZillowNeighborhoods-NY.shp"
    )
    nyc_neighborhoods_residuals = nyc_neighborhoods.merge(
        mean, left_on="Name", right_on="neighbourhood_cleansed"
    )
    return residuals_neighborhood, nyc_neighborhoods_residuals


def plot_residuals_neighborhood(residuals_neighborhood: pd.DataFrame) -> None:
    fig = px.violin(
        residuals_neighborhood,
        x="neighbourhood_cleansed",
        y="ols_m_r",
        color="neighbourhood_cleansed",
    )
    fig.update_layout(xaxis_title="Neighborhood", yaxis_title="Residuals")
    fig.show()


def plot_residuals_choropleth(nyc_neighborhoods_residuals: gpd.GeoDataFrame) -> None:
    _, ax = plt.subplots(1, figsize=(10, 10))
    nyc_neighborhoods_residuals.plot(
        column="neighborhood_residual",
        cmap="vlag",
        scheme="quantiles",
        k=4,
        edgecolor="white",
        linewidth=0.1,
        alpha=0.75,
        legend=True,
        ax=ax,
    )
    cx.add_basemap(ax, crs=nyc_neighborhoods_residuals.crs)
    for _, row in nyc_neighborhoods_residuals.iterrows():
        plt.annotate(
            text=row["Name"],
            xy=tuple([row.geometry.centroid.x, row.geometry.centroid.y]),
            horizontalalignment="center",
            fontsize=8,
        )
    ax.set_axis_off()
    plt.show()


def plot_spatial_lag(
    residuals_neighborhood: pd.DataFrame,
    manhattan_listings: gpd.GeoDataFrame,
    ols_m: spreg.OLS,
) -> None:
    residuals_neighborhood = residuals_neighborhood.merge(
        manhattan_listings[["id", "geometry"]], how="left", on="id"
    )
    knn = weights.KNN.from_dataframe(residuals_neighborhood, k=5)
    lag_residual = weights.spatial_lag.lag_spatial(knn, ols_m.u)
    fig = px.scatter(
        x=ols_m.u.flatten(),
        y=lag_residual.flatten(),
        trendline="ols",
        width=800,
        height=800,
    )
    fig.update_layout(
        xaxis_title="Airbnb Residuals", yaxis_title="Spatially Lagged Residuals"
    )
    fig.show()


if __name__ == "__main__":
    manhattan_listings, manhattan_listings_subset = get_train_data()
    ols_m = build_regression_model(manhattan_listings_subset)
    (
        residuals_neighborhood,
        nyc_neighborhoods_residuals,
    ) = get_average_neighborhood_residual(
        manhattan_listings, manhattan_listings_subset, ols_m
    )
    plot_residuals_neighborhood(residuals_neighborhood)
    plot_residuals_choropleth(nyc_neighborhoods_residuals)
    plot_spatial_lag(residuals_neighborhood, manhattan_listings, ols_m)
