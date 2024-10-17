from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import BookRequest, UserRequest
from typing import List
import views
from contextlib import asynccontextmanager

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
    id = book.id
    k = book.k
    return views.get_similar(id, k)

@app.post("/recommendations")
def get_recommendations_for_user(user: UserRequest):
    user_id = user.user_id
    k = user.k
    return views.get_recommendations_for_user(user_id, k)

@app.post("/item_recommendations")
def get_item_recommendations(book_ids: List[str]):
    return views.get_item_based_recommendations(book_ids)
