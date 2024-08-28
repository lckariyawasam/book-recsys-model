from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get MongoDB connection string and database name from environment
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]