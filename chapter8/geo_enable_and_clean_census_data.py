import geopandas as gpd
import pandas as pd


def clean_census_data(census_gpd: gpd.GeoDataFrame) -> None:
    census_gpd = census_gpd.rename(
        columns={
            "B01003_001E": "TotPop",
            "B25077_001E": "MedVal_OwnOccUnit",
            "B08013_001E": "TrvTimWrk",
            "B17013_002E": "PopBlwPovLvl",
        }
    )


def geo_enable_census_data() -> gpd.GeoDataFrame:
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
    return geo_enabled_ny_census_df


if __name__ == "__main__":
    geo_enabled_ny_census_df = geo_enable_census_data()
    clean_census_data(geo_enabled_ny_census_df)
