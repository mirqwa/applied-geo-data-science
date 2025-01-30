import geopandas as gpd
import numpy as np

from pysal.lib import weights
from libpysal.weights import Queen, KNN
from sklearn.cluster import AgglomerativeClustering

import constants
import utils


np.random.seed(32)


def fit_model(
    ny_census: gpd.GeoDataFrame, label_column_name: str, w: weights.weights = None
) -> gpd.GeoDataFrame:
    model = (
        AgglomerativeClustering(linkage="ward", connectivity=w.sparse, n_clusters=5)
        if w
        else AgglomerativeClustering(linkage="ward", n_clusters=5)
    )
    model.fit(ny_census[constants.GEO_DEMO_RN])
    ny_census[label_column_name] = model.labels_
    return ny_census


def fit_model_and_plot_clusters(
    ny_census: gpd.GeoDataFrame, label_column_name: str, w: weights.weights = None
) -> None:
    ny_census = fit_model(ny_census, label_column_name, w)
    ward5sizes = ny_census.groupby(label_column_name).size()
    utils.plot_clusters_choropleth(ny_census, label_column_name, "Set3")
    utils.plot_radial_plot(
        ny_census.groupby(label_column_name)[constants.GEO_DEMO_RN].mean()
    )


if __name__ == "__main__":
    ny_census = gpd.read_file("data/us_census/ny_census_transformed_and_scaled.geojson")
    fit_model_and_plot_clusters(ny_census, "ward5_label")

    # spatially constrained clustering
    spatial_w = Queen.from_dataframe(ny_census)
    fit_model_and_plot_clusters(ny_census, "ward5wgt_label", spatial_w)

    knn_spatial_w = KNN.from_dataframe(ny_census, k=10)
    fit_model_and_plot_clusters(ny_census, "ward5_knnwgt_label", knn_spatial_w)
