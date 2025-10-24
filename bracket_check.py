import csv
from LocgiApi import GeoDataService
from UserUtils import UserInput

result = []

geo_id_asia = 30019581

modify_dict = {
    'jp': {
        'id': geo_id_jp,
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
    geo_regions = GeoDataService.get_children_geo_by_id(parent_geo_id, locgi_url)
    if not geo_regions:
        return
    for region in geo_regions:
        geo_id = region.get('geoId')
        name = region.get('name')
        country_code = region.get('countryISO')
        res = GeoDataService.get_geo_theme(geo_id, modify_dict[language]['locale'], locgi_url)
        if not res:
            if name.find('(') != -1 or name.find(')') != -1:
                result.append([language, geo_id, name, '-'])
                print(f"id: {geo_id} name {name}")
            continue
        local_name = res.get('localName', '')
        if local_name.find('(') != -1 or local_name.find(')') != -1 or local_name.find('（') != -1 or local_name.find('）') != -1: 
            print(f"id: {geo_id}, name {name}, local name {local_name}")
            result.append([language, geo_id, name, local_name])
        fetch_children(region.get('geoId'), language, locgi_url)

def main():
    env = UserInput.choose_env()
    locgi_url = UserInput.get_locgi_url(env)
    for language in modify_dict:
        geo_id = modify_dict[language]['id']
        fetch_children(geo_id, language, locgi_url)

        with open(f'bracket_check_{language}.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['country-code', 'geoId', 'name', 'local-name', 'is-synonym'])
            for row in result:
                spamwriter.writerow(row)

if __name__ == "__main__":
    main()