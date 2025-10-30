import pymongo
import pandas as pd
import getpass
import csv
import json

host = input("Please Enter host info to connect MongoDB...")
username = input("Please Enter username...")
password = getpass.getpass("Please Enter password...")


def match_landmarks_simple():
    # MongoDB connection
    client = pymongo.MongoClient(
        host=host,
        port=27017,
        username=username,
        password=password,
        authSource="admin"
    )
    
    db = client["traveloka-data"]
    landmark_collection = db["landmark"]
    
    # Read CSV file
    csv_file_path = "./landmark_updated_by_BQ_sorted.csv"
    print("Reading CSV file...")
    df = pd.read_csv(csv_file_path)
    print(f"Loaded {len(df)} records from CSV")
    
    
    matched_count = 0
    
    print("Starting matching process...")
    
    # Create a list to store all results (one CSV row can have multiple matches)
    all_results = []
    
    for index, row in df.iterrows():
        if index % 1 == 0:
            print(f"Processing record {index + 1}/{len(df)}")
        
        csv_name = str(row['name']).strip()
        csv_lat = row['lat']
        csv_lon = row['lon']
        
        # Find ALL landmarks with this name in MongoDB
        landmarks = list(landmark_collection.find({"name": csv_name}))
        
        for landmark in landmarks:
            mongo_lat = landmark.get('geoLocation', {}).get('lat')
            mongo_lon = landmark.get('geoLocation', {}).get('lon')
            
            # Check if coordinates match (with small tolerance for floating point)
            if (mongo_lat is not None and mongo_lon is not None and 
                abs(csv_lat - mongo_lat) < 0.0001 and 
                abs(csv_lon - mongo_lon) < 0.0001):
                
                # Create a new row for each match
                result_row = row.copy()
                result_row['landmarkId'] = str(landmark.get('_id', ''))
                result_row['aliases'] = ', '.join(landmark.get('aliases', []))
                all_results.append(result_row)
                matched_count += 1
                break
        with open('./match_progress.txt', 'w') as progress_file:
            progress_file.write(f"Processed {index + 1} of {len(df)} records. Matches found: {matched_count}\n")
    
    print(f"\nMatching completed!")
    print(f"Original CSV records: {len(df)}")
    print(f"Total matches found: {matched_count}")
    print(f"Output records: {len(all_results)}")
    
    # Convert results to DataFrame and save
    if all_results:
        result_df = pd.DataFrame(all_results)
        output_file = "./withLandmarkId.csv"
        print(f"\nSaving updated CSV to: {output_file}")
        result_df.to_csv(output_file, index=False)
    else:
        print("No matches found!")
        output_file = None
    
    client.close()
    return output_file

if __name__ == "__main__":
    query_dict = {}
    csv_file_path = "./landmark_updated_by_BQ_sorted.csv"

    with open(csv_file_path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    for row in data:
        key, value, final = row
        if key not in query_dict:
            query_dict[key] = (value, final)
        else:
            existing_value, _ = query_dict[key]
            if value < existing_value:
                query_dict[key] = (value, final)
    # Strip out the second column, keeping only the final value
    query_dict = {k: v[1] for k, v in query_dict.items()}

    # match_landmarks_simple()
