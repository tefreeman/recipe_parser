import random
import pymongo
from config import Config


class Tester:

    def __init__(self):
        client = pymongo.MongoClient(Config.get_mongo_address())
        self.db = client['recipes']
        self.collection_names = self.db.list_collection_names()
        self.collection_count = len(self.collection_names)

    def get_random_collection_num(self):
        return random.randint(0, self.collection_count-1)

    def get_random_recipe(self):
        collection_name = self.collection_names[self.get_random_collection_num()]
        collection = self.db[collection_name]

        cursor = collection.aggregate([{ '$sample': {'size': 1}}])
        for doc in cursor:
            return doc
