import geopandas as gpd

from libpysal.weights import Queen, KNN

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


if __name__ == "__main__":
    ny_census = fit_models()
