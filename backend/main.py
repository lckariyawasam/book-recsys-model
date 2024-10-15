from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from models import BookRequest
from typing import List
import views

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/similar")
def get_similar_books(book: BookRequest, response: Response):
    id = book.id
    k = book.k
    recommendations =  views.get_similar(id, k)

    if len(recommendations) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return recommendations
    else:
        return recommendations

@app.post("/item_recommendations")
def get_item_recommendations(book_ids: List[str]):
    result = views.get_item_based_recommendations(book_ids)
    return result


@app.post("/recommend")
def recommend_books(titles: List[str]):
    print(titles)
    result = views.recommend_from_multiple(titles)
    return result


@app.get("/search")
def search_books(title: str):
    result = views.search_books(title)
    return result