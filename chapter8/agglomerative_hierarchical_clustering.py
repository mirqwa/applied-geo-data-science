import geopandas as gpd
import numpy as np

from sklearn.cluster import AgglomerativeClustering

import constants


np.random.seed(32)


def fit_model(ny_census: gpd.GeoDataFrame) -> None:
    model = AgglomerativeClustering(linkage="ward", n_clusters=5)
    model.fit(ny_census[constants.GEO_DEMO_RN])
    ny_census["ward5_label"] = model.labels_


if __name__ == "__main__":
    ny_census = gpd.read_file("data/us_census/ny_census_transformed_and_scaled.geojson")
    fit_model(ny_census)
