import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from esda.moran import Moran
from libpysal.weights import Queen

import constants


np.random.seed(32)


def plot_data(ny_census: gpd.GeoDataFrame) -> None:
    fig, axes = plt.subplots(nrows=5, ncols=2, layout="tight")
    axes = axes.flatten()
    # plt.rcParams["font.size"] = "40"
    for i, col in enumerate(constants.GEO_DEMO_RN):
        ax = axes[i]
        ny_census.plot(
            column=col,
            ax=ax,
            scheme="quantiles",
            linewidth=0,
            cmap="coolwarm",
            legend=True,
            legend_kwds={
                "loc": "center left",
                "bbox_to_anchor": (1, 0.5),
                "fmt": "{:.0f}",
            },
        )
        ax.set_axis_off()
        ax.set_title(col)
    plt.subplots_adjust(wspace=None, hspace=None)
    plt.show()


def calculate_moran_i(ny_census: gpd.GeoDataFrame) -> None:
    w = Queen.from_dataframe(ny_census)
    moransi_results = [Moran(ny_census[v], w) for v in constants.GEO_DEMO_RN]
    moransi_results = [
        (v, res.I, res.p_sim) for v, res in zip(constants.GEO_DEMO_RN, moransi_results)
    ]
    table = pd.DataFrame(
        moransi_results, columns=["GEODEMO Var", "Moran's I", "P-value"]
    ).set_index("GEODEMO Var")


def plot_pair_plots(ny_census: gpd.GeoDataFrame) -> None:
    selected_variables = ["PopBlwPovLvl", "UnempPop", "RetPopNoRetInc", "PopIncGT75"]
    sns.pairplot(ny_census[selected_variables], kind="reg", diag_kind="kde")
    plt.show()


if __name__ == "__main__":
    ny_census = gpd.read_file("data/us_census/ny_census_transformed.geojson")
    plot_data(ny_census)
    calculate_moran_i(ny_census)
    plot_pair_plots(ny_census)
