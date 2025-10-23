import csv
from LocgiApi import GeoDataService
from UserUtils import UserInput

result = []

geo_id_jp = 20001756
geo_id_kr = 20004311
geo_id_vi = 10009958
geo_id_th = 10000007

prefix_thai = ["อำเภอ",
               "ตำบล",
               "หมู่บ้าน",
               "แขวง"]
prefix_viet = ["Tỉnh",
               "Xã",
               "Huyện",
               "Thành phố",
               "Thị xã",
               "Thị trấn",
               "Đảo"]
suffix_kr = [
    "특별시",
    "시",
    "섬",
    "주",
    "도",
    "군",
    "구",
    "광역시"
]
suffix_jp = [
    "県",
    "市",
    "町",
    "島",
    "区"
]

modify_dict = {
    'jp': {
        'id': geo_id_jp,
        'locale': 'ja_jp',
        "type": 'suffix',
        "suffix": suffix_jp
    },
    'kr': {
        'id': geo_id_kr,
        'locale': 'ko_ko',
        "type": 'suffix',
        "suffix": suffix_kr
    },
    'vi': {
        'id': geo_id_vi,
        'locale': 'vi_vn',
        "type": 'prefix',
        "prefix": prefix_viet
    },
    'th': {
        'id': geo_id_th,
        'locale': 'th_th',
        "type": 'prefix',
        "prefix": prefix_thai
    }
}

def fetch_children(parent_geo_id, country_code, locgi_url):
    geo_regions = GeoDataService.get_children_geo_by_id(parent_geo_id, locgi_url)
    if not geo_regions:
        return
    for region in geo_regions:
        geo_id = region.get('geoId')
        local_name = GeoDataService.get_geo_theme(geo_id, modify_dict[country_code]['locale'], locgi_url).get('localName', '')

        if modify_dict[country_code]['type'] == 'prefix':
            for prefix in modify_dict[country_code]['prefix']:
                if geo_name.startswith(prefix):
                    result.append((geo_id, local_name))
                    print(f"Updated geoId {geo_id} name from {local_name} to {new_name}")
        elif modify_dict[country_code]['type'] == 'suffix':
            for suffix in modify_dict[country_code]['suffix']:
                if geo_name.endswith(suffix):
                    result.append((geo_id, local_name))
                    print(f"Updated geoId {geo_id} name from {local_name} to {new_name}")
        region['children'] = fetch_children(region.get('geoId'), locgi_url)

def main():
    env = UserInput.choose_env()
    locgi_url = UserInput.get_locgi_url(env)
    for country_code in modify_dict:
        geo_id = modify_dict[country_code]['id']
        fetch_children(geo_id, country_code, locgi_url)

if __name__ == "__main__":
    main()