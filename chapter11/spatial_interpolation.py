import os

import pandas as pd


def get_weather_data():
    weather_dir = "data/weather/2023-10"
    weather_files = os.listdir(weather_dir)
    dfs = []
    for weather_file in weather_files:
        dfs.append(pd.read_csv(f"{weather_dir}/{weather_file}"))
    weather_df = pd.concat(dfs)


if __name__ == "__main__":
    get_weather_data()