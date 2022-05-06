from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017/")
dbconn = mongo_client["testdb"]


class Coll:
    papers = dbconn.papers
    signatures = dbconn.signatures
    clusters = dbconn.clusters
