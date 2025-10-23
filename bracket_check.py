import csv
from LocgiApi import GeoDataService
from UserUtils import UserInput

result = []

geo_id_jp = 20001756
geo_id_kr = 20004311
geo_id_vi = 10009958
geo_id_th = 10000007

modify_dict = {
    'jp': {
        'id': geo_id_jp,
        'locale': 'ja_jp',
    },
    'kr': {
        'id': geo_id_kr,
        'locale': 'ko_ko',
    },
    'vi': {
        'id': geo_id_vi,
        'locale': 'vi_vn',
    },
    'th': {
        'id': geo_id_th,
        'locale': 'th_th',
    }
}

def fetch_children(parent_geo_id, country_code, locgi_url):
    geo_regions = GeoDataService.get_children_geo_by_id(parent_geo_id, locgi_url)
    if not geo_regions:
        return
    for region in geo_regions:
        geo_id = region.get('geoId')
        name = region.get('name')
        res = GeoDataService.get_geo_theme(geo_id, modify_dict[country_code]['locale'], locgi_url)
        if not res:
            if name.find('(') != -1 or local_name.find(')') != -1:
                result.append([country_code, geo_id, name, '-'])
                print(f"id: {geo_id} name {local_name}")
            continue
        local_name = res.get('localName', '')
        if local_name.find('(') != -1 or local_name.find(')') != -1:
            print(f"id: {geo_id}, name {name}, local name {local_name}")
            result.append([country_code, geo_id, name, local_name])
        fetch_children(region.get('geoId'), country_code, locgi_url)

def main():
    env = UserInput.choose_env()
    locgi_url = UserInput.get_locgi_url(env)
    for country_code in modify_dict:
        geo_id = modify_dict[country_code]['id']
        fetch_children(geo_id, country_code, locgi_url)

    with open('bracket_check.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['country_code', 'geoId', 'name', 'local_name'])
        for row in result:
            spamwriter.writerow(row)

if __name__ == "__main__":
    main()