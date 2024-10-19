from vectordb import book_index, item_index, user_index
from LightGCN import model
import math

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

    book_ids = [int(book_id) for book_id in book_ids]
    k = math.ceil(top_k / len(book_ids) + 1)
    nearest_neighbors = []
    for book_id in book_ids:
        query_result = item_index.query(id=str(book_id), top_k=k+len(book_ids))
        similar_items = [(int(match['id']), match['score']) for match in query_result['matches'] if int(match['id']) not in book_ids]
        nearest_neighbors.extend(similar_items)
    # sort nearest_neighbors by score
    nearest_neighbors.sort(key=lambda x: x[1], reverse=True)
    if len(nearest_neighbors) > top_k:
        nearest_neighbors = nearest_neighbors[:top_k]
    return nearest_neighbors




