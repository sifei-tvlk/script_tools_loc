import csv
from LocgiApi import GeoDataService
from UserUtils import UserInput

geo_id_world = 100001

modify_dict = {
    'jp': {
        'id': geo_id_world,
        'locale': 'ja_jp',
    # },
    # 'kr': {
    #     'id': geo_id_kr,
    #     'locale': 'ko_ko',
    # },
    # 'vi': {
    #     'id': geo_id_vi,
    #     'locale': 'vi_vn',
    # },
    # 'th': {
    #     'id': geo_id_th,
    #     'locale': 'th_th',
    }
}

def fetch_children(parent_geo_id, language, locgi_url):
    result = []
    theme_res = GeoDataService.get_geo_theme(parent_geo_id, modify_dict[language]['locale'], locgi_url)
    name = theme_res.get('name')
    country_code = theme_res.get('countryISO')
    if theme_res:
        local_name = res.get('localName', '')
        if local_name.find('(') != -1 or local_name.find(')') != -1 or local_name.find('（') != -1 or local_name.find('）') != -1: 
            # print(f"id: {geo_id}, name {name}, local name {local_name}")
            result.append([language, country_code, geo_id, name, local_name])
    geo_regions = GeoDataService.get_children_geo_by_id(parent_geo_id, locgi_url)
    for region in geo_regions:
        # geo_id = region.get('geoId')
        # name = region.get('name')
        # country_code = region.get('countryISO')
        # res = GeoDataService.get_geo_theme(geo_id, modify_dict[language]['locale'], locgi_url)
        # if res:
        #     local_name = res.get('localName', '')
        #     if local_name.find('(') != -1 or local_name.find(')') != -1 or local_name.find('（') != -1 or local_name.find('）') != -1: 
        #         # print(f"id: {geo_id}, name {name}, local name {local_name}")
        #         result.append([language, country_code, geo_id, name, local_name])
        sub_result = fetch_children(region.get('geoId'), language, locgi_url)
    if sub_result:
        result.extend(sub_result)
    return result


def main():
    env = UserInput.choose_env()
    locgi_url = UserInput.get_locgi_url(env)
    for language in modify_dict:
        geo_id = modify_dict[language]['id']
        continents = GeoDataService.get_children_geo_by_id(geo_id, locgi_url)
        for continent in continents:
            continent_id = continent.get('geoId')
            continent_name = continent.get('name')
            countries = GeoDataService.get_children_geo_by_id(continent_id, locgi_url)
            print(f"Starting country {continent_name} for language {language}")
            if not countries:
                continue
            for country in countries:
                name = country.get('name')
                country_id = country.get('geoId')
                country_code = country.get('countryISO')
                result = fetch_children(country_id, language, locgi_url)
                if not result:
                    continue
                with open(f"./bracket_check/bracket_check_{country_code}_{language}.csv", 'w', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',
                                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(['language', 'country-ISO', 'geoId', 'name', 'local-name', 'is-synonym'])
                    for row in result:
                        spamwriter.writerow(row)
            print(f"Finished country {continent_name} for language {language}")

if __name__ == "__main__":
    main()