import warnings

import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

from libpysal import weights
from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW
from pysal.model import spreg


warnings.filterwarnings("ignore")

M_VARS = [
    "accommodates",
    "bedrooms",
    "beds",
    "review_scores_rating",
    "rt_entire_home_apartment",
    "rt_private_room",
    "rt_shared_room",
]
G_VARS = [
    "Central Park",
    "Central Park Zoo",
    "Empire State Building",
    "Statue of Liberty",
    "Rockeffeller Center",
    "Chrysler Building",
    "Times Square",
    "MoMa",
    "Charging Bull",
]
G_M_VARS = G_VARS + M_VARS


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
    manhattan_listings_subset: gpd.GeoDataFrame, columns: list
) -> gpd.GeoDataFrame:
    for column in columns:
        manhattan_listings_subset = manhattan_listings_subset[
            manhattan_listings_subset[column].notna()
        ]
    return manhattan_listings_subset


def get_train_data() -> gpd.GeoDataFrame:
    manhattan_listings = gpd.read_file(
        "data/output/new_york/manhattan_listings.geojson"
    )
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
    manhattan_listings_subset = drop_missing_values(
        manhattan_listings_subset, ["bedrooms", "beds", "review_scores_rating", "price"]
    )
    return manhattan_listings, manhattan_listings_subset


def build_spatially_fixed_effects_regression_model(
    manhattan_listings: gpd.GeoDataFrame, variables: str
) -> spreg.OLS_Regimes:
    sfe_m = spreg.OLS_Regimes(
        manhattan_listings[["log_price"]].values,
        manhattan_listings[variables].values,
        manhattan_listings["neighbourhood_cleansed"].tolist(),
        constant_regi="many",
        cols2regi=[False] * len(variables),
        regime_err_sep=False,
        name_y="log_price",
        name_x=variables,
    )
    return sfe_m


def build_ols_model(manhattan_listings: gpd.GeoDataFrame, variables: str) -> spreg.OLS:
    ols_m = spreg.OLS(
        manhattan_listings[["log_price"]].values,
        manhattan_listings[variables].values,
        name_y="price",
        name_x=variables,
    )
    return ols_m


def get_average_neighborhood_residual(
    manhattan_listings: gpd.GeoDataFrame,
    manhattan_listings_subset: gpd.GeoDataFrame,
    model: spreg.OLS,
) -> tuple:
    manhattan_listings_subset["model_residual"] = model.u
    if "neighbourhood_cleansed" not in manhattan_listings_subset.columns:
        manhattan_listings_subset = manhattan_listings_subset.merge(
            manhattan_listings[["id", "neighbourhood_cleansed"]], how="left", on="id"
        )
    mean = (
        manhattan_listings_subset.groupby("neighbourhood_cleansed")
        .model_residual.mean()
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
        y="model_residual",
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
    model: spreg.OLS,
) -> None:
    residuals_neighborhood = residuals_neighborhood.merge(
        manhattan_listings[["id", "geometry"]], how="left", on="id"
    )
    knn = weights.KNN.from_dataframe(residuals_neighborhood, k=5)
    lag_residual = weights.spatial_lag.lag_spatial(knn, model.u)
    fig = px.scatter(
        x=model.u.flatten(),
        y=lag_residual.flatten(),
        trendline="ols",
        width=800,
        height=800,
    )
    fig.update_layout(
        xaxis_title="Airbnb Residuals", yaxis_title="Spatially Lagged Residuals"
    )
    fig.show()


def build_model_and_plot(
    manhattan_listings_subset: pd.DataFrame,
    manhattan_listings: gpd.GeoDataFrame,
    variables: str,
    spatial_fixed_model: bool = False,
) -> None:
    model = (
        build_spatially_fixed_effects_regression_model(
            manhattan_listings_subset, variables
        )
        if spatial_fixed_model
        else build_ols_model(manhattan_listings_subset, variables)
    )
    print(model.summary)
    (
        residuals_neighborhood,
        nyc_neighborhoods_residuals,
    ) = get_average_neighborhood_residual(
        manhattan_listings, manhattan_listings_subset, model
    )
    plot_residuals_neighborhood(residuals_neighborhood)
    plot_residuals_choropleth(nyc_neighborhoods_residuals)
    plot_spatial_lag(residuals_neighborhood, manhattan_listings, model)


def get_data_for_gwr(manhattan_listings: gpd.GeoDataFrame) -> tuple:
    manhattan_listings = drop_missing_values(
        manhattan_listings,
        ["accommodates", "bedrooms", "beds", "review_scores_rating", "price"],
    )
    exp_vars = manhattan_listings[
        ["accommodates", "bedrooms", "beds", "review_scores_rating"]
    ].values
    manhattan_listings = format_price(manhattan_listings)
    manhattan_listings["log_price"] = np.log(manhattan_listings["price"])
    y = (manhattan_listings["log_price"].values).reshape((-1, 1))
    coords = list(zip(manhattan_listings.geometry.x, manhattan_listings.geometry.y))
    return exp_vars, y, coords


def build_geographical_weigted_regression_model(
    exp_vars: np.array,
    y: np.array,
    coords: list,
) -> None:
    gwr_selector = Sel_BW(coords, y, exp_vars, spherical=True)
    gwr_bw = gwr_selector.search(bw_min=2)
    gwr_results = GWR(coords, y, exp_vars, gwr_bw).fit()


def build_geographical_multi_weigted_regression_model(
    exp_vars: np.array,
    y: np.array,
    coords: list,
) -> None:
    selector = Sel_BW(coords, y, exp_vars, multi=True, spherical=True)
    selector.search(multi_bw_min=[4])
    mgwr_results = MGWR(coords, y, exp_vars, selector, sigma2_v1=True).fit()


if __name__ == "__main__":
    manhattan_listings, manhattan_listings_subset = get_train_data()
    build_model_and_plot(manhattan_listings_subset.copy(), manhattan_listings, M_VARS)

    manhattan_listings_subset = manhattan_listings_subset.merge(
        manhattan_listings[
            [
                "id",
                "Central Park",
                "Central Park Zoo",
                "Empire State Building",
                "Statue of Liberty",
                "Rockeffeller Center",
                "Chrysler Building",
                "Times Square",
                "MoMa",
                "Charging Bull",
            ]
        ],
        how="left",
        on="id",
    )
    build_model_and_plot(manhattan_listings_subset.copy(), manhattan_listings, G_M_VARS)

    manhattan_listings_subset = manhattan_listings_subset.merge(
        manhattan_listings[["id", "neighbourhood_cleansed"]], how="left", on="id"
    )
    build_model_and_plot(
        manhattan_listings_subset.copy(), manhattan_listings, G_M_VARS, True
    )

    exp_vars, y, coords = get_data_for_gwr(manhattan_listings.copy())

    build_geographical_weigted_regression_model(exp_vars, y, coords)

    # build_geographical_multi_weigted_regression_model(exp_vars, y, coords)
