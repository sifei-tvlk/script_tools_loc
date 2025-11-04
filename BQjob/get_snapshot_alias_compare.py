import csv
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
    if row[0] not in landmark_dict:
        landmark_dict[row[0]] = {'before': set(), 'after': set()}
        after_info = LandmarkDataService().get_landmark_by_id(row[0], locgi_url)
        landmark_dict[row[0]]['after'] = set(after_info.get('alias', []))


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
collection = db["landmark"]

# Query and save
cursor = collection.find({"_id": {"$in": list(landmark_dict.keys())}})

for doc in cursor:
    landmark_dict[doc.get("_id")]['before'] = set(doc.get("alias", []))

for landmark_id in landmark_dict::
    before_aliases = landmark_dict[landmark_id]['before']
    after_aliases = landmark_dict[landmark_id]['after']
    added_aliases = after_aliases - before_aliases
    landmark_dict[landmark_id]['added'] = added_aliases