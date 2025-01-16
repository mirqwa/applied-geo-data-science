import geopandas as gpd
import matplotlib.pyplot as plt


world = gpd.read_file("data/110m_cultural/ne_110m_admin_0_countries.shp")
capitals = gpd.read_file("data/110m_cultural/ne_110m_populated_places.shp")
capitals = capitals[capitals["FEATURECLA"] == "Admin-0 capital"]
grat = gpd.read_file(
    "data/110m_physical/ne_110m_graticules_all/ne_110m_graticules_10.shp"
)
