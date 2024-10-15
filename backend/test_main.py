# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


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
        # assert "Avg_Rating" in book
        # assert type(book["Avg_Rating"]) == float
        assert "previewLink" in book
        assert "id" in book


def test_recommendations():
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
        # assert "Avg_Rating" in book
        # assert type(book["Avg_Rating"]) == float
        assert "previewLink" in book
        assert "id" in book