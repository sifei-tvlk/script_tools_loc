import pymongo

import csv
import sys, os
import getpass
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)
from LocgiApi import LandmarkDataService
from UserUtils import UserInput

gadm_mapping_history = []

locgi_url = UserInput().get_locgi_url("production")

password = getpass.getpass("Please Enter password...")

# Simple connection
client = pymongo.MongoClient(f"mongodb://traveloka2:{password}@loc-docdb-743a4a540ac14099.cvr6biffoe7c.ap-southeast-1.docdb.amazonaws.com:27017/?retryWrites=false")
db = client["traveloka-data"]
collection = db["gadm.mapping"]

# Query and save
cursor = collection.find()

for doc in cursor:
    gadm_mapping_history.append(doc)

cursor.close()

collection = db["prompt.config"]
cursor = collection.find()

for doc in cursor:
    prompt_history.append(doc)
cursor.close()