import csv

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

from LocgiApi import GeoDataService
from UserUtils import UserInput

locgi_url = UserInput.get_locgi_url("production")

# Step 1: Load CSV into a dictionary
geo_alias_map = {}
with open('bracket_check_jp_alias_fixed.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        geoId = row['geoId']
        alias = row['alias']
        if geoId and alias:
            geo_alias_map[geoId] = [a.strip() for a in alias.split(',') if a.strip()]
print(geo_alias_map)

# Step 2: Loop through the dictionary and update via API
for geoId, new_aliases in geo_alias_map.items():
    data = GeoDataService.get_geo_with_geometry_by_id(geoId, locgi_url)
    print(data)
    existing_aliases = data.get('alias', [])
    combined_aliases = list(set(existing_aliases + new_aliases))  # Avoid duplicates
    data['alias'] = combined_aliases
    print(data)
    # GeoDataService.upsert_geo_with_geometry(data, locgi_url)
    break
