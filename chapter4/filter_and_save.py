from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt


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

    fig, ax = plt.subplots(figsize=(12, 10))

    world.plot(ax=ax, color="lightgray")
    africa_capitals.plot(ax=ax, color="blue", markersize=10, marker="o")
    north_america_cities.plot(ax=ax, color="red", markersize=10, marker="o")
    south_america_cities.plot(ax=ax, color="green", markersize=10, marker="o")

    ax.set(
        xlabel="Longitude(Degrees)", ylabel="Latitude(Degrees)", title="WGS 1984 Datum"
    )

    plt.show()
