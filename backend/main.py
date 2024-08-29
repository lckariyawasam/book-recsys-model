from fastapi import FastAPI, HTTPException
from models import BookTitle
import views

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/similar")
def get_similar_books(title: BookTitle):
    print(title)
    result = views.recommend_from_one(title.title)
    return result


@app.get("/recommend")
def recommend_books(titles: list[BookTitle]):
    print(titles)
    result = views.recommend_from_multiple([title.title for title in titles])
    return result