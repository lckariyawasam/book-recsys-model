from bson.objectid import ObjectId
from database import db
from collaborative_filtering import cfmodel



def get_books(title_input: str):
    rating_lower_bound = 8
    title = cfmodel.search(title_input, result_count=1).values[0]
    print("The title is :", title)
    similar_users = cfmodel.get_similar_users(title, rating_threshold=rating_lower_bound)
    print("Number of similar users: ", len(similar_users))

    recommendations = cfmodel.get_recommendations_from_similar_users(similar_users, minimum_similarity=0.01, count=15, normalize=False)
    # for recommendation, score in recommendations.items():
    #     print(recommendation, score)
    
    # Return a dictionary of recommendation and score
    return recommendations.to_dict()

def get_item(item_id: str):
    print(item_id)
    return db.books.find_all()
    return db.items.find_one({"_id": ObjectId(item_id)})

def create_item(item_data):
    result = db.items.insert_one(item_data)
    return str(result.inserted_id)

def update_item(item_id: str, item_data):
    db.items.update_one({"_id": ObjectId(item_id)}, {"$set": item_data})
    return get_item(item_id)

def delete_item(item_id: str):
    db.items.delete_one({"_id": ObjectId(item_id)})
    return True