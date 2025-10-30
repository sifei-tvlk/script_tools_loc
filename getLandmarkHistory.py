import pymongo
import csv
from datetime import datetime, timedelta, date
import getpass

host = input("Please Enter host info to connect MongoDB...")
username = input("Please Enter username...")
password = getpass.getpass("Please Enter password...")

# Simple connection
client = pymongo.MongoClient(
    host=host,           # e.g., "localhost" or "mongodb://localhost:27017"
    port=27017,                 # MongoDB port
    username=username,   # Your MongoDB username
    password=password,   # Your MongoDB password
    authSource="admin"          # Database where user is defined (usually "admin")
)
db = client["traveloka-data"]
collection = db["landmark.history"]

user = "landmarkSourcingFromBQ"

# One month ago timestamp
start_time = int(datetime(2025, 6, 1, 0, 0, 0).timestamp() * 1000)
end_time = int((datetime.now()).timestamp() * 1000)

# Query and save
query = {"user": "landmarkSourcingFromBQ", "__lut": {"$gte": start_time, '$lte': end_time}}
cursor = collection.find(query)

query_data = []

with open("landmark_updated_by_BQ.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["landmarkId", "before", "created_date"])

    for doc in cursor:
        row = [
            doc.get("landmarkId", ""),
            doc.get("before", {}),
            datetime.fromtimestamp(doc.get("__lut", 0) / 1000).strftime('%Y-%m-%d %H:%M:%S') if doc.get("__lut") else ""
        ]
        writer.writerow(row)
        query_data.append(row)

query_data.sort(key=lambda x: (x[0], x[2]))
query_dict = {}
with open(f"./landmark_updated_by_BQ_sorted.csv", 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['landmarkId', 'before', 'created_date'])
    for row in query_data:
        if row[0] not in query_dict:
            query_dict[row[0]] = row
        spamwriter.writerow(row)
        key, value, final = row
        if key not in query_dict:
            query_dict[key] = (value, final)
        else:
            existing_value, _ = query_dict[key]
            if value < existing_value:
                query_dict[key] = (value, final)
    # Strip out the second column, keeping only the final value
    query_dict = {k: v[1] for k, v in query_dict.items()}
with open("landmark_updated_by_BQ_sorted.json", "w") as f:
    json.dump(query_dict, f, indent=4)
print("CSV file created successfully!")
