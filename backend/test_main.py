# test_main.py
from fastapi.testclient import TestClient
from main import app
from pymongo import MongoClient
import dotenv
import os
import pytest

dotenv.load_dotenv()

client = TestClient(app)
mongo_client = MongoClient(os.environ.get("MONGO_URI"))

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_similar():
    k = 5
    response = client.post("/similar", json={
        "id": "1279",
        "k": k
    })
    assert response.status_code == 200
    
    response_json = response.json()

    # Check that the response returns a list
    assert type(response_json) == list
    assert len(response_json) == k


    # Check that each book object is complete
    for book in response_json:
        assert "Title" in book
        assert "authors" in book
        assert "description" in book
        assert "categories" in book
        assert "previewLink" in book
        assert "id" in book


def test_valid_recommendations():
    book_ids = ["90402","60834"]
    response = client.post("/item_recommendations", json=book_ids)

    assert response.status_code == 200

    response_json = response.json()

    assert type(response_json) == list
    for book in response_json:
        assert "Title" in book
        assert "authors" in book
        assert "description" in book
        assert "categories" in book
        assert "previewLink" in book
        assert "id" in book


def test_similar_invalid_id():
    invalid_id="invalid_id"

    k = 5
    response = client.post("/similar", json={
        "id": invalid_id,
        "k": k
    })

    assert response.status_code == 404


def test_one_invalid_book():
    book_ids = ["90402","60834", "THIS_IS_INVALID"]
    response = client.post("/item_recommendations", json=book_ids)

    # If only one id is invalid the response should still work
    assert response.status_code == 200

    response_json = response.json()

    assert type(response_json) == list
    for book in response_json:
        assert "Title" in book
        assert "authors" in book
        assert "description" in book
        assert "categories" in book
        assert "previewLink" in book
        assert "id" in book

    
def test_monogo_db_connection():
    try:
        mongo_client.admin.command('ping')
        assert True  # Connection successful
    except ConnectionError:
        pytest.fail("Could not connect to MongoDB")


def test_insert_and_retrieve():
    test_db = mongo_client["testing_db"]
    collection = test_db['ratings_temp']

    # Sample data to insert
    sample_data = {'user_id': '23423', 'book_id': 23423, "rating": 4.7}

    # Insert data
    result = collection.insert_one(sample_data)
    assert result.inserted_id is not None

    # Retrieve the document
    retrieved_data = collection.find_one({'_id': result.inserted_id})
    assert retrieved_data is not None
    assert retrieved_data['user_id'] == sample_data['user_id']
    assert retrieved_data['book_id'] == sample_data['book_id']
    assert retrieved_data["rating"] == sample_data["rating"]

    collection.drop()
    mongo_client.drop_database("test_db")

    assert True


def test_retrieve_book():
    book_id = 90402
    collection = mongo_client[os.environ.get("DATABASE_NAME")][os.environ.get("COLLECTION_NAME")]
    retrieved_book = collection.find_one({"id": book_id})

    assert "Title" in retrieved_book
    assert "authors" in retrieved_book
    assert "description" in retrieved_book
    assert "categories" in retrieved_book
    assert "previewLink" in retrieved_book
    assert "id" in retrieved_book

    mongo_client.close()