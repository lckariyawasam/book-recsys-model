from fastapi import FastAPI, HTTPException
# from models import BookTitle
from typing import List
import views

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/similar")
def get_similar_books(id: str, k: int = 10):
    # print(title)
    # result = views.recommend_from_one(title.title)
    # return result
    return views.get_similar(id, k)


@app.post("/recommend")
def recommend_books(titles: List[str]):
    print(titles)
    result = views.recommend_from_multiple(titles)
    return result