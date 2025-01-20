import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pysal.explore import esda
from pysal.lib import weights
from splot import esda as esdaplot

import manual_spatial_correlation
import utils


def kde_plot(price_lisa) -> None:
    _, ax = plt.subplots(1, figsize=(10, 10))
    sns.kdeplot(price_lisa, ax=ax)
    plt.show()


def plot_choropleth(data: gpd.GeoDataFrame, price_lisa) -> None:
    data_copy = data.copy()
    _, ax = plt.subplots(1, figsize=(10, 10))
    data_copy.assign(ML_Is=price_lisa).plot(
        column="ML_Is",
        cmap="vlag",
        scheme="quantiles",
        k=4,
        edgecolor="white",
        linewidth=0.1,
        alpha=0.75,
        legend=True,
        ax=ax,
    )
    plt.show()


def plot_choropleth_with_quadrant_classes(data, price_lisa, p=1) -> None:
    _, ax = plt.subplots(1, figsize=(10, 10))
    esdaplot.lisa_cluster(price_lisa, data, p=p, ax=ax)
    plt.show()


def plot_choropleth_with_signicance(data: gpd.GeoDataFrame, price_lisa) -> None:
    _, ax = plt.subplots(1, figsize=(10, 10))
    alpha = 0.05
    labels = pd.Series(1 * (price_lisa.p_sim < alpha), index=data.index).map(
        {1: "Significant", 0: "Insignificant"}
    )
    data.assign(ML_Sig=labels).plot(
        column="ML_Sig",
        categorical=True,
        k=2,
        cmap="vlag",
        linewidth=0.1,
        edgecolor="white",
        legend=True,
        ax=ax,
    )
    plt.show()


def plot_local_moran(data: gpd.GeoDataFrame, price_lisa, manual_price_lisa) -> None:
    kde_plot(price_lisa.Is)
    kde_plot(manual_price_lisa)
    plot_choropleth(data, price_lisa.Is)
    plot_choropleth(data, manual_price_lisa)
    plot_choropleth_with_quadrant_classes(data, price_lisa)
    plot_choropleth_with_signicance(data, price_lisa)
    plot_choropleth_with_quadrant_classes(data, price_lisa, 0.05)


if __name__ == "__main__":
    data = utils.get_data()
    data, w = utils.calculate_weight_and_lag(data, "price")
    price_lisa = esda.moran.Moran_Local(data["price"], w)
    manual_price_lisa = manual_spatial_correlation.compute_local_moran_index(
        data["price"], w
    )
    plot_local_moran(data, price_lisa, manual_price_lisa)
