from bson.objectid import ObjectId
from database import db
from collaborative_filtering import cfmodel



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