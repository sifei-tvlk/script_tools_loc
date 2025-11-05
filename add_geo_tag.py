from LocgiApi import GeoDataService
from UserUtils import UserInput
import csv

def main():
    env = "production"
    locgi_url = UserInput.get_locgi_url(env)
    csv_file_path = "./test.csv"

    with open(csv_file_path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    for row in data:
        geoId = row[0]
        info = GeoDataService.get_geo_region_by_id(geoId, locgi_url)
        if not info:
            print(f"Cannot get info for geoId {geoId}")
        info['geoTag'][row[2]] = row[3]
        print(info['geoTag'])

if __name__ == "__main__":
    main()