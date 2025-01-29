import geopandas as gpd
import matplotlib.pyplot as plt

import constants


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


if __name__ == "__main__":
    ny_census = gpd.read_file("data/us_census/ny_census_transformed.geojson")
    plot_data(ny_census)
