from fastapi import FastAPI, HTTPException
from models import Item
import views

app = FastAPI()

@app.post("/items/", response_model=str)
def create_item(item: Item):
    item_data = item.dict()
    item_id = views.create_item(item_data)
    return item_id

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: str):
    item = views.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: str, item: Item):
    updated_item = views.update_item(item_id, item.dict())
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@app.delete("/items/{item_id}", response_model=dict)
def delete_item(item_id: str):
    result = views.delete_item(item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted"}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/books/{title}")
def get_recommendations(title: str):
    result = views.get_books(title)
    return result