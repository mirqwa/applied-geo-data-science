import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from sklearn.cluster import KMeans

import constants
import utils


np.random.seed(0)


def get_and_plot_distortion(ny_census: gpd.GeoDataFrame) -> None:
    distortions = []
    K = range(1, 15)
    ny_census.dropna(inplace=True)
    for k in K:
        # Instantiating the model
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(ny_census[constants.GEO_DEMO_RN])
        distortions.append(kmeans.inertia_)
    plt.figure(figsize=(16, 10))
    plt.plot(K, distortions, "bx-")
    plt.xlabel("k")
    plt.ylabel("Distortion")
    plt.title("Elbow Method for optimal k")
    plt.show()


def calculate_tract_average_areas(ny_census: gpd.GeoDataFrame) -> None:
    # area in km squared
    k5distr = ny_census.groupby("kmeans_5_label").size()
    ny_census["area"] = (ny_census.geometry.area) * 9.2903e-8
    area = ny_census.dissolve(by="kmeans_5_label", aggfunc="sum")["area"]
    tract_area = pd.DataFrame({"Num. Tracts": k5distr, "Area": area})
    tract_area["Area_per_tract"] = tract_area["Area"] / tract_area["Num. Tracts"]
    tract_area.reset_index(inplace=True)
    _ = tract_area.plot.bar(x="kmeans_5_label", y="Area_per_tract")
    plt.show()


def fit_model(ny_census: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    kmeans = KMeans(n_clusters=5)
    kmeans_5 = kmeans.fit(ny_census[constants.GEO_DEMO_RN])
    ny_census["kmeans_5_label"] = kmeans_5.labels_
    return ny_census


def get_and_plot_clusters(ny_census: gpd.GeoDataFrame) -> None:
    ny_census = fit_model(ny_census)
    utils.plot_clusters_choropleth(ny_census, "kmeans_5_label", "Set2")
    calculate_tract_average_areas(ny_census)
    utils.plot_radial_plot(
        ny_census.groupby("kmeans_5_label")[constants.GEO_DEMO_RN].mean()
    )


if __name__ == "__main__":
    ny_census = gpd.read_file("data/us_census/ny_census_transformed_and_scaled.geojson")
    get_and_plot_distortion(ny_census)
    get_and_plot_clusters(ny_census)
