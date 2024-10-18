import pymongo
import os
import dotenv


dotenv.load_dotenv()


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
        self.db = self.client[os.environ.get("DATABASE_NAME")]
        self.books_collection = self.db[os.environ.get("BOOKS_COLLECTION_NAME")]
        self.ratings_collection = self.db[os.environ.get("RATINGS_COLLECTION_NAME")]
        self.temp_ratings = self.db["RatedListItems"]

    def insert(self, data, collection_name):
        if collection_name == "books":
            self.books_collection.insert_one(data)
        elif collection_name == "ratings":
            self.ratings_collection.insert_one(data)

    # without _id
    def find_all(self, collection_name):
        if collection_name == "books":
            return self.books_collection.find({}, {"_id": 0})
        elif collection_name == "ratings":
            return self.ratings_collection.find({}, {"_id": 0})

    def find_one(self, query, collection_name):
        result = None
        print(query)
        if collection_name == "books":
            result = self.books_collection.find_one(query)
        elif collection_name == "ratings":
            result = self.ratings_collection.find_one(query)
        if result is not None:
            result.pop("_id")
            return result
        
        return result

    def update(self, query, data, collection_name):
        if collection_name == "books":
            self.books_collection.update_one(query, {"$set": data})
        elif collection_name == "ratings":
            self.ratings_collection.update_one(query, {"$set": data})

    def delete(self, query, collection_name):
        if collection_name == "books":
            self.books_collection.delete_one(query)
        elif collection_name == "ratings":
            self.ratings_collection.delete_one(query)


mongodb = Database()