import geopandas as gpd
import numpy as np
import pandas as pd

import constants


def clean_census_data(census_gpd: gpd.GeoDataFrame) -> None:
    census_gpd = census_gpd.rename(
        columns={
            "B01003_001E": "TotPop",  # "Total Population"
            "B25077_001E": "MedVal_OwnOccUnit",  # "Median value of owner occupied units"
            "B25026_001E": "TotPopOccUnits",  # "Total population in occupied housing units"
            "B25008_002E": "TotNumOwnOccUnit",  # "Total number of owner occupied units"
            "B25008_003E": "TotNumRentOccUnit",  # "Total number of renter occupied units"
            "B06009_002E": "PopLTHSDip",  # "Population with less than a high school diploma"
            "B06009_003E": "PopHSDip",  # "Population with high school diploma or equivalent"
            "B06009_004E": "PopAssoc",  # "Population with some college/associates degree"
            "B06009_005E": "PopBA",  # "Population with bachelors degree"
            "B06009_006E": "PopGrad",  # "Population with a graduate degree"
            "B01002_001E": "MedAge",  # "Median age"
            "B06010_004E": "PopIncLT10",  # "Population with income less than 9999"
            "B06010_005E": "PopInc1015",  # "Population with income between 10000 and 14999"
            "B06010_006E": "PopInc1525",  # "Population with income between 15000 and 24999"
            "B06010_007E": "PopInc2535",  # "Population with income between 25000 and 34999"
            "B06010_008E": "PopInc3550",  # "Population with income between 35000 and 49999"
            "B06010_009E": "PopInc5065",  # "Population with income between 50000 and 64999"
            "B06010_010E": "PopInc6575",  # "Population with income between 65000 and 74999"
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
    census_gpd.to_file("data/us_census/ny_census_transformed.geojson", driver="GeoJSON")


def format_values(row):
    county = f"00{str(row['county'])}"
    tract = f"00000{str(row['tract'])}"
    return county[-3:], tract[-6:]


def geo_enable_census_data() -> gpd.GeoDataFrame:
    ny_tract = gpd.read_file("data/tiger/tl_2019_36_tract.zip")
    ny_tract = ny_tract.to_crs(epsg=2263)
    ny_census_df = pd.read_csv("data/us_census/ny_census.csv")
    ny_census_df[["county", "tract"]] = ny_census_df.apply(
        lambda row: format_values(row), axis=1, result_type="expand"
    )
    ny_census_df["GEOID"] = (
        ny_census_df["state"].astype(str)
        + ny_census_df["county"].astype(str)
        + ny_census_df["tract"].astype(str)
    )
    geo_enabled_ny_census_df = ny_tract.merge(ny_census_df, on="GEOID")
    return geo_enabled_ny_census_df


if __name__ == "__main__":
    geo_enabled_ny_census_df = geo_enable_census_data()
    clean_census_data(geo_enabled_ny_census_df)
