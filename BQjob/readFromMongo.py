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
collection = db["landmark.sourcing.history"]

# One month ago timestamp
one_month_ago = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
july = datetime(2025, 7, 1, 0, 0, 0).timestamp() * 1000
august = datetime(2025, 8, 1, 0, 0, 0).timestamp() * 1000

# Query and save
query = {"country": "BQ", "__lut": {"$gte": july, '$lte': august}}
cursor = collection.find(query)

with open("bigquery_landmarks.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["name","lat", "lon", "_id", "created_date"])
    
    for doc in cursor:
        writer.writerow([
            doc.get("name", ""),
            doc.get("geoLocation", {}).get("lat", ""),
            doc.get("geoLocation", {}).get("lon", ""),
            doc.get("_id", ""),
            datetime.fromtimestamp(doc.get("__lut", 0) / 1000).strftime('%Y-%m-%d %H:%M:%S') if doc.get("__lut") else ""
        ])

print("CSV file created successfully!")