import pymongo
import csv
import sys, os
import getpass
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)
from LocgiApi import LandmarkDataService
from UserUtils import UserInput

landmark_dict = {}

locgi_url = UserInput().get_locgi_url("production")

csv_file_path = "landmark_updated_by_BQ.csv"
with open(csv_file_path, newline='') as f:
    reader = csv.reader(f)
    data = list(reader)
data = data[1:]
for row in data:
    ids = row[0]
    if ids not in landmark_dict:
        landmark_dict[ids] = {'before': set(), 'after': set()}
        after_info = LandmarkDataService().get_landmark_by_id(ids, locgi_url)
        landmark_dict[ids]['after'] = set(after_info.get('aliases', []))

password = getpass.getpass("Please Enter password...")

# Simple connection
client = pymongo.MongoClient(f"mongodb://root:{}@docdb-2025-11-03-14-00-48.cvr6biffoe7c.ap-southeast-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false")
db = client["traveloka-data"]
collection = db["landmark"]

# Query and save
cursor = collection.find({"_id": ""})

for doc in cursor:
    landmark_dict[doc.get("_id")]['before'] = set(doc.get("alias", []))

for landmark_id in landmark_dict:
    before_aliases = landmark_dict[landmark_id]['before']
    after_aliases = landmark_dict[landmark_id]['after']
    added_aliases = after_aliases - before_aliases
    landmark_dict[landmark_id]['added'] = added_aliases