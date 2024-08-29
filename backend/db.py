import pymongo
import os
import dotenv


dotenv.load_dotenv()


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
        self.db = self.client[os.environ.get("DATABASE_NAME")]
        self.collection = self.db[os.environ.get("COLLECTION_NAME")]

    def insert(self, data):
        self.collection.insert_one(data)

    def find_all(self):
        return self.collection.find()

    def find_one(self, query):
        result = self.collection.find_one(query)
        if result:
            result.pop("_id")
            return result
        
        return result

    def update(self, query, data):
        self.collection.update_one(query, {"$set": data})

    def delete(self, query):
        self.collection.delete_one(query)


mongodb = Database()