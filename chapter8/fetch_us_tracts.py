import wget

for i in range(10, 79):
    url = f"https://www2.census.gov/geo/tiger/TIGER2019/TRACT/tl_2019_{i}_tract.zip"
    try:
        wget.download(url, out="data/tiger/TIGER2019")
    except Exception:
        continue