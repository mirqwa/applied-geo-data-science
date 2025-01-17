import geopandas as gpd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    world = gpd.read_file("data/110m_cultural/ne_110m_admin_0_countries.shp")
    africa = world[world["CONTINENT"] == "Africa"]
    africa_capitals = gpd.read_file(
        "data/110m_cultural/ne_110m_populated_places.shp", mask=africa
    )

    bounding_box = (-170, 70, -60, 10)
    north_america_cities = gpd.read_file(
        "data/110m_cultural/ne_110m_populated_places.shp", bbox=bounding_box
    )

    fig, ax = plt.subplots(figsize=(12, 10))

    world.plot(ax=ax, color="lightgray")
    africa_capitals.plot(ax=ax, color="black", markersize=10, marker="o")
    north_america_cities.plot(ax=ax, color="red", markersize=10, marker="o")

    ax.set(
        xlabel="Longitude(Degrees)", ylabel="Latitude(Degrees)", title="WGS 1984 Datum"
    )

    plt.show()
