import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)
import json
import csv
from LocgiApi import GeoDataService
from UserUtils import UserInput

choose = UserInput.choose_env()
locgi_url = UserInput.get_locgi_url(choose)

process_level = 0

input_message = "Pick an process level:\n"
user_input = ""
while user_input not in map(str, range(0, 4)):
    user_input = input(input_message)
process_level = int(user_input)

pair_info_list = []
with open('pair_info.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
        pair_info_list.append(row)

new_regions = []
with open('new_region_id_list.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
        new_regions.append(row)

hier_dict = {}
hier_dict_file = 'hier_dict.json'
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
    if pair_info[4] != str(process_level + 1):
        continue
    geojson_file = f'./geojson/area{process_level}/{admcode}_polygon.json'
    with open(geojson_file, 'r') as file:
        geojson = json.load(file).get('features')[0].get('geometry')
    print(geoId, admcode)
    res = overrite_geojson(geoId, geojson, locgi_url)
    print(geoId, " polygon overwritten.")

for new_region in new_regions:
    admcode = new_region[0]
    name = new_region[1]
    naver_code = new_region[2]
    parentId = new_region[3]
    geojson_file = f'./geojson/area{process_level}/{admcode}_polygon.json'
    center_lng = hier_dict[naver_code]['coords'][0]
    center_lat = hier_dict[naver_code]['coords'][1]
    with open(geojson_file, 'r') as file:
        geojson = json.load(file)
    add_new_regions(name, "REGION", parentId, center_lng, center_lat, geojson, locgi_url)
    print(name, admcode, " new region added.")