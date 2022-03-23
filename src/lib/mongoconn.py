from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017/")
dbconn = mongo_client["testdb"]
