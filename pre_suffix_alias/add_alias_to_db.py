import csv
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

from LocgiApi import GeoDataService
from UserUtils import UserInput

locgi_url = UserInput.get_locgi_url("production")

# Step 1: Load CSV into a dictionary
geo_alias_map = {}
with open('bracket_check_jp_alias_fixed.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for i, row in enumerate(reader):
        if i == 0:
            continue
        geoId = row['geoId']
        alias = row['alias'].split(",")
        for i, a in enumerate(alias):
            alias[i] = alias[i].strip(" ").strip("[]'\"")
        if geoId and alias:
            geo_alias_map[geoId] = alias
            print(geoId, alias)

# Step 2: Loop through the dictionary and update via API
for geoId, new_aliases in geo_alias_map.items():
    data = GeoDataService.get_geo_region_by_id(geoId, locgi_url)
    existing_aliases = data.get('alias', [])
    print(existing_aliases)
    print(new_aliases)
    if existing_aliases:
        existing_aliases.extend(new_aliases)
    else:
        existing_aliases = new_aliases
    combined_aliases = list(set(existing_aliases))  # Avoid duplicates
    data['alias'] = combined_aliases
    GeoDataService.upsert_geo_region(data, locgi_url)
    new_data = GeoDataService.get_geo_region_by_id(geoId, locgi_url)
    print(geoId, new_data.get('alias', []))
    break
