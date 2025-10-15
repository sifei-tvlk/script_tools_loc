import json
import requests

def get_result(response):
    if response.status_code == 200:
        res_json = response.json()
        error = res_json.get("error", None)
        if error is None or error == "":
            res = res_json.get("result", None)
            if res:
                return res
    return None

class GeoDataService:

    @staticmethod
    def get_gadm_after_id(gadm_id, type, url, limit=1, skip=0):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "script",
            "method": "findGadmAfterId",
            "params": [
                {
                    "id": gadm_id,
                    "type": type,
                    "page" : {
                        "limit": limit,
                        "skip": skip
                    }
                }
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/gadm", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def get_gadm(gadm_id, type, url, limit=1, skip=0):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "script",
            "method": "findGadmBySpec",
            "params": [
                {
                    "id": gadm_id,
                    "type": type,
                    "page" : {
                        "limit": limit,
                        "skip": skip
                    }
                }
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/gadm", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def do_mapping_gadm(id, type, url):
        # skip this id
        if id == "?":
            return None

        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "script",
            "method": "findAndMatchWithGadm",
            "params": [
                {
                    "id": id,
                    "type": type,
                    "page" : {
                        "limit": 1,
                        "skip": 0
                    }
                }
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geometryEnhancer", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def do_update_geometry_after_id(gadm_id, type, url, limit=1, skip=0):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "script",
            "method": "doUpdateGeometryAfterId",
            "params": [
                {
                    "id": gadm_id,
                    "type": type,
                    "page" : {
                        "limit": limit,
                        "skip": skip
                    }
                }
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geometryEnhancer", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def do_update_geometry_by_id(gadm_id, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "script",
            "method": "doUpdateGeometryById",
            "params": [gadm_id]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geometryEnhancer", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def get_geo_region_after_id(geo_id, limit, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "script",
            "method": "getGeoRegionsAfterId",
            "params": [
                geo_id,
                limit
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def do_translate_geo(geo_id, locales, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "script",
            "method": "translationGeoName",
            "params": [
                {
                    "geoId": geo_id,
                    "locales": locales,
                    "user": "script"
                }
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def get_geo_with_geometry_by_id(geo_id, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "getGeoRegionWithGeometryById",
            "params": [
                int(geo_id)
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def upsert_geo_with_geometry(geo, url):
        req_body = {
            "id": "123",
            "jsonrpc": "2.0",
            "source": "localhost",
            "method": "upsertGeoRegionWithGeometry",
            "params": [
                geo,
                "Andri",
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def upsert_geo_region(geo,url):
        req_body = {
            "id": "123",
            "jsonrpc": "2.0",
            "source": "localhost",
            "method": "upsertGeoRegion",
            "params": [
                geo,
                "Deft",
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def get_geo_region_by_id(geo_id, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "getGeoRegionById",
            "params": [
                int(geo_id)
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)


    @staticmethod
    def push_geo_regions(geo_list, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "pushGeoRegions",
            "params": [
                geo_list
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def get_geo_theme(id, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "getGeoThemeInfo",
            "params": [
                "ko_ko",
                id,
                "DEFAULT"
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def upsert_geo_theme(geo_theme_, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "upsertGeoThemeInfo",
            "params": [
                "ko_ko",
                geo_theme_,
                "Deft"
            ]
        }
        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def get_children_geo_by_id(geoId, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "getChildrenGeos",
            "params": [
                geoId
            ]
        }
        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

class LandmarkEnrichmentService:

    @staticmethod
    def add_new_landmark_from_external(landmark_provider_list, url):
        req_body = {
            "id": "123",
            "jsonrpc": "2.0",
            "source": "localhost",
            "method": "addLandmarkFromExternal",
            "params": [
                landmark_provider_list,
                "Andri",
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/landmarkEnrichmentFromExternal", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

class LandmarkDataService:

    @staticmethod
    def push_landmarks(landmark_id_list, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "pushLandmarks",
            "params": [
                landmark_id_list
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/landmarkData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)


    @staticmethod
    def get_landmark_after_id(landmark_id, limit, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "getLandmarksAfterId",
            "params": [
                landmark_id, limit
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/landmarkData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)


    @staticmethod
    def get_landmark_by_id(landmark_id, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "getLandmarkById",
            "params": [
                int(landmark_id)
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/landmarkData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)


    @staticmethod
    def update_landmark(landmark, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "localhost",
            "method": "upsertLandmark",
            "params": [
                landmark,
                "Andri"
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/landmarkData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)


    @staticmethod
    def upsert_landmark_locale_info(locale_info, locale, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "bastion",
            "method": "upsertLandmarkLocaleInfo",
            "params": [
                locale,
                locale_info,
                "Andri"
            ]
        }

        req_body_json = json.dumps(req_body)

        response = requests.post(url=url + "/landmarkData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def get_landmark_locale_info(landmark_id, locale, url):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "bastion",
            "method": "getLandmarkLocaleInfo",
            "params": [
                locale,
                int(landmark_id)
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/landmarkData", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)
