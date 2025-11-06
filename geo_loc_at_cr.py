from LocgiApi import GeoDataService
from UserUtils import UserInput
import csv

world_id = 100001

result = []

def fetch_children(parent_geo, iso, locgi_url):
    parent_id = parent_geo.get('geoId')
    geo_info = GeoDataService.get_geo_region_by_id(parent_id, locgi_url)
    if geo_info:
        name = geo_info.get('name')
        usage = geo_info.get('users')
        if len(usage) == 1 and ('CAR_RENTAL' in usage or 'AIRPORT_TRANSFER' in usage):
            result.append([iso, parent_id, name, usage[0]])
    geo_regions = GeoDataService.get_children_geo_by_id(parent_id, locgi_url)
    if geo_regions:
        for region in geo_regions:
            fetch_children(region, iso, locgi_url)


def main():
    env = "production"
    locgi_url = UserInput.get_locgi_url(env)
    continents = GeoDataService.get_children_geo_by_id(world_id, locgi_url)
    for continent in continents:
        continent_id = continent.get('geoId')
        continent_name = continent.get('name')
        countries = GeoDataService.get_children_geo_by_id(continent_id, locgi_url)
        print(f"Starting continent {continent_name}")
        if not countries:
            continue
        for country in countries:
            name = country.get('name')
            print(f"Starting country {name} ")
            country_code = country.get('countryISO')
            fetch_children(country, country_code, locgi_url)
            print(f"Finished country {name} ")
        print(f"Finished continent {continent_name} ")
    with open(f"./get_at_cr.csv", 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['country-ISO', 'geoId', 'name', 'type'])
        for row in result:
            spamwriter.writerow(row)

if __name__ == "__main__":
    main()