from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import json
import time
import copy
from urllib.parse import urlparse, parse_qs

base_x = 126.99080268424797
base_y = 37.56655100000084
zoom = 13
region_to_polygon = {}

available_code_file = 'available_code.json'
available_code = {}
with open(available_code_file, 'r') as file:
    available_code = json.load(file)
    
url = f"https://map.naver.com/p?c={zoom},0,0,0,dh"

# Start Chrome with Selenium 4
options = webdriver.ChromeOptions()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
driver = webdriver.Chrome(options)

# Enable network tracking
driver.execute_cdp_cmd("Network.enable", {})

driver.get(url) 
polygon_url = lambda k: f"https://map.naver.com/p/api/polygon?lng={base_x}&lat={base_y}&order=adm&keyword={k}&zoom=13"

def get_region_json(k):
    area_url = polygon_url(k)
    polygon = driver.execute_async_script(f"""
    let polygon_url = "{area_url}";
    const callback = arguments[arguments.length - 1];
    let xhr = new XMLHttpRequest();
    xhr.open('GET', polygon_url);
    console.log(polygon_url);
    xhr.onreadystatechange = function() {{
        if (xhr.readyState === 4 && xhr.status === 200) {{
            console.log(xhr.readyState, xhr.status, xhr.responseText);
            let responseData = JSON.parse(xhr.responseText);
            console.log(responseData);
            callback(responseData);
        }} else if (xhr.status !== 200) {{
            console.error('Error fetching data');
        }}
    }};
    xhr.send();""")
    return polygon

hier_dict_test = {}
hier_dict_test_file = 'hier_dict_test.json'
with open(hier_dict_test_file, 'r') as file:
    hier_dict_test = json.load(file)

def get_name(features):
    properties = features[0].get('properties', {})
    if properties.get('area4'):
        return features[0].get('properties', {}).get('area4')
    if properties.get('area3'):
        return features[0].get('properties', {}).get('area3')
    if properties.get('area2'):
        return features[0].get('properties', {}).get('area2')
    return features[0].get('properties', {}).get('area1')

# Level 1
for i in range(1, 20):
    naver_code = str(i).zfill(2)
    print(naver_code)
    data = get_region_json(str(i).zfill(2))
    features = data.get('features', [])
    if not features:
        continue
    name = get_name(features)
    admcode = features[0].get('properties', {}).get('admcode')
    print(admcode)
    if not admcode:
        continue
    if str(i).zfill(2) not in available_code.keys():
        available_code[str(i).zfill(2)] = {}
    region_to_polygon[admcode] = data
    file_path = f"./geojson/area1/{admcode}_polygon.json"
    time.sleep(0.1)
    if name not in hier_dict_test.keys() and naver_code not in hier_dict_test.keys():
        hier_dict_test[naver_code] = {"admcode": admcode, "kr_name": name, "coords": [features[0].get('properties', {}).get('center').get('x'), features[0].get('properties', {}).get('center').get('y')], "sub_regions": {}}
    if name in hier_dict_test.keys():
        hier_dict_test[naver_code] = copy.deepcopy(hier_dict_test[name])
        hier_dict_test[naver_code]["admcode"] = admcode
        # hier_dict_test[naver_code]["coords"] = [features[0].get('properties', {}).get('center').get('x'), features[0].get('properties', {}).get('center').get('y')]
        hier_dict_test.pop(name)
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(region_to_polygon[admcode], json_file, indent=4, ensure_ascii=False)

for l1_naver_code in available_code.keys():
    if available_code[l1_naver_code] == {}:
        idxs = list(range(100, 1000))
    else:
        idxs = available_code[l1_naver_code].keys()
    for i in idxs:
        navercode = l1_naver_code + str(i).zfill(3)
        try:
            data = get_region_json(navercode)
            features = data.get('features', [])
            if not features:
                continue
            admcode = features[0].get('properties', {}).get('admcode')
            print(navercode, admcode)
            if not admcode:
                continue
            if navercode not in available_code[l1_naver_code].keys():
                available_code[l1_naver_code][navercode] = {}
            region_to_polygon[admcode] = data
            if name not in hier_dict_test[l1_naver_code]['sub_regions'].keys() and admcode not in hier_dict_test[l1_naver_code]['sub_regions'].keys():
                hier_dict_test[l1_naver_code]['sub_regions'][naver_code] = {"kr_name": name, "coords": [features[0].get('properties', {}).get('center').get('x'), features[0].get('properties', {}).get('center').get('y')], "sub_regions": {}}
            if name in hier_dict_test[l1_naver_code]['sub_regions'].keys():
                hier_dict_test[l1_naver_code]['sub_regions'][naver_code] = copy.deepcopy(hier_dict_test[l1_naver_code]['sub_regions'][name])
                hier_dict_test[l1_naver_code]['sub_regions'][naver_code]["admcode"] = admcode
                # hier_dict_test[admcode]["coords"] = [features[0].get('properties', {}).get('center').get('x'), features[0].get('properties', {}).get('center').get('y')]
                hier_dict_test[l1_naver_code]['sub_regions'].pop(name)
            file_path = f"./geojson/area2/{admcode}_polygon.json"
            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(region_to_polygon[admcode], json_file, indent=4, ensure_ascii=False)
            time.sleep(0.1)
        except:
            break

with open(available_code_file, "w", encoding="utf-8") as json_file:
    json.dump(available_code, json_file, indent=4, ensure_ascii=False)

with open(hier_dict_test_file, "w", encoding="utf-8") as json_file:
    json.dump(hier_dict_test, json_file, indent=4, ensure_ascii=False)