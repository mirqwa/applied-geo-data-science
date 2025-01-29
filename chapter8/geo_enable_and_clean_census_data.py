import geopandas as gpd
import pandas as pd

import constants


def clean_census_data(census_gpd: gpd.GeoDataFrame) -> None:
    census_gpd = census_gpd.rename(
        columns={
            "B01003_001E": "TotPop",  # "Total Population"
            "B25026_001E": "TotPopOccUnits",  # "Total population in occupied housing units"
            "B25008_002E": "TotNumOwnOccUnit",  # "Total number of owner occupied units"
            "B25008_003E": "TotNumRentOccUnit",  # "Total number of renter occupied units"
            "B06010_011E": "PopIncGT75",  # "Population with income of 75000 or more"
            "B28007_009E": "UnempPop",  # "Population in labor force and unemployed"
            "B19059_002E": "RetPop",  # "Population that is retired with retirement income"
            "B19059_003E": "RetPopNoRetInc",  # "Retired without retirement income"
            "B08013_001E": "TrvTimWrk",  # "Travel time to work in minutes"
            "B17013_002E": "PopBlwPovLvl",  # "Population with income below poverty level in past 12 months"
        }
    )
    census_gpd = census_gpd[constants.GEO_DEMO_RN + ["geometry"]]
    census_gpd = census_gpd[census_gpd["TotPop"] > 0]
    census_gpd.reset_index(inplace=True)
    census_gpd.to_csv("data/us_census/ny_census_transformed.csv", index=False)


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
