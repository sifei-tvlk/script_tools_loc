import csv
from LocgiApi import GeoDataService
from UserUtils import UserInput


geo_id_world = 100001

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
    # 'jp': {
    #     'id': geo_id_asia,
    #     'locale': 'ja_jp',
    #     "type": 'suffix',
    #     "suffix": suffix_jp
    # },
    'kr': {
        'id': geo_id_world,
        'locale': 'ko_ko',
        "type": 'suffix',
        "suffix": suffix_kr
    },
    'vi': {
        'id': geo_id_world,
        'locale': 'vi_vn',
        "type": 'prefix',
        "prefix": prefix_viet
    },
    'th': {
        'id': geo_id_world,
        'locale': 'th_th',
        "type": 'prefix',
        "prefix": prefix_thai
    }
}

def fetch_children(parent_geo_id, language, locgi_url):
    country_result = []
    geo_regions = GeoDataService.get_children_geo_by_id(parent_geo_id, locgi_url)
    if not geo_regions:
        return
    for region in geo_regions:
        geo_id = region.get('geoId')
        name = region.get('name')
        country_code = region.get('countryISO')
        res = GeoDataService.get_geo_theme(geo_id, modify_dict[language]['locale'], locgi_url)
        if not res:
            continue
        local_name = res.get('localName', '')
        if modify_dict[language]['type'] == 'prefix':
            for prefix in modify_dict[language]['prefix']:
                if local_name.startswith(prefix):
                    trimmed_name = local_name[len(prefix):].strip()
                    country_result.append([language, country_code, geo_id, name, local_name, trimmed_name])
                    # print(f"geoId {geo_id} name {local_name}")
                    break
        elif modify_dict[language]['type'] == 'suffix':
            for suffix in modify_dict[language]['suffix']:
                if local_name.endswith(suffix):
                    trimmed_name = local_name[:-len(suffix)].strip()
                    country_result.append([language, country_code, geo_id, name, local_name, trimmed_name])
                    # print(f"geoId {geo_id} name {local_name}")
                    break
        country_result.extend(fetch_children(region.get('geoId'), language, locgi_url))
        return country_result

def main():
    env = UserInput.choose_env()
    locgi_url = UserInput.get_locgi_url(env)
    for language_code in modify_dict:
        geo_id = modify_dict[language_code]['id']
        continents = GeoDataService.get_children_geo_by_id(geo_id, locgi_url)
        for continent in continents:
            continent_id = continent.get('geoId')
            continent_name = continent.get('name')
            countries = GeoDataService.get_children_geo_by_id(continent_id, locgi_url)
            for country in countries:
                name = country.get('name')
                country_id = country.get('geoId')
                country_code = country.get('countryISO')
                result = fetch_children(continent_id, language_code, locgi_url)
                with open(f"./{language_code}_check/check_{language_code}_{country_code}.csv", 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(['language', 'country-code', 'geoId', 'name', 'local-name', 'trimmed-name'])
                    for row in result:
                        spamwriter.writerow(row)

if __name__ == "__main__":
    main()