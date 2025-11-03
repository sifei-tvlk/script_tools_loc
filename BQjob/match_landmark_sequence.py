import pymongo
import pandas as pd
import getpass
import csv
import json
from LocgiApi import LandmarkDataService, LLMService
from UserUtils import UserInput

host = input("Please Enter host info to connect MongoDB...")
username = input("Please Enter username...")
password = getpass.getpass("Please Enter password...")


if __name__ == "__main__":
    env = 'production'
    locgi_url = UserInput.get_locgi_url(env)
    query_dict = {}
    csv_file_path = "./landmark_updated_by_BQ_sorted.csv"

    with open(csv_file_path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    data = data[1:]
    for row in data:
        key, final, value = row
        if key not in query_dict:
            query_dict[key] = (value, final)
        else:
            existing_value, _ = query_dict[key]
            if value < existing_value:
                query_dict[key] = (value, final)
    # Strip out the second column, keeping only the final value
    query_dict = {k: v[1] for k, v in query_dict.items()}
    filtered_alias_by_landmark = {}
    for landmark_id, before in query_dict.items():
        print(f"{landmark_id}, {before}")
        current_landmark = LandmarkDataService.get_landmark_by_id(landmark_id, locgi_url)
        current_alias = current_landmark.get("alias", [])
        filtered_alias_by_landmark[landmark_id] = []
        for alias in current_alias:
            if alias not in before:
                filtered_alias_by_landmark[landmark_id].append(alias)
    with open(f"./filtered_aliases_by_landmark.json", 'w') as jsonfile:
        json.dump(filtered_alias_by_landmark, jsonfile, indent=4)
    print("JSON file created successfully!")
