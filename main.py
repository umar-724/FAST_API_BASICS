from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Generator, List
from sqlalchemy.orm import Session

from db import SessionLocal, init_db
import models

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str
    price: int
    car: str


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def model_to_dict(item: models.Item) -> Dict:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "car": item.car,
    }


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/items/{item_id}")
def create_item(item_id: int, item: Item, db: Session = Depends(get_db)):
    existing = db.query(models.Item).filter(models.Item.id == item_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already exists")

    db_item = models.Item(id=item_id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": "Item created", "data": model_to_dict(db_item)}


@app.get("/items")
def get_all_items(db: Session = Depends(get_db)) -> List[Dict]:
    rows = db.query(models.Item).all()
    return [model_to_dict(r) for r in rows]


@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return model_to_dict(row)


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, db: Session = Depends(get_db)):
    row = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")

    row.name = item.name
    row.description = item.description
    row.price = item.price
    row.car = item.car
    db.commit()
    db.refresh(row)
    return {"message": "Item updated", "data": model_to_dict(row)}


@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    row = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(row)
    db.commit()
    return {"message": "Item deleted"}