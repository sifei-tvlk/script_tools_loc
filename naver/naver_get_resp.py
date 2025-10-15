from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import json
import time
from urllib.parse import urlparse, parse_qs

base_x = 126.99080268424797
base_y = 37.56655100000084
zoom = 13
hier_dict = {}
region_to_coord = {}
region_to_polygon = {}

hier_dict = {}
hier_dict_file = 'hier_dict.json'
with open(hier_dict_file, 'r') as file:
    hier_dict = json.load(file)

hier_dict_test = {}
hier_dict_test_file = 'hier_dict_test.json'
with open(hier_dict_test_file, 'r') as file:
    hier_dict_test = json.load(file)

def parse_coords(url: str):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    
    # Get coords parameter
    coords_str = query.get("coords", [None])[0]
    if not coords_str:
        raise ValueError("No 'coords' parameter found in URL")

    # Split into lon, lat
    lon_str, lat_str = coords_str.split(",")
    return lon_str, lat_str

def move_left(driver):
    clickable = driver.find_element(By.CLASS_NAME, "mapboxgl-canvas")
    clickable.click()
    ActionChains(driver).key_down(Keys.ARROW_LEFT).perform()
    time.sleep(0.1)
    ActionChains(driver).key_up(Keys.ARROW_LEFT).perform()

def move_right(driver):
    clickable = driver.find_element(By.CLASS_NAME, "mapboxgl-canvas")
    clickable.click()
    ActionChains(driver).key_down(Keys.ARROW_RIGHT).perform()
    time.sleep(0.1)
    ActionChains(driver).key_up(Keys.ARROW_RIGHT).perform()

def get_response(driver):
    # Grab performance logs
    logs = driver.get_log("performance")
    print('///////////////////////')
    # print(logs)

    for entry in logs:
        msg = json.loads(entry["message"])["message"]

        # Look for network responses
        if msg["method"] == "Network.responseReceived":
            url = msg["params"]["response"]["url"]
            req_id = msg["params"]["requestId"]

            # Filter for the requests you care about
            if "coord" not in url:
                continue
            try:
                body = driver.execute_cdp_cmd(
                    "Network.getResponseBody",
                    {"requestId": req_id}
                )
                # print("URL:", url)
                # print("Body:", body["body"])
                results = json.loads(body["body"]).get('results')
                print(parse_coords(url))
                for result in results:
                    area1 = result.get("region").get('area1').get('name')
                    area2 = result.get("region").get('area2').get('name')
                    area3 = result.get("region").get('area3').get('name')
                    area4 = result.get("region").get('area4').get('name')
                    print(area1, area2, area3, area4)
                    if not area1:
                        return
                    if area1 and area1 not in hier_dict:
                        hier_dict[area1] = {}
                        hier_dict_test[area1] = {"kr_name": area1, "sub_regions": {}}
                    if not area2:
                        return
                    if area2 not in hier_dict[area1]:
                        hier_dict[area1][area2] = {}
                        hier_dict_test[area1]["sub_regions"][area2] = {"kr_name": area2, "sub_regions": {}}
                    if not area3:
                        return
                    if area3 not in hier_dict[area1][area2]:
                        hier_dict[area1][area2][area3] = []
                        hier_dict_test[area1]["sub_regions"][area2]["sub_regions"][area3] = {"kr_name": area3, "sub_regions": {}}
                    if area4:
                        hier_dict[area1][area2][area3].append(area4)
                        hier_dict_test[area1]["sub_regions"][area2]["sub_regions"][area3]["sub_regions"][area4] = {"kr_name": area4, "sub_regions": {}}
            except Exception as e:
                print("Could not get body for", url, e)

url = f"https://map.naver.com/p?c={zoom},0,0,0,dh"

# Start Chrome with Selenium 4
options = webdriver.ChromeOptions()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
driver = webdriver.Chrome(options)

# Enable network tracking
driver.execute_cdp_cmd("Network.enable", {})

driver.get(url) 

