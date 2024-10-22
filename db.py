from pymongo import MongoClient
import bcrypt

# import pymongo

# create MongoDB client
client = MongoClient("mongodb://db:27017/")
db = client["user_database"]
users_collection = db["users"]


def get_collection(collection_name):
    return db[collection_name]


def get_user_by_username(username):
    return users_collection.find_one({"username": username})


def create_user(username, password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    user_data = {
        "username": username,
        "salt": salt,
        # 'password': hashed_password
    }
    users_collection.insert_one(user_data)
