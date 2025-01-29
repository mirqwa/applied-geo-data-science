import argparse

import pandas as pd
from census import Census
from us import states


def main(api_key: str) -> None:
    census_api = Census(api_key)
    ny_census = census_api.acs5.state_county_tract(
        fields=(
            "NAME",
            "B01003_001E",
            "B25026_001E",
            "B25008_002E",
            "B25008_003E",
            "B06010_011E",
            "B28007_009E",
            "B19059_002E",
            "B19059_003E",
            "B08013_001E",
            "B17013_002E",
        ),
        state_fips=states.NY.fips,
        county_fips="*",
        tract="*",
        year=2019,
    )
    ny_census_df = pd.DataFrame(ny_census)
    ny_census_df.to_csv("data/us_census/ny_census.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_key",
        type=str,
    )

    args = parser.parse_args()
    main(args.api_key)
