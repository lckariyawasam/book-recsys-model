from pinecone import Pinecone, ServerlessSpec
import dotenv
import os
import numpy as np

dotenv.load_dotenv()

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

book_index_name = os.environ.get("BOOK_TEXT_INDEX")
book_index = pc.Index(book_index_name)

item_index_name = os.environ.get("ITEM_BASED_INDEX")
item_index = pc.Index(item_index_name)

user_index_name = os.environ.get("USER_BASED_INDEX")
user_index = pc.Index(user_index_name)


