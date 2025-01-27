import requests

import pandas as pd


overpass_url = "http://overpass-api.de/api/interpreter"

overpass_query = """
[out:json];
node["amenity"="place_of_worship"]
  (-1.5,36.7,-1.2,36.9);
out center;
"""


response = requests.get(overpass_url, params={"data": overpass_query})
data = response.json()
df = pd.DataFrame(data["elements"])
df.to_csv("data/osm/nairobi_worship_places.csv", index=False)
