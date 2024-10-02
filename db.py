from pymongo import MongoClient

# create MongoDB client
client = MongoClient('mongodb://localhost:27017/')
db = client['weekFour']  

def get_collection(collection_name):
    return db[collection_name]
