from vectordb import find_similar_books
from db import  Database


db = Database()


indexes = find_similar_books("522")

for index in indexes:
    print(db.find_one({"id": index}))


# print(len(list(db.find_all())))

