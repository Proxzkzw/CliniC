
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    text: str = None
    completed: bool = False

items = []

@app.get("/")
def read_root():
    return "Hello, World"

@app.post("/items", response_model= list[Item])
def create_item(item: str):
    items.append(item)
    return item

@app.get("/items/{item_id}", response_model= Item) 
def get_item(item_id: int) -> Item:
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(statuscode=404,details=f("item {item_id} not found"))
    