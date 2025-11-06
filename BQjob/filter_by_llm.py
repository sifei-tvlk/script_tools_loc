import sys
import os
import csv

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

from LocgiApi import LLMService
import json

def query_llm(name, aliases) -> int:
    prompt = f"You are an expert in geographical landmarks. \
    I give you a geographical landmark, \
    and another list of geographical landmark aliases, \
    find the aliases that match the landmark name. \
    There might be no match. Answer only by the aliases' names in the list\n\
    name: {name}. \n\
    List of region alias matched: [{', '.join(aliases)}].\n"
    response = LLMService.ask_llm_with_prompt(prompt, locgi_url)
    return response

with open("update_result.csv", "w", newline='', encoding="utf-8") as csvfile:
    reader = csv.reader(f)
    data = list(reader)
data = data[1:]

for row in data:
    landmark_id = row[0]
    landmark_name = row[1]
    added_aliases = json.loads(row[4].replace("'", '"'))
    
    if not added_aliases:
        continue
    
    keep_aliases = query_llm(landmark_name, after_aliases)
    remove_aliases = [alias for alias in added_aliases if alias not in keep_aliases]
    with open("landmark_llm_match.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([landmark_id, landmark_name, added_aliases, keep_aliases, remove_aliases])
    print(f"Landmark ID {landmark_id} processed, LLM match index: {match_index}")