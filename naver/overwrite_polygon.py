import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)
import json
from LocgiApi import GeoDataService
from UserUtils import UserInput

locgi_url = UserInput.get_locgi_url('staging')

sk_id = 20004311

pair_info_list = []
pair_info_file = 'l1_pair_info.json'
with open(pair_info_file, 'r') as file:
    pair_info_list = json.load(file)

new_regions = []
new_region_file = 'new_region_id_list.json'
with open(new_region_file, 'r') as file:
    new_regions = json.load(file)

hier_dict = {}
hier_dict_file = 'hier_dict_test.json'
with open(hier_dict_file, 'r') as file:
    hier_dict = json.load(file)

def overrite_geojson(geoId, geojson, locgi_url):
    data = GeoDataService.get_geo_with_geometry_by_id(geoId, locgi_url)
    data['geometry'] = geojson
    res = GeoDataService.upsert_geo_with_geometry(data, locgi_url)
    return res

def add_new_regions(name, region_type, parentId, center_lng, center_lat, geojson, locgi_url):
    parent_data = GeoDataService.get_geo_with_geometry_by_id(parentId, locgi_url)
    data = {
        "name": name,
        "type": region_type,
        "countryISO": "KR",
        "centerLatitude": center_lat,
        "centerLongitude": center_lng,
        "geoLocation": {
            "lon": center_lng,
            "lat": center_lat
        },
        "timezoneId": "Asia/Seoul",
        "DEFAULT_POPULARITY": 0.1,
        "DEFAULT_POPULARITYV2": -1.0,
        "geoId": 0,
        "parentId": parentId,
        "popularity": min(0.75, parent_data.get('popularity')),
        "popularityV2": min(0.75, parent_data.get('popularityV2')),
        "users": [
            "ACCOMMODATION",
            "EXPERIENCE",
            "CULINARY",
            "CAR_RENTAL",
            "LOCAL",
            "AIRPORT_TRANSFER",
            "TRANSPORT_EXTRANET",
            "FLIGHT",
            "TRAIN",
            "CINEMA",
            "BILL",
            "OTHER",
            "VACATION"
        ],
        "geometry": geojson,
        "isActive": "true",
        "isManualCentroid": "false"
    }
    res = GeoDataService.upsert_geo_with_geometry(data, locgi_url)

for pair_info in pair_info_list:
    geoId = pair_info[1]
    admcode = pair_info[0]
    geojson_file = f'./geojson/area1/{admcode}_polygon.json'
    with open(geojson_file, 'r') as file:
        geojson = json.load(file).get('features')[0].get('geometry')
    print(geoId, admcode)
    res = overrite_geojson(geoId, geojson, locgi_url)
    print(geoId, " polygon overwritten.")

# l1 new region
for new_region in new_regions:
    admcode = new_region[0]
    name = new_region[1]
    naver_code = new_region[2]
    parentId = sk_id
    geojson_file = f'./geojson/area1/{admcode}_polygon.json'
    center_lng = hier_dict[naver_code]['coords'][0]
    center_lat = hier_dict[naver_code]['coords'][1]
    with open(geojson_file, 'r') as file:
        geojson = json.load(file)
    add_new_regions(name, "REGION", parentId, center_lng, center_lat, geojson, locgi_url)
    print(name, admcode, " new region added.")