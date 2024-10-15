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
        assert "Book" in book
        assert "Author" in book
        assert "Description" in book
        assert "Genres" in book
        assert "Avg_Rating" in book
        assert type(book["Avg_Rating"]) == float
        assert "URL" in book
        assert "id" in book


def test_recommendations():
    book_ids = []
    response = client.post("/recommend", json={
        "titles": book_ids
    })