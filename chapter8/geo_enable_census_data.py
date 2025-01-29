import geopandas as gpd
import pandas as pd


def geo_enable_census_data() -> None:
    ny_tract = gpd.read_file("data/tiger/tl_2019_36_tract.zip")
    ny_tract = ny_tract.to_crs(epsg=2263)
    ny_census_df = pd.read_csv("data/us_census/ny_census.csv")
    ny_census_df["GEOID"] = (
        ny_census_df["state"].astype(str)
        + ny_census_df["county"].astype(str)
        + ny_census_df["tract"].astype(str)
    )
    ny_census_df = ny_census_df.drop(columns=["state", "county", "tract"])
    geo_enabled_ny_census_df = ny_tract.merge(ny_census_df, on="GEOID")


if __name__ == "__main__":
    geo_enable_census_data()
