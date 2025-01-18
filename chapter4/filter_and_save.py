from pathlib import Path

import geopandas as gpd
import geoplot.crs as gcrs
import geoplot as gplt
import matplotlib.pyplot as plt
import pandas as pd


def save_geodf(geodf: gpd.GeoDataFrame, path: str, driver: str) -> None:
    output_path = Path(path)
    Path(output_path.parent).mkdir(parents=True, exist_ok=True)
    geodf.to_file(output_path, driver=driver)


if __name__ == "__main__":
    world = gpd.read_file("data/110m_cultural/ne_110m_admin_0_countries.shp")
    africa = world[world["CONTINENT"] == "Africa"]
    africa_capitals = gpd.read_file(
        "data/110m_cultural/ne_110m_populated_places.shp", mask=africa
    )
    save_geodf(
        africa_capitals, "data/output/africa/capitals/capitals.shp", "ESRI Shapefile"
    )

    bounding_box = (-170, 70, -60, 10)
    north_america_cities = gpd.read_file(
        "data/110m_cultural/ne_110m_populated_places.shp", bbox=bounding_box
    )
    save_geodf(
        north_america_cities,
        "data/output/north_america/capitals/capitals.geojson",
        "GeoJSON",
    )

    bounding_box = world[world["CONTINENT"] == "South America"].geometry.total_bounds
    south_america_cities = gpd.read_file(
        "data/110m_cultural/ne_110m_populated_places.shp", bbox=tuple(bounding_box)
    )
    save_geodf(
        south_america_cities,
        "data/output/south_america/capitals/capitals.geojson",
        "GeoJSON",
    )

    # fig, ax = plt.subplots(figsize=(12, 10))
    ax = gplt.webmap(world, projection=gcrs.WebMercator())
    filtered_cities = gpd.GeoDataFrame(
        pd.concat(
            [africa_capitals, north_america_cities, south_america_cities],
            ignore_index=True,
        ),
        crs=africa_capitals.crs,
    )
    gplt.pointplot(filtered_cities, ax=ax)

    plt.show()
