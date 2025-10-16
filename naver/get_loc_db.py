import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

from LocgiApi import GeoDataService
from UserUtils import UserInput
import json

locgi_url = UserInput.get_locgi_url('staging')

hier_dict_test = {}
hier_dict_test_file = 'hier_dict_test.json'
with open(hier_dict_test_file, 'r') as file:
    hier_dict_test = json.load(file)

sk_id = 20004311

def query_llm(name_naver, list_db_name) -> int:
    prompt = f"You are an expert in korean administrative geography. \
    I give you a korean first level administrative region, \
    and another list of first level administrative region alias, \
    find the best match region in the list for the given region. \
    There might be no best match. Answer only by the index in the list, or -1 if no best match. \n\
    Given region: {name_naver}. \n\
    List of region alias: [{', '.join(list_db_name)}].\n"
    response = GeoDataService.get_response_by_prompt(prompt, locgi_url)
    return int(response)

l1_info = GeoDataService.get_children_geo_by_id(sk_id, locgi_url)
l1_ids = []

for l1 in l1_info:
    l1_id = l1.get('geoId')
    l1_ids.append([l1_id, l1.get('name')])

json.dump(l1_ids, open('l1_info.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

hier_dict_test = {}
hier_dict_test_file = 'hier_dict_test.json'
with open(hier_dict_test_file, 'r') as file:
    hier_dict_test = json.load(file)

pair_ids = []
new_regions = []

for naver_code in hier_dict_test:
    db_names = [x[1] for x in l1_ids]
    naver_name = hier_dict_test[naver_code]['en_name']
    admcode = hier_dict_test[naver_code]['admcode']
    idx = query_llm(naver_name, db_names)
    if idx == -1:
        # print(f"No match for {naver_name}")
        new_regions.append([admcode, naver_name, naver_code])
    elif idx < len(db_names):
        # print(f"{naver_name} find match in db: {db_names[idx]}")
        pair_ids.append([admcode, l1_ids[idx][0], naver_name, db_names[idx]])
    else:
        print(f"Wrong output with idx: {idx}")
print("pair ids:")
for pair in pair_ids:
    print(pair)
json.dump(pair_ids, open('l1_pair_info.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

print("new regions:")
print(new_regions)
json.dump(new_regions, open('new_region_id_list.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
