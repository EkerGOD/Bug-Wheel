from pymongo import MongoClient
import config
from base import System


class MongoDB(System):
    def __init__(self):
        super().__init__()
        self.client = MongoClient(config.HOST, config.PORT)
        self.db = self.client[config.DATABASE]

    def changeDB(self, database):
        self.db = self.client[database]

    def insert(self, doc, collection=config.COLLECTION):
        col = self.db[collection]
        if isinstance(doc, list):
            insert_result = col.insert_many(doc)
        else:
            insert_result = col.insert_one(doc)

        self.systemStore.get('app').write(f"[mongoDB]{insert_result}")
        return insert_result
