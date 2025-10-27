import json
import os
import pandas as pd
from tqdm import tqdm

from LocgiApi import LandmarkDataService
from UserUtils import UserInput


def choose_option():
    options = ["local", "staging", "production"]
    user_input = ""

    input_message = "Pick an option:\n"

    for index, item in enumerate(options):
        input_message += f"{index + 1}) {item}\n"

    input_message += "Your choice: "

    while user_input not in map(str, range(1, len(options) + 1)):
        user_input = input(input_message)

    picked = options[int(user_input) - 1]

    print("You picked: " + picked)
    return picked


def get_path(env):
    if env == 'staging':
        return "https://locgi.loc.stg-tvlk.cloud"
    elif env == 'production':
        return "https://locgi.loc.tvlk.cloud"
    elif env == 'local':
        # only for local testing purpose
        return ""
    else:
        raise Exception('cannot find the environment {}'.format(env))


def main():
    # Choose environment; read JSONL automatically from current dir
    env = UserInput.choose_env()
    locgi_url = UserInput.get_locgi_url(env)
    cwd = os.getcwd()
    input_path = os.path.join(cwd, "test.jsonl")
    if not os.path.exists(input_path):
        print("Missing required file: filtered_aliases_result_fixed_records.jsonl in current directory.")
        return
    print(f"Reading JSONL: {input_path}")

    # Read JSONL records
    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                records.append(obj)
            except Exception:
                continue

    print(f"Loaded {len(records)} records from JSONL")

    # Process updates
    results = []
    errors = []
    for obj in tqdm(records, desc="Updating aliases"):
        landmark_id = obj.get("landmarkId")
        filtered_aliases = obj.get("filtered_aliases", [])

        if landmark_id is None:
            errors.append({"error": "missing_landmark_id", "record": obj})
            continue

        try:
            landmark = LandmarkDataService.get_landmark_by_id(landmark_id, locgi_url)
            if not landmark:
                errors.append({"error": "landmark_not_found", "landmarkId": landmark_id})
                continue
            if landmark.get('priceLevel') is None:
                landmark['priceLevel'] = 0
            # Update aliases only when present; if empty list is intended to clear, we still set it.
            if isinstance(filtered_aliases, list):
                landmark['aliases'] = filtered_aliases
            else:
                # Skip records with malformed aliases
                errors.append({"error": "malformed_filtered_aliases", "landmarkId": landmark_id, "value": filtered_aliases})
                continue

            LandmarkDataService.update_landmark(landmark, locgi_url)
            results.append({
                    "landmarkId": landmark_id,
                    "name": landmark.get("name"),
                    "updated_aliases": landmark.get("aliases", []),
                })
        except Exception as e:
            errors.append({"error": str(e), "landmarkId": landmark_id})

    # Persist results
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    os.makedirs("result", exist_ok=True)

    if results:
        pd.DataFrame(results).to_csv(f"result/{base_name}-aliases-updated.csv", index=False)
        print(f"Saved success results to result/{base_name}-aliases-updated.csv")
    if errors:
        pd.DataFrame(errors).to_csv(f"result/{base_name}-aliases-errors.csv", index=False)
        print(f"Saved error details to result/{base_name}-aliases-errors.csv")

if __name__ == "__main__":
    main()

