import json
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime
URI = "mongodb+srv://davepierre:Legoat23!@transactions.ghvzvld.mongodb.net/"
TEST_URI="mongodb://localhost:27017/"
TEST=False
# Connect to MongoDB
def loadData():

    try:
        collection=getTfsaLimitsTable()
 
        # Read TFSA limits data from JSON file
        with open("tfsa_limits.json", "r") as file:
            tfsa_limits_data = json.load(file)

        # Insert TFSA limits data into MongoDB
        collection.insert_many(tfsa_limits_data)

        print("TFSA limits data imported successfully.")
    except Exception as e:
        print(e)


def getTfsaLimitsTable():
    db = getTfsaDb()
    return db["tfsa_limits"]
def getTfsaDb():
    if(TEST):
        client=pymongo.MongoClient(URI)
    else:
        client= MongoClient(URI, server_api=ServerApi('1'))
    db = client["tfsa_db"]
    return db
def deleteTfsaLimitsConnection():
    # Connect to MongoDB
    db = getTfsaDb()
    # Drop the collection
    db.drop_collection("tfsa_limits")

    print("Collection 'tfsa_limits' dropped successfully.")


#to be used if the other function is not in used
def calculate_contribution_room2(start_year):
    tfsa_limits = {
        2009: 5000,
        2010: 5000,
        2011: 5000,
        2012: 5000,
        2013: 5500,
        2014: 5500,
        2015: 10000,
        2016: 5500,
        2017: 5500,
        2018: 5500,
        2019: 6000,
        2020: 6000,
        2021: 6000,
        2022: 6000,
        2023: 6500,
        2024: 7000
    }

    if start_year in tfsa_limits:
        total_limit = sum(tfsa_limits[year] for year in range(start_year, 2025))
        return total_limit
    else:
        return "Invalid start year"

# Function to calculate TFSA contribution room
def calculate_contribution_room(start_year):
    total_limit = 0
    collection= getTfsaLimitsTable()
    for year in range(start_year, 2025):
        limit_doc = collection.find_one({"year": year})
        if limit_doc:
            total_limit += limit_doc["dollar_limit"]
        else:
            return "Invalid start year"
    return total_limit




if __name__ == "__main__":
   print(calculate_contribution_room(2016))
