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
                    if not area2:
                        return
                    if area2 not in hier_dict[area1]:
                        hier_dict[area1][area2] = {}
                    if not area3:
                        return
                    if area3 not in hier_dict[area1][area2]:
                        hier_dict[area1][area2][area3] = []
                    if area4:
                        hier_dict[area1][area2][area3].append(area4)
            except Exception as e:
                print("Could not get body for", url, e)

url = "https://map.naver.com/p?c={zoom},0,0,0,dh"

# Start Chrome with Selenium 4
options = webdriver.ChromeOptions()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
driver = webdriver.Chrome(options)

# Enable network tracking
driver.execute_cdp_cmd("Network.enable", {})

driver.get(url) 

for i in range(1):
    x_coord = base_x + i * 0.001
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
    let areas = [];
    xhr.onreadystatechange = function() {{
        if (xhr.readyState === 4 && xhr.status === 200) {{
            let responseData = JSON.parse(xhr.responseText);
            let region = responseData.results[0].region;
            let area1 = region.area1.name;
            let area2 = region.area2.name;
            let area3 = region.area3.name;
            let area4 = region.area4.name;
            areas = [area1, area2, area3, area4];
            console.log(areas);
            callback(areas);
        }} else {{
            console.log(xhr.readyState, xhr.status, xhr.responseText);
            console.error('Error fetching data');
        }}
    }}
    xhr.send();
    """)
    if not areas[0]:
        continue
    if areas[0] not in hier_dict:
        hier_dict[areas[0]] = {}
        region_to_coord[areas[0]] = (x_coord, y_coord)
    if not areas[1]:
        continue
    if areas[1] not in hier_dict[areas[0]]:
        hier_dict[areas[0]][areas[1]] = {}
        region_to_coord[areas[1]] = (x_coord, y_coord)
    if not areas[2]:
        continue
    if areas[2] not in hier_dict[areas[0]][areas[1]]:
        hier_dict[areas[0]][areas[1]][areas[2]] = []
        region_to_coord[areas[2]] = (x_coord, y_coord)
    if areas[3]:
        hier_dict[areas[0]][areas[1]][areas[2]].append(areas[3])
        region_to_coord[areas[3]] = (x_coord, y_coord)
print(hier_dict)
file_path = f"./hier_dict.json"
with open(file_path, "w") as json_file:
    json.dump(hier_dict, json_file, indent=4)

polygon_url = lambda x, y: f"https://map.naver.com/p/api/polygon?lng={x}&lat={y}&order=adm&keyword=09140&zoom=14"

def get_region_json(area):
    area_url = polygon_url(*region_to_coord[area])
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

for area in region_to_coord:
    if area in region_to_polygon.keys():
        continue
    region_to_polygon[area] = get_region_json(area)
    file_path = f"./geojson/{area}_polygon.json"
    with open(file_path, "w") as json_file:
        json.dump(region_to_polygon[area], json_file, indent=4)

print(region_to_polygon)

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
