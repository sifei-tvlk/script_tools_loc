import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

import LocgiApi import GeoDataService
from UserUtils import UserInput
import json

locgi_url = get_locgi_url('staging')

hier_dict_test = {}
hier_dict_test_file = 'hier_dict_test.json'
with open(hier_dict_test_file, 'r') as file:
    hier_dict_test = json.load(file)

sk_id = 20004311

l1_info = GeoDataService.get_children_geo_by_id(sk_id, locgi_url)
l1_ids = []

for l1 in l1_info:
    l1_id = l1.get('geoId')
    l1_ids.append([l1_id, l1.get('name')])

json.dump(l1_ids, open('l1_info.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)