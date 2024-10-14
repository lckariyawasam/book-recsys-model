import pymongo
import pyarrow
import pymongoarrow.monkey
from pymongoarrow.api import Schema
import dotenv
import os

dotenv.load_dotenv()

# Add extra find_* methods to pymongo collection objects:
pymongoarrow.monkey.patch_all()

# Connect to the MongoDB server
client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

# Get the database
db = client['book-rec-sys']

# Get the collection
collection = db['ratings']

# Define the schema

ratings_schema = Schema({
        'user_id': pyarrow.int32(),
        'id': pyarrow.int32(),
        'score': pyarrow.float64(),
    })

df = collection.find_pandas_all({}, schema=ratings_schema)

print(df.head())