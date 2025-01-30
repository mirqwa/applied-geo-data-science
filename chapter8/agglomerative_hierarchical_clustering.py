import geopandas as gpd
import numpy as np

from sklearn.cluster import AgglomerativeClustering

import constants
import utils


np.random.seed(32)


def fit_model(ny_census: gpd.GeoDataFrame) -> None:
    model = AgglomerativeClustering(linkage="ward", n_clusters=5)
    model.fit(ny_census[constants.GEO_DEMO_RN])
    ny_census["ward5_label"] = model.labels_
    ward5sizes = ny_census.groupby("ward5_label").size()
    utils.plot_radial_plot(
        ny_census.groupby("ward5_label")[constants.GEO_DEMO_RN].mean()
    )


if __name__ == "__main__":
    ny_census = gpd.read_file("data/us_census/ny_census_transformed_and_scaled.geojson")
    fit_model(ny_census)
