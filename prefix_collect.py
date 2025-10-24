import csv
from LocgiApi import GeoDataService
from UserUtils import UserInput

result = []

geo_id_asia = 30019581

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
    "郡",
    "町",
    "島",
    "区",
    "村"
]

modify_dict = {
    'jp': {
        'id': geo_id_asia,
        'locale': 'ja_jp',
        "type": 'suffix',
        "suffix": suffix_jp
    },
    'kr': {
        'id': geo_id_asia,
        'locale': 'ko_ko',
        "type": 'suffix',
        "suffix": suffix_kr
    },
    'vi': {
        'id': geo_id_asia,
        'locale': 'vi_vn',
        "type": 'prefix',
        "prefix": prefix_viet
    },
    'th': {
        'id': geo_id_asia,
        'locale': 'th_th',
        "type": 'prefix',
        "prefix": prefix_thai
    }
}

def fetch_children(parent_geo_id, language, locgi_url):
    geo_regions = GeoDataService.get_children_geo_by_id(parent_geo_id, locgi_url)
    if not geo_regions:
        return
    for region in geo_regions:
        geo_id = region.get('geoId')
        name = region.get('name')
        country_code = region.get('countryCode')
        res = GeoDataService.get_geo_theme(geo_id, modify_dict[language]['locale'], locgi_url)
        if not res:
            continue
        local_name = res.get('localName', '')
        if modify_dict[language]['type'] == 'prefix':
            for prefix in modify_dict[language]['prefix']:
                if local_name.startswith(prefix):
                    trimmed_name = local_name[len(prefix):].strip()
                    result.append([language, country_code, geo_id, name, local_name, trimmed_name])
                    print(f"geoId {geo_id} name {local_name}")
                    break
        elif modify_dict[language]['type'] == 'suffix':
            for suffix in modify_dict[language]['suffix']:
                if local_name.endswith(suffix):
                    trimmed_name = local_name[:-len(suffix)].strip()
                    result.append([language, country_code, geo_id, name, local_name, trimmed_name])
                    print(f"geoId {geo_id} name {local_name}")
                    break
        fetch_children(region.get('geoId'), language, locgi_url)

def main():
    env = UserInput.choose_env()
    locgi_url = UserInput.get_locgi_url(env)
    for country_code in modify_dict:
        geo_id = modify_dict[country_code]['id']
        fetch_children(geo_id, country_code, locgi_url)

        with open(f'{modify_dict[country_code]["type"]}_check_{modify_dict[country_code]["locale"]}.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['language', 'country-code', 'geoId', 'name', 'local-name', 'trimmed-name'])
            for row in result:
                spamwriter.writerow(row)

if __name__ == "__main__":
    main()