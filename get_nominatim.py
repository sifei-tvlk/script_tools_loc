import requests
import urllib, json
from LocgsApi import GeoSearchService
from LocgiApi import GeoDataService
from UserUtils import UserInput
from copy import deepcopy

def get_data_by_city_name(city_name):
    template = "https://nominatim.openstreetmap.org/search?city={}&polygon_geojson=1&format=json"
    url = template.format(city_name.replace(" ", "%20"))
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    result = {}
    for item in data:
        if item["class"] == "boundary":
            return item
    return {}

def get_upsert_data(name, regionType, lon, lat, parentData, geometry, geoBound, author=""):
    if len(geoBound) != 4:
        return None
    southLatitude = geoBound[0]
    northLatitude = geoBound[1]
    westLongitude = geoBound[2]
    eastLongitude = geoBound[3]
    data = deepcopy(parentData)
    parentId = data.get("geoId", 0)
    data["geoId"] = 0
    data["type"] = regionType
    data["name"] = name
    data["longName"] = None
    data["alias"] = []
    data["postalCode"] = None
    data["centerLatitude"] = lat
    data["centerLongitude"] = lon
    data["geoLocation"] = {
        "lon": lon,
        "lat": lat
    }
    data["geoBounds"] = {
        "northLatitude": northLatitude,
        "southLatitude": southLatitude,
        "westLongitude": westLongitude,
        "eastLongitude": eastLongitude
    }
    data["parentId"] = parentId
    data["themes"] = []
    data["geometry"] = geometry
    data["fipsCode"] = None
    data["description"] = None
    data["localName"] = None
    data["caption"] = None
    data["includedInSEO"] = False
    data["searchVolume"] = 0
    data["relevance"] = 0.0
    data["searchResultRelevance"] = 0.0
    data["duplicateId"] = None
    data["isActive"] = True
    return data

if __name__ == "__main__":
    locgi_url = UserInput.get_locgi_url("production")
    infos = [
        ["Forster", 4007839722],
        ["Kalbarri", 4007839625],
        ["Lakes Entrance", 4007839541],
        ["Mudgee", 4007839751],

        ["Shoal Bay", 4002152652],
        ["Lightning Ridge", 4007839781],

        ["Rainbow Beach", 4007839583],
        ["South West Rocks", 4007839737],
        ["Thredbo", 4007839772],
        ["Beechworth", 4007839795],
        ["Bowen", 4007839413],
        ["Yamba", 4007839711],
        ["Coral Bay", 4007839376],
    ]

    for info in infos:
        name = info[0]
        data = get_data_by_city_name(name)
        parentId = info[1]
        lat = data.get("lat", 0)
        lon = data.get("lon", 0)
        geometry = data.get("geojson", {})
        parent_data = GeoDataService.get_geo_with_geometry_by_id(parentId, locgi_url)
        # print(parent_data)
        # print("//////////////////")
        # print(geometry)
        # print("//////////////////")
        new_region_data = get_upsert_data(name, "CITY", lon, lat, parent_data, geometry, data.get("boundingbox", []), author="")
        if not new_region_data:
            print("Failed to get new region data")
        else:
            result = GeoDataService.upsert_geo_with_geometry(new_region_data, locgi_url)
            print(name, parentId, result)
