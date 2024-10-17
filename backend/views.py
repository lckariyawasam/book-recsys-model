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
    return recommended_books

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
