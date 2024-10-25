from vectordb import book_index, item_index, user_index
from LightGCN import model
import math
import numpy as np

def find_similar_books(book_id, top_k=10):
    try:
        query_result = book_index.query(id=book_id, top_k=top_k)
        similar_books = [(int(match['id']), match['score']) for match in query_result['matches']]
        return similar_books
    except Exception as e:
        print(f"Error finding similar books: {e}")
        return []

def recommendations_for_user(user_id, top_k=10):
    try:
        user_id = int(user_id)
        results = model.recommend_user(user=user_id, n_rec=top_k, cold_start='popular')
        # Ensure results[user_id] is a list
        books_ids = results[user_id].tolist() if hasattr(results[user_id], 'tolist') else [results[user_id]]
        scores = []
        for book_id in books_ids:
            score = model.predict(user=user_id, item=book_id)
            # score is float32 array, we need to convert it to float
            score = float(score)
            scores.append(score)
        recommendations = {}
        for book_id, score in zip(books_ids, scores):
            recommendations[book_id] = score
        return recommendations
    except Exception as e:
        print(f"Error finding recommendations for user: {e}")
        return {}

def recommendations_for_books(book_ids, top_k=10):
    if len(book_ids) == 0:
        return []  # Return an empty list if no book_ids are provided

    # Convert book_ids to integers
    book_ids = [int(book_id) for book_id in book_ids]

    # Get embeddings for each book
    embeddings = [model.get_item_embedding(book_id) for book_id in book_ids]

    # Calculate average embedding
    avg_embedding = np.mean(embeddings, axis=0)

    # Query Pinecone index with the average embedding
    query_result = item_index.query(vector=avg_embedding.tolist(), top_k=top_k+len(book_ids))

    # Process results, excluding input books
    nearest_neighbors = [
        (int(match['id']), match['score']) 
        for match in query_result['matches'] 
        if int(match['id']) not in book_ids
    ]

    # Trim to top_k results if necessary
    return nearest_neighbors[:top_k]




