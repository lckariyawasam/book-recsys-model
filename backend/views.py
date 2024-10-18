from recommendations import find_similar_books
# , find_similar_items
from db import  mongodb
from recommendations import recommendations_for_user, recommendations_for_books


def get_similar(id: str, k: int = 10):
    indexes_with_scores = find_similar_books(str(id), top_k=k)
    if not indexes_with_scores:
        return []
    similar_books = []
    for index, score in indexes_with_scores:
        book = mongodb.find_one({"book_id": index}, "books")
        if book:
            book['score'] = score
            similar_books.append(book)
    return similar_books

def get_recommendations_for_user(user_id: str, k: int = 10):
    recommendations = recommendations_for_user(user_id, top_k=k)
    recommended_books = []
    for book_id, score in recommendations.items():
        book = mongodb.find_one({"book_id": book_id}, "books")
        if book:
            book['score'] = score
            recommended_books.append(book)

    if len(recommended_books) != 0:
        return recommended_books
    
    ### If the user is not included in the latest trained model, we will use the item-based recommendations
    else:
        rated_items = mongodb.ratings_collection.find({"user": user_id}, {"_id": 0, "item": 1}).sort("rating", -1).limit(10)
        book_ids = []
        if rated_items:
            for item in rated_items:
                book_ids.append(item['item'])
            return get_item_based_recommendations(book_ids, k)
        else:
            return []

def get_item_based_recommendations(book_ids: list, k: int = 10):
    recommendations = recommendations_for_books(book_ids, top_k=k)
    recommended_books = []
    # recommendations is a list of tuples (book_id, score)
    for book_id, score in recommendations:
        book = mongodb.find_one({"book_id": book_id}, "books")
        if book:
            book['score'] = score
            recommended_books.append(book)
    return recommended_books

def get_all_recommendations_for_user(user_id: str, k: int = 10):
    # Helper function to add unique recommendations
    def add_unique_recommendation(book, score):
        if book['book_id'] not in rated_book_ids and not any(rec['book_id'] == book['book_id'] for rec in recommended_books):
            book['score'] = score
            recommended_books.append(book)
    
    # Get user's rated books
    rated_items = mongodb.ratings_collection.find({"user": user_id}, {"_id": 0, "item": 1}).sort("rating", -1).limit(10)
    rated_book_ids = set(item['item'] for item in rated_items)
    
    # Get user-based recommendations
    recommendations = recommendations_for_user(user_id, top_k=k)
    recommended_books = []
    for book_id, score in recommendations.items():
        book = mongodb.find_one({"book_id": book_id}, "books")
        if book:
            add_unique_recommendation(book, score)
    
    
    # Process item-based recommendations
    item_based_recommendations = recommendations_for_books(list(rated_book_ids), top_k=10)
    for book_id, score in item_based_recommendations:
        book = mongodb.find_one({"book_id": book_id}, "books")
        if book:
            add_unique_recommendation(book, score)
    
    # Process similar books
    for book_id in rated_book_ids:
        similar_books = find_similar_books(str(book_id), 10)
        for similar_book_id, score in similar_books:
            book = mongodb.find_one({"book_id": similar_book_id}, "books")
            if book:
                add_unique_recommendation(book, score)
    
    # Sort recommendations by score in descending order
    recommended_books.sort(key=lambda x: x['score'], reverse=True)
    
    return recommended_books
