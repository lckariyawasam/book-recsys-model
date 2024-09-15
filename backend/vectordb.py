from pinecone import Pinecone, ServerlessSpec
import dotenv
import os
import numpy as np

dotenv.load_dotenv()

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

book_index_name = 'book-text'
book_index = pc.Index(book_index_name)
item_index_name = 'item-based'
item_index = pc.Index(item_index_name)


def find_similar_books(book_id, top_k=10):
    query_result = book_index.query(id=book_id, top_k=top_k)
    similar_books = [(int(match['id']), match['score']) for match in query_result['matches']]
    return similar_books


def find_similar_items(book_ids, top_k=10):
    results = []
    for item_id in book_ids:
        # Query Pinecone for similar items
        response = item_index.query(id=str(item_id), top_k=top_k)
        results.extend(response['matches'])
    # Aggregate and rank results
    ranked_items = {}
    for result in results:
        item_id = result['id']
        score = result['score']
        if item_id in ranked_items:
            ranked_items[item_id].append(score)
        else:
            ranked_items[item_id] = [score]
            
    # Average scores and sort items
    averaged_scores = {item_id: np.mean(scores) for item_id, scores in ranked_items.items()}
    ranked_items = sorted(averaged_scores.items(), key=lambda x: x[1], reverse=True)
    
    recommended_items = [(item_id, score) for item_id, score in ranked_items]
    return recommended_items


if __name__ == '__main__':
    find_similar_books("522")