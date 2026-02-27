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

class UserCreate(BaseModel):
    username: str
    password: str

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
# --- Filtering Endpoint ---

@app.get("/items/filter/")
def filter_cars(
    car_name: str = None, 
    color: str = None, 
    price: int = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Item)

    if car_name:
        query = query.filter(models.Item.car == car_name)
    if color:
        # Chunke aap description mein color likh rahe hain
        query = query.filter(models.Item.description.contains(color))
    if price:
        query = query.filter(models.Item.price == price)

    results = query.all()
    return [model_to_dict(r) for r in results]


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

# ... purana code (delete_item etc) ...

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check karein ke user pehle se to nahi hai
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = models.User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "username": new_user.username}


# --- Login Endpoint (Authentication) ---
@app.post("/login")
def login_user(user: UserCreate, db: Session = Depends(get_db)):
    # Database mein user ko dhoondein
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    
    # Agar user nahi mila ya password galat hai
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {"message": "Login successful!", "user": db_user.username}