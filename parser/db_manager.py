import pymongo
from pymongo import CursorType
from typing import List
from config import Config


class DbManager:
    client = pymongo.MongoClient(Config.get_mongo_address())

    def __init__(self, db_name: str, col_name: str, batch_limit: int = 1000):
        self.db = DbManager.client[db_name]
        self.collection = self.db[col_name]
        self.batch_inserts = []
        self.batch_insert_count = 0
        self.batch_limit = batch_limit

    def add_doc(self, doc: any):
        if self.batch_insert_count > self.batch_limit:
            self._batch_insert()
        self.batch_inserts.append(doc)
        self.batch_insert_count += 1

    def add_docs(self, docs: List):
        self.batch_inserts.extend(docs)
        self.batch_insert_count += len(docs)
        self._batch_insert()

    def _batch_insert(self):
        self.collection.insert_many(self.batch_inserts)
        self.batch_inserts.clear()
        self.batch_insert_count = 0

    def get_all(self) -> List:
        return self.collection.find({}).toArray()

    def get_all_as_cursor(self) -> CursorType:
        return self.collection.find()

