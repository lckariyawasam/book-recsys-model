from bson.objectid import ObjectId
from database import db
from collaborative_filtering import cfmodel
from vectordb import find_similar_books, find_similar_items
from db import  mongodb
import json



def search_books(title: str):
    results = cfmodel.search(title)
    print(results)
    books = []
    for result in results:
        book = cfmodel.books_df[cfmodel.books_df["Book-Title"] == result]
        book = book.to_dict(orient="records")[0]
        books.append(book)
    return books

def get_similar(id: str, k: int = 10):
    indexes_with_scores = find_similar_books(str(id), top_k=k)
    if not indexes_with_scores:
        return []
    similar_books = []
    for index, score in indexes_with_scores:
        book = mongodb.find_one({"id": index})
        if book:
            book['score'] = score
            similar_books.append(book)
    return similar_books


def get_item_based_recommendations(book_ids: list, k: int = 10):
    indexes_with_scores = find_similar_items(book_ids, top_k=k)
    if not indexes_with_scores:
        return []
    recommended_books = []
    for index, score in indexes_with_scores:
        book = mongodb.find_one({"id": int(index)})
        if book:
            book['score'] = score
            recommended_books.append(book)
    return recommended_books

def recommend_from_one(title_input: str):
    rating_lower_bound = 8
    title = cfmodel.search(title_input, result_count=1).values[0]
    print("The title is :", title)
    similar_users = cfmodel.get_similar_users(title, rating_threshold=rating_lower_bound)
    print("Number of similar users: ", len(similar_users))

    recommendations = cfmodel.get_recommendations_from_similar_users(similar_users, minimum_similarity=0.01, count=15, normalize=False)
    # for recommendation, score in recommendations.items():
    #     print(recommendation, score)
    
    # Return a dictionary of recommendation and score
    return recommendations[1:].to_dict()


def recommend_from_multiple(titles_input: list):
    titles_input = [cfmodel.search(title, result_count=1).values[0] for title in titles_input]
    rating_lower_bound = 8
    recommendations = cfmodel.get_recommendations_from_multiple_books(titles_input, rating_lower_bound, count=15)
    # for recommendation, score in recommendations.items():
    #     print(recommendation, score)
    
    # Return a dictionary of recommendation and score
    return recommendations[1:].to_dict()