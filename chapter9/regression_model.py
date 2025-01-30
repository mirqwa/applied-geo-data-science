import geopandas as gpd


if __name__ == "__main__":
    manhattan_listings = gpd.read_file("data/new_york/manhattan_listings.geojson")
