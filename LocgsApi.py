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

class GeoSearchService:

    @staticmethod
    def get_geo_details(list_geo_ids, url, limit=1, skip=0):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "script",
            "method": "getGeoDetails",
            "params": [
                {
                    "geoIds": list_geo_ids,
                    "locale": "ko_ko"
                }
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoSearch", data=req_body_json, headers={"Content-Type": "application/json"})
        return get_result(response)

    @staticmethod
    def get_geo_id_by_country_iso(iso, url, limit=1, skip=0):
        req_body = {
            "jsonrpc": "2.0",
            "id": "123",
            "source": "script",
            "method": "getGeoIdsByCountryISO",
            "params": [
                {
                    "countryISO": iso,
                    "filter": {
                        "types": ["COUNTRY"]
                    }
                }
            ]
        }

        req_body_json = json.dumps(req_body)
        response = requests.post(url=url + "/geoSearch", data=req_body_json, headers={"Content-Type": "application/json"})
        if not response or not get_result(response):
            return None
        return get_result(response).get('ids')
