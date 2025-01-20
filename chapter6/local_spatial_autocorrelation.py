import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from pysal.explore import esda
from pysal.lib import weights

import utils


def kde_plot(price_lisa) -> None:
    _, ax = plt.subplots(1, figsize=(10, 10))
    sns.kdeplot(price_lisa.Is, ax=ax)
    plt.show()


def plot_choropleth(data: gpd.GeoDataFrame, price_lisa) -> None:
    _, ax = plt.subplots(1, figsize=(10, 10))
    data.assign(ML_Is=price_lisa.Is).plot(
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


def compute_and_plot_local_moran(y: gpd.GeoDataFrame, w: weights.weights) -> None:
    price_lisa = esda.moran.Moran_Local(y, w)
    kde_plot(price_lisa)
    plot_choropleth(data, price_lisa)


if __name__ == "__main__":
    data = utils.get_data()
    data, w = utils.calculate_weight_and_lag(data, "price")
    compute_and_plot_local_moran(data["price"], w)
