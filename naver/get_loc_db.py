import sys
import os
import csv

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

from LocgiApi import GeoDataService
from UserUtils import UserInput
import json

locgi_url = UserInput.get_locgi_url('staging')

hier_dict = {}
hier_dict_file = 'hier_dict.json'
with open(hier_dict_file, 'r') as file:
    hier_dict = json.load(file)

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

def pairing_ids(level, parentId, all_sub_info, hier_info=""):
    if level == 4:
        return
    db_info = GeoDataService.get_children_geo_by_id(parentId, locgi_url)
    if not db_info:
        db_info = []
    db_active_ids = []
    for info in db_info:
        if info.get('isActive') == False:
            continue
        db_active_ids.append([info.get('geoId'), info.get('name')])
    for naver_code in all_sub_info:
        db_names = [x[1] for x in db_active_ids]
        naver_name = all_sub_info[naver_code]['en_name']
        admcode = all_sub_info[naver_code]['admcode']
        idx = query_llm(naver_name, db_names)
        if idx == -1:
            new_regions.append([admcode, naver_name, naver_code, parentId, hier_info])
        elif idx < len(db_names):
            paired_ids[level - 1].append([admcode, db_active_ids[idx][0], naver_name, db_names[idx], level, parentId, hier_info])
        else:
            print(f"Wrong output with idx: {idx}")
        pairing_ids(level + 1, db_active_ids[idx][0], all_sub_info[naver_code]['sub_regions'], f"{hier_info}/{db_names[idx]}")

paired_ids = [[], [], [], []]  # level 1 to level 4
new_regions = []
db_active_l1_ids = []

db_l1_info = GeoDataService.get_children_geo_by_id(sk_id, locgi_url)
for l1 in db_l1_info:
    if l1.get('isActive') == False:
        continue
    db_active_l1_ids.append([l1.get('geoId'), l1.get('name')])

for naver_code in hier_dict:
    db_names = [x[1] for x in db_active_l1_ids]

    naver_name = hier_dict[naver_code]['en_name']
    admcode = hier_dict[naver_code]['admcode']
    idx = query_llm(naver_name, db_names)
    if idx == -1:
        # print(f"No match for {naver_name}")
        new_regions.append([admcode, naver_name, naver_code, sk_id, ""])
    elif idx < len(db_names):
        # print(f"{naver_name} find match in db: {db_names[idx]}")
        paired_ids[0].append([admcode, db_active_l1_ids[idx][0], naver_name, db_names[idx], 1, ""])
    else:
        print(f"Wrong output with idx: {idx}")
    pairing_ids(2, db_active_l1_ids[idx][0], hier_dict[naver_code]['sub_regions'], f"{db_names[idx]}")
    
with open('pair_info.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['admcode', 'geoId', 'naver_name', 'db_name', 'level'])
    for pair in paired_ids:
        spamwriter.writerow(pair)

with open('new_region_id_list.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['admcode', 'naver_name', 'naver_code', 'level'])
    for pair in new_regions:
        spamwriter.writerow(pair)
