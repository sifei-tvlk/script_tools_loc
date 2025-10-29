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

query_data.sort(key=lambda x: x[0])
with open(f"./landmark_updated_by_BQ_sorted.csv", 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['language', 'country-code', 'geoId', 'name', 'local-name', 'trimmed-name'])
    for row in query_data:
        spamwriter.writerow(row)
print("CSV file created successfully!")
