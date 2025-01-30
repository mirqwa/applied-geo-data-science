import geopandas as gpd
import numpy as np

from pysal.lib import weights
from libpysal.weights import Queen, KNN
from sklearn.cluster import AgglomerativeClustering

import constants
import utils


np.random.seed(32)


def fit_model(ny_census: gpd.GeoDataFrame, w: weights.weights = None) -> None:
    model = (
        AgglomerativeClustering(linkage="ward", connectivity=w.sparse, n_clusters=5)
        if w
        else AgglomerativeClustering(linkage="ward", n_clusters=5)
    )
    model.fit(ny_census[constants.GEO_DEMO_RN])
    ny_census["ward5_label"] = model.labels_
    ward5sizes = ny_census.groupby("ward5_label").size()
    utils.plot_clusters_choropleth(ny_census, "ward5_label", "Set3")
    utils.plot_radial_plot(
        ny_census.groupby("ward5_label")[constants.GEO_DEMO_RN].mean()
    )


if __name__ == "__main__":
    ny_census = gpd.read_file("data/us_census/ny_census_transformed_and_scaled.geojson")
    # fit_model(ny_census.copy())

    # spatially constrained clustering
    spatial_w = Queen.from_dataframe(ny_census)
    fit_model(ny_census.copy(), spatial_w)

    knn_spatial_w = KNN.from_dataframe(ny_census, k=10)
    fit_model(ny_census.copy(), knn_spatial_w)
