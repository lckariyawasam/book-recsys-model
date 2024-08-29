from fastapi import FastAPI, HTTPException
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
def get_similar_books(book: BookRequest):
    # print(title)
    # result = views.recommend_from_one(title.title)
    # return result
    id = book.id
    k = book.k
    return views.get_similar(id, k)


@app.post("/recommend")
def recommend_books(titles: List[str]):
    print(titles)
    result = views.recommend_from_multiple(titles)
    return result


@app.get("/search")
def search_books(title: str):
    result = views.search_books(title)
    return result