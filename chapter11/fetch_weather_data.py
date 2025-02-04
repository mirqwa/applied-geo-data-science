import glob
import re
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


LOCATIONS = [
    "London",
    "Manchester",
    "Liverpool",
    "Falmer",
    "Birmingham",
    "Wolverhampton",
    "Bournemouth",
    "Sheffield",
    "Nottingham",
    "Newcastle upon Tyne",
    "Luton",
    "Burnley",
    "Leeds",
    "Leicester",
    "Southampton",
    "Norwich",
    "Watford",
    "West Bromwich",
    "Huddersfield",
    "Cardiff",
    "Swansea",
    "Stoke-on-Trent",
    "Kingston upon Hull",
    "Middlesbrough",
    "Sunderland",
    "Reading",
    "Wigan",
    "Blackburn",
    "Bolton",
    "Blackpool",
    "Portsmouth",
    "Derby",
    "Ipswich",
    "Coventry",
    "Bradford",
    "Barnsley",
    "Swindon",
    "Oldham",
]

DATES = ["2025-02-01"]


def get_station_code(station_name):
    pattern = r"\((.*)\)"
    pattern_search = re.search(pattern, station_name)
    return pattern_search.group(1)


def get_cached_weather_stations(city):
    file_pattern = f"data/weather/stations/{city}/*/*.csv"
    weather_stations = [
        file.split("/")[-1].replace(".csv", "")
        for file in glob.glob(file_pattern, recursive=True)
    ]
    return set(weather_stations)


def get_weather_stations(city, date, cached=False):
    if cached:
        weather_stations = get_cached_weather_stations(city)
        if weather_stations:
            print("Using cached weather stations...")
            return weather_stations
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)
    url = f"https://www.wunderground.com/history/daily/gb/{city}/date/{date}"
    print(f"Getting weather station from {url}")
    driver.get(url)
    WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//*[@id="station-select-button"]',
            )
        )
    ).click()
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                '//*[@id="stationselector_table"]/div[1]/a',
            )
        )
    )
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "lxml")
    stations = soup.find_all("a", {"class": "stationselectorRowPWS"})
    stations = [get_station_code(station.text) for station in stations]
    driver.quit()
    return stations


def get_tables_from_site(city, weather_station, date):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)
    url = f"https://www.wunderground.com/history/daily/gb/{city}/{weather_station}/date/{date}"
    print(f"Loading the page for station data: {url}")
    driver.get(url)
    table_xpath = '//*[@id="inner-content"]/div[2]/div[1]/div[5]/div[1]/div/lib-city-history-observation/div/div[2]/table'
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                table_xpath,
            )
        )
    )

    soup = BeautifulSoup(driver.page_source, "lxml")
    geo_cordinates = soup.find("span", {"class": "subheading"}).text.strip()
    driver.quit()
    print(f"Page loaded and tables extracted for {city}, {weather_station}, {date}")
    return geo_cordinates, soup.find_all("table")


def get_weather_station_data(city, weather_station, date, geo_cordinates, tables):
    tables = pd.read_html(str(tables))

    directory = f"data/weather/stations/{city}/{date}"
    Path(directory).mkdir(parents=True, exist_ok=True)

    for table in tables:
        columns = table.columns.to_list()
        if columns[0] == "Time":
            table["Coordinate"] = geo_cordinates
            table["Date"] = date
            table = table[["Coordinate", "Date"] + columns]
            table.to_csv(f"{directory}/{weather_station}.csv", index=False)
            break


def get_weather_data(city, date):
    print("==========================================================")
    print(f"Getting data for {city} on {date}")
    print(f"Getting weather stations for {city} on {date}")
    try:
        weather_stations = get_weather_stations(city, date)
        for weather_station in weather_stations:
            directory = f"data/weather/stations/*/{date}"
            file_path = f"{directory}/{weather_station}.csv"
            if glob.glob(file_path):
                print(f"{date}/{weather_station}.csv already downloaded, skipping")
                continue
            geo_cordinates, tables = get_tables_from_site(city, weather_station, date)
            get_weather_station_data(
                city, weather_station, date, geo_cordinates, tables
            )
        print(f"Weather data fetch for {city}, {date} done")
    except Exception:
        print(f"Weather data fetch for {city}, {date} failed")


if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        for location in LOCATIONS:
            for date in DATES:
                executor.submit(get_weather_data, location.lower(), date)
