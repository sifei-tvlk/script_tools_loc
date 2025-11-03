import csv
from LocgiApi import GeoDataService
from UserUtils import UserInput

geo_id_world = 100001
supp_check_dict = {}
modify_dict = {
    'jp': {
        'id': geo_id_world,
        'locale': 'ja_jp',
    }
}

def fetch_children(parent_geo_id, language, iso, locgi_url):
    theme_res = GeoDataService.get_geo_theme(parent_geo_id, modify_dict[language]['locale'], locgi_url)
    if theme_res:
        name = theme_res.get('name')
        local_name = theme_res.get('localName', '')
        if local_name.find('(') != -1 or local_name.find(')') != -1 or local_name.find('（') != -1 or local_name.find('）') != -1: 
            if iso not in supp_check_dict:
                supp_check_dict[iso] = []
            supp_check_dict[iso].append([language, iso, parent_geo_id, name, local_name])
    geo_regions = GeoDataService.get_children_geo_by_id(parent_geo_id, locgi_url)
    if geo_regions:
        for region in geo_regions:
            fetch_children(region.get('geoId'), language, region.get('countryISO'), locgi_url)


def main():
    env = UserInput.choose_env()
    locgi_url = UserInput.get_locgi_url(env)
    for language in modify_dict:
        geo_id = modify_dict[language]['id']
        continents = GeoDataService.get_children_geo_by_id(geo_id, locgi_url)
        for continent in continents:
            continent_id = continent.get('geoId')
            continent_name = continent.get('name')
            upper_countries = GeoDataService.get_children_geo_by_id(continent_id, locgi_url)
            print(f"Starting continent {continent_name} for language {language}")
            if not upper_countries:
                continue
            for upper_country in upper_countries:
                if upper_country.get('type') == 'COUNTRY':
                    continue
                name = upper_country.get('name')
                country_id = upper_country.get('geoId')
                fetch_children(country_id, language, upper_country.get('countryISO'), locgi_url)
                for country_code in supp_check_dict:
                    with open(f"./bracket_supp/bracket_supp_{country_code}_{language}.csv", 'w', newline='') as csvfile:
                        spamwriter = csv.writer(csvfile, delimiter=',',
                                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        spamwriter.writerow(['language', 'country-ISO', 'geoId', 'name', 'local-name', 'is-synonym'])
                        for row in supp_check_dict[country_code]:
                            spamwriter.writerow(row)
            print(f"Finished continent {continent_name} for language {language}")

if __name__ == "__main__":
    main()