for i in range(100):
    x_coord = base_x + i * 0.01
    y_coord = base_y
    time.sleep(5)
    areas = driver.execute_async_script(f"""
    const callback = arguments[arguments.length - 1];
    let xhr = new XMLHttpRequest();
    let x = {x_coord};
    let y = {y_coord};
    let url = `https://map.naver.com/p/api/location/geocode?coords=${{x}},${{y}}&orders=admcode,legalcode`;
    console.log(url);
    xhr.open('GET', url);
    let areas = new Map();
    xhr.onreadystatechange = function() {{
        if (xhr.readyState === 4 && xhr.status === 200) {{
            let responseData = JSON.parse(xhr.responseText);
            let region = responseData.results[0].region;
            areas.set("l1", [region.area1.name, region.area1.coords.center.x, region.area1.coords.center.y]);
            areas.set("l2", [region.area2.name, region.area2.coords.center.x, region.area2.coords.center.y]);
            areas.set("l3", [region.area3.name, region.area3.coords.center.x, region.area3.coords.center.y]);
            if (region.area4.name !== "") {{
                areas.set("l4", [region.area4.name, region.area4.coords.center.x, region.area4.coords.center.y]);
            }}
            const obj = Object.fromEntries(areas);
            console.log(obj);
            callback(obj);
        }} else {{
            console.log(xhr.readyState, xhr.status, xhr.responseText);
            console.error('Error fetching data');
        }}
    }}
    xhr.send();
    """)
    print(areas)
    if not areas.get("l1"):
        continue
    if areas.get("l1")[0] not in hier_dict:
        hier_dict[areas.get("l1")[0]] = {}
        region_to_coord[areas.get("l1")[0]] = (areas.get("l1")[1], areas.get("l1")[2])
        hier_dict_test[areas.get("l1")[0]] = {"kr_name": areas.get("l1")[0], "coords": [areas.get("l1")[1], areas.get("l1")[2]], "sub_regions": {}}
    if not areas.get("l2"):
        continue
    if areas.get("l2")[0] not in hier_dict[areas.get("l1")[0]]:
        hier_dict[areas.get("l1")[0]][areas.get("l2")[0]] = {}
        region_to_coord[areas.get("l2")[0]] = (areas.get("l2")[1], areas.get("l2")[2])
        hier_dict_test[areas.get("l1")[0]]["sub_regions"][areas.get("l2")[0]] = {"kr_name": areas.get("l2")[0], "coords": [areas.get("l2")[1], areas.get("l2")[2]], "sub_regions": {}}
    if not areas.get("l3"):
        continue
    if areas.get("l3")[0] not in hier_dict[areas.get("l1")[0]][areas.get("l2")[0]]:
        hier_dict[areas.get("l1")[0]][areas.get("l2")[0]][areas.get("l3")[0]] = []
        region_to_coord[areas.get("l3")[0]] = (areas.get("l3")[1], areas.get("l3")[2])
        hier_dict_test[areas.get("l1")[0]]["sub_regions"][areas.get("l2")[0]]["sub_regions"][areas.get("l3")[0]] = {"kr_name": areas.get("l3")[0], "coords": [areas.get("l3")[1], areas.get("l3")[2]], "sub_regions": {}}
    if areas.get("l4"):
        hier_dict[areas.get("l1")[0]][areas.get("l2")[0]][areas.get("l3")[0]].append(areas.get("l4")[0])
        region_to_coord[areas.get("l4")[0]] = (areas.get("l4")[1], areas.get("l4")[2])
        hier_dict_test[areas.get("l1")[0]]["sub_regions"][areas.get("l2")[0]]["sub_regions"][areas.get("l3")[0]][areas.get("l4")[0]] = {"kr_name": areas.get("l4")[0], "coords": [areas.get("l4")[1], areas.get("l4")[2]], "sub_regions": {}}
        
print(hier_dict)
with open(hier_dict_file, "w", encoding="utf-8") as json_file:
    json.dump(hier_dict, json_file, indent=4, ensure_ascii=False)
with open(hier_dict_test_file, "w", encoding="utf-8") as json_file:
    json.dump(hier_dict_test, json_file, indent=4, ensure_ascii=False)
file_path = f"./region_coord.json"
with open(file_path, "w", encoding="utf-8") as json_file:
    json.dump(region_to_coord, json_file, indent=4, ensure_ascii=False)

polygon_url = lambda x, y, k, z: f"https://map.naver.com/p/api/polygon?lng={x}&lat={y}&order=adm&keyword={k}&zoom={z}"

print(region_to_coord)

# deprecated 
# retrieve area data by moving map with arrow keys
# time.sleep(5)
# get_response(driver)
# clickable = None
# cnt = 0
# while not clickable and cnt < 1000:
#     clickable = driver.find_element(By.CLASS_NAME, "mapboxgl-canvas")
#     cnt += 1
#     time.sleep(0.01)
# print("cnt>>>>>>>>>>>", cnt)

# driver.quit()
