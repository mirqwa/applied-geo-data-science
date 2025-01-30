import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from esda.moran import Moran
from libpysal.weights import Queen
from sklearn.preprocessing import robust_scale

import constants


np.random.seed(32)


def plot_data(ny_census: gpd.GeoDataFrame) -> None:
    _, axes = plt.subplots(nrows=7, ncols=3, layout="tight")
    axes = axes.flatten()
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
    selected_variables = ["TotNumRentOccUnit", "PopGrad", "UnempPop", "PopBlwPovLvl"]
    sns.pairplot(ny_census[selected_variables], kind="reg", diag_kind="kde")
    plt.show()


def plot_correlation_heatmap(ny_census: gpd.GeoDataFrame) -> None:
    plt.figure(figsize=(16, 12))
    plt.rcParams["font.size"] = "10"
    mask = np.triu(
        np.ones_like(ny_census[constants.GEO_DEMO_RN].corr(), dtype=np.bool_)
    )
    heatmap = sns.heatmap(
        ny_census[constants.GEO_DEMO_RN].corr(),
        mask=mask,
        vmin=-1,
        vmax=1,
        annot=True,
        cmap="coolwarm",
    )
    heatmap.set_title(
        "ACS Variable Correlation Heatmap", fontdict={"fontsize": 18}, pad=16
    )
    plt.show()


def scale_data(ny_census: gpd.GeoDataFrame) -> None:
    scaled_variables = robust_scale(ny_census[constants.GEO_DEMO_RN])
    ny_census[constants.GEO_DEMO_RN] = scaled_variables
    ny_census.to_file(
        "data/us_census/ny_census_transformed_and_scaled.geojson", driver="GeoJSON"
    )


if __name__ == "__main__":
    ny_census = gpd.read_file("data/us_census/ny_census_transformed.geojson")
    plot_data(ny_census)
    calculate_moran_i(ny_census)
    plot_pair_plots(ny_census)
    plot_correlation_heatmap(ny_census)
    scale_data(ny_census)
