from pinecone import Pinecone, ServerlessSpec
import dotenv
import os
import pandas as pd
import numpy as np

# Load the environment variables
dotenv.load_dotenv()

# Initialize the Pinecone client
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Define the name of the index
book_index_name = 'book-text'

# Get the index
book_index = pc.Index(book_index_name)

# Add data to the index


# Load the embeddings

embeddings = pd.read_csv('../data/trained_embeddings/item_embeddings.csv', index_col=0)

print(embeddings.head())


