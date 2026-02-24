from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# ----------------------
# Data Model
# ----------------------
class Item(BaseModel):
    name: str
    description: str
    price: int
    car : str
# ----------------------
# Fake Database
# ----------------------
items_db: Dict[int, Item] = {}

# ----------------------
# CREATE
# ----------------------
@app.post("/items/{item_id}")
def create_item(item_id: int, item: Item):
    if item_id in items_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    
    items_db[item_id] = item
    return {"message": "Item created", "data": item}

# ----------------------
# READ ALL
# ----------------------
@app.get("/items")
def get_all_items():
    return items_db

# ----------------------
# READ ONE
# ----------------------
@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return items_db[item_id]

# ----------------------
# UPDATE
# ----------------------
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    items_db[item_id] = item
    return {"message": "Item updated", "data": item}

# ----------------------
# DELETE
# ----------------------
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    del items_db[item_id]
    return {"message": "Item deleted"}