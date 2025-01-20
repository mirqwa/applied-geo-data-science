import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from pysal.explore import esda
from pysal.lib import weights
from splot.esda import plot_moran

import manual_spatial_correlation
import utils


def plot_moran_i(data: gpd.GeoDataFrame, value_column: str) -> None:
    f, ax = plt.subplots(1, figsize=(10, 10))
    sns.regplot(
        x=f"{value_column}_std",
        y=f"{value_column}_lag_std",
        ci=None,
        data=data,
        line_kws={"color": "r"},
    )
    ax.axvline(0, c="k", alpha=0.8)
    ax.axhline(0, c="k", alpha=0.8)
    ax.set_title(f"Moran Plot - NYC Airbnb {value_column}")
    ax.set_xlabel(f"Standardized {value_column}")
    ax.set_ylabel(f"Standardized {value_column} Lag")
    plt.show()


def calculate_and_plot_moran1(
    data: gpd.GeoDataFrame, variables: str, w: weights.weights
) -> None:
    for variable in variables:
        morans_stat = esda.moran.Moran(data[variable], w)
        plot_moran(morans_stat)
        plt.show()


def calculate_geary_c(
    data: gpd.GeoDataFrame, variables: str, w: weights.weights
) -> None:
    for variable in variables:
        geary_c = esda.geary.Geary(data[variable], w)
        print(f"Geary's C for {variable}: {geary_c.C}")
        print(f"p-value for for {variable}: {geary_c.p_sim}")


if __name__ == "__main__":
    data = utils.get_data()
    data, w = utils.calculate_weight_and_lag(data, "price")
    plot_moran_i(data, "price")
    data, _ = utils.calculate_weight_and_lag(data, "shuffled price")
    plot_moran_i(data, "shuffled price")
    calculate_and_plot_moran1(data, ["price", "shuffled price"], w)
    calculate_geary_c(data, ["price", "shuffled price"], w)

    # computing moran index manually
    price_moran_i = manual_spatial_correlation.compute_moran_index(data["price"], w)
    shuffled_price_moran_i = manual_spatial_correlation.compute_moran_index(
        data["shuffled price"], w
    )
    price_geary_c = manual_spatial_correlation.compute_geary_c(data["price"], w)
