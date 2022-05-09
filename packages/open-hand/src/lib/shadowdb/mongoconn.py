from typing import Any

from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection

from lib.predef.config import get_config

from bson.raw_bson import RawBSONDocument

MCollection = Collection[RawBSONDocument]


class MongoDB:
    client: MongoClient[RawBSONDocument]
    dbname: str
    db: Database[Any]

    papers: MCollection
    signatures: MCollection
    clusters: MCollection
    profiles: MCollection
    equivalence: MCollection

    def __init__(self):
        config = get_config()
        connUrl = config.mongodb.connectionUrl
        self.client: MongoClient[RawBSONDocument] = MongoClient(connUrl, document_class=RawBSONDocument)
        self.dbname = config.mongodb.dbName
        self.db = self.client[self.dbname]
        self.papers: MCollection = self.db.papers
        self.signatures: MCollection = self.db.signatures
        self.clusters: MCollection = self.db.clusters
        self.profiles: MCollection = self.db.profiles
        self.equivalence: MCollection = self.db.equivalence

    def reset_db(self):
        self.client.drop_database(self.dbname)
        self.create_collections()

    def create_collections(self):
        self.papers.create_index("id", unique=True)

        self.signatures.create_index("paper_id")
        self.signatures.create_index("signature_id", unique=True)
        self.signatures.create_index("author_info.block")

        self.clusters.create_index("cluster_id")
        self.clusters.create_index("signature_id")
        self.clusters.create_index("canopy")

        self.profiles.create_index("id", unique=True)

        self.equivalence.create_index("ids")
