import geopandas as gpd
import matplotlib.pyplot as plt


world = gpd.read_file("data/110m_cultural/ne_110m_admin_0_countries.shp")
capitals = gpd.read_file("data/110m_cultural/ne_110m_populated_places.shp")
capitals = capitals[capitals["FEATURECLA"] == "Admin-0 capital"]
grat = gpd.read_file(
    "data/110m_physical/ne_110m_graticules_all/ne_110m_graticules_10.shp"
)

fig, ax = plt.subplots(figsize=(12, 10))

world.plot(ax=ax, color="lightgray")
capitals.plot(ax=ax, color="black", markersize=10, marker="o")
grat.plot(ax=ax, color="lightgray", linewidth=0.5)

ax.set(xlabel="Longitude(Degrees)", ylabel="Latitude(Degrees)", title="WGS 1984 Datum")

plt.show()
