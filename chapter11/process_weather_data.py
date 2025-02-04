import re
import datetime

import dask.dataframe as dd
import pandas as pd


def get_latitude_and_longitude(coordinate):
    date_pattern = r"((\d+\.*\d*) °[N,S]), ((\d+\.*\d*) °[W,E])"
    pattern_search = re.search(date_pattern, coordinate)
    lat = pattern_search.group(2)
    lat = -1 * float(lat) if "S" in pattern_search.group(1) else lat
    long = pattern_search.group(4)
    long = -1 * float(long) if "W" in pattern_search.group(3) else long
    return long, lat


def get_numerical_value(value):
    try:
        return float(re.search(r"(\d+\.*\d*)", value).group(1))
    except Exception:
        return None


def pre_process_columns(row):
    long, lat = get_latitude_and_longitude(row["Coordinate"])
    temp = get_numerical_value(row["Temperature"])
    temp = (temp - 32) * 5 / 9 if temp else temp
    dew_point = get_numerical_value(row["Dew Point"])
    dew_point = (dew_point - 32) * 5 / 9 if dew_point else dew_point
    humidity = get_numerical_value(row["Humidity"])
    # convert to km/h
    wind_speed = get_numerical_value(row["Wind Speed"])
    wind_speed = wind_speed * 1.60934 if wind_speed else wind_speed
    # convert to km/h
    wind_gust = get_numerical_value(row["Wind Gust"])
    wind_gust = wind_gust * 1.60934 if wind_gust else wind_gust
    pressure = get_numerical_value(row["Pressure"])
    precip = get_numerical_value(row["Precip."])
    try:
        observation_time = datetime.datetime.strptime(
            f"{row['Date']} {row['Time']}", "%Y-%m-%d %I:%M %p"
        )
        time = observation_time.strftime("%Y-%m-%d %H:%M")
        time_of_the_day = observation_time.strftime("%H")
    except ValueError:
        time = ""
        time_of_the_day = ""
    return (
        time,
        time_of_the_day,
        long,
        lat,
        temp,
        dew_point,
        humidity,
        wind_speed,
        wind_gust,
        pressure,
        precip,
    )


def process_weather_data(result_file):
    for month_index in pd.date_range(start="2024-02-01", end="2025-03-31", freq="M"):
        year_month = month_index.strftime("%Y-%m")
        print("Processing data for", year_month)
        try:
            ddf = dd.read_csv(
                f"data/weather/stations/*/{year_month}-*/*.csv"
            )
        except OSError:
            continue
        ddf = ddf.repartition(npartitions=5)
        ddf[
            [
                "Date Time",
                "Time of Day",
                "Longitude",
                "Latitude",
                "Temperature",
                "Dew Point",
                "Humidity",
                "Wind Speed",
                "Wind Gust",
                "Pressure",
                "Precip.",
            ]
        ] = ddf.apply(
            pre_process_columns,
            axis=1,
            result_type="expand",
            meta={
                0: str,
                1: int,
                2: float,
                3: float,
                4: int,
                5: int,
                6: int,
                7: int,
                8: int,
                9: float,
                10: float,
            },
        )
        try:
            ddf.to_csv(
                f"data/weather/processed_stations/{month_index.strftime('%Y')}/{year_month}/*.csv",
                index=False,
            )
        except Exception as e:
            result_file.write(year_month)


if __name__ == "__main__":
    with open(
        "data/weather/weather_processing_failed.txt", "a"
    ) as result_file:
        process_weather_data(result_file)
