import geopandas as gpd

import constants


if __name__ == "__main__":
    ny_census = gpd.read_file("data/us_census/ny_census_transformed.geojson")
