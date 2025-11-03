import csv
from LocgiApi import GeoDataService
from UserUtils import UserInput
import re
import os

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
    "광역시",
    "특별시",
    "제도",
    "시",
    "섬",
    "주",
    "도",
    "군",
    "구",
    "읍",
    "면",
    "동",
    "리"
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
        'id': geo_id_world,
        'locale': 'ja_jp',
        "type": 'suffix',
        "suffix": suffix_jp
    },
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
supp_check_dict = {}

def extract_suffixes(language):
    directory = f"{language}_check"
    pattern = re.compile(rf'^check_{language}_([A-Z]+)\.csv$')
    suffixes = []

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            suffixes.append(match.group(1))
    return suffixes

def fetch_children(parent_geo_id, language, locgi_url):
    geo_regions = GeoDataService.get_children_geo_by_id(parent_geo_id, locgi_url)
    if not geo_regions:
        return []
    for region in geo_regions:
        geo_id = region.get('geoId')
        name = region.get('name')
        country_code = region.get('countryISO')
        res = GeoDataService.get_geo_theme(geo_id, modify_dict[language]['locale'], locgi_url)
        if res:
            local_name = res.get('localName', '')
            if local_name:
                if modify_dict[language]['type'] == 'prefix':
                    for prefix in modify_dict[language]['prefix']:
                        if local_name.startswith(prefix):
                            trimmed_name = local_name[len(prefix):].strip()
                            if country_code not in supp_check_dict:
                                supp_check_dict[country_code] = []
                            supp_check_dict[country_code].append([language, country_code, geo_id, name, local_name, trimmed_name])
                            break
                elif modify_dict[language]['type'] == 'suffix':
                    for suffix in modify_dict[language]['suffix']:
                        if local_name.endswith(suffix):
                            trimmed_name = local_name[:-len(suffix)].strip()
                            if country_code not in supp_check_dict:
                                supp_check_dict[country_code] = []
                            supp_check_dict[country_code].append([language, country_code, geo_id, name, local_name, trimmed_name])
                            break
        fetch_children(geo_id, language, locgi_url)

def main():
    env = UserInput.choose_env()
    locgi_url = UserInput.get_locgi_url(env)
    for language_code in modify_dict:
        geo_id = modify_dict[language_code]['id']
        continents = GeoDataService.get_children_geo_by_id(geo_id, locgi_url)
        countries_gotten = extract_suffixes(language_code)
        for continent in continents:
            continent_id = continent.get('geoId')
            continent_name = continent.get('name')
            upper_countries = GeoDataService.get_children_geo_by_id(continent_id, locgi_url)
            print(f"Starting country {continent_name} for language {language_code}")
            if not upper_countries:
                continue
            for upper_country in upper_countries:
                if upper_country.get('type') == 'COUNTRY':
                    continue
                name = upper_country.get('name')
                country_id = upper_country.get('geoId')
                fetch_children(country_id, language_code, locgi_url)
    for country_code in supp_check_dict:
        with open(f"./supp_check/check_{language_code}_{country_code}.csv", 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['language', 'country-code', 'geoId', 'name', 'local-name', 'trimmed-name'])
            for row in supp_check_dict[country_code]:
                spamwriter.writerow(row)
            print(f"Finished country {continent_name} for language {language_code}")

if __name__ == "__main__":
    main()