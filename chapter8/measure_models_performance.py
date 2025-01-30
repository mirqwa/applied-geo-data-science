import geopandas as gpd
import pandas as pd

from libpysal.weights import Queen, KNN
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)

import constants
from k_means_clustering import fit_model as fit_k_means_model
from agglomerative_hierarchical_clustering import fit_model as fit_ahc_model


def fit_models() -> gpd.GeoDataFrame:
    ny_census = gpd.read_file("data/us_census/ny_census_transformed_and_scaled.geojson")
    ny_census = fit_k_means_model(ny_census)
    ny_census = fit_ahc_model(ny_census, "ward5_label")
    spatial_w = Queen.from_dataframe(ny_census)
    ny_census = fit_ahc_model(ny_census, "ward5wgt_label", spatial_w)
    knn_spatial_w = KNN.from_dataframe(ny_census, k=10)
    ny_census = fit_ahc_model(ny_census, "ward5_knnwgt_label", knn_spatial_w)
    return ny_census


def get_performance_values(ny_census: gpd.GeoDataFrame) -> None:
    ch_scores = []
    db_scores = []
    s_scores = []
    for model in (
        "kmeans_5_label",
        "ward5_label",
        "ward5wgt_label",
        "ward5_knnwgt_label",
    ):
        ch_score = calinski_harabasz_score(
            ny_census[constants.GEO_DEMO_RN],
            ny_census[model],
        )
        ch_scores.append((model, ch_score))
        # compute the DB score
        db_score = davies_bouldin_score(
            ny_census[constants.GEO_DEMO_RN],
            ny_census[model],
        )
        db_scores.append((model, db_score))
        # compute the silhouette score
        s_score = silhouette_score(
            ny_census[constants.GEO_DEMO_RN],
            ny_census[model],
        )
        s_scores.append((model, s_score))
    ch_df = pd.DataFrame(ch_scores, columns=["model", "CH score"]).set_index("model")
    db_df = pd.DataFrame(db_scores, columns=["model", "DB score"]).set_index("model")
    s_df = pd.DataFrame(s_scores, columns=["model", "Silhouettescore"]).set_index(
        "model"
    )
    scores_df = ch_df.merge(db_df, on="model")
    scores_df = scores_df.merge(s_df, on="model")


if __name__ == "__main__":
    ny_census = fit_models()
    get_performance_values(ny_census)
