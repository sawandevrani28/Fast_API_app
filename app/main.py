from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

class ItemCreate(BaseModel):
    name: str
    description: str

class ItemRead(ItemCreate):
    id: int

    class Config:
        orm_mode = True

@app.post("/items/", response_model=ItemRead)
def create_item(item: ItemCreate):
    db: Session = SessionLocal()
    db_item = models.Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.get("/items/", response_model=List[ItemRead])
def read_items():
    db: Session = SessionLocal()
    items = db.query(models.Item).all()
    db.close()
    return items

@app.put("/items/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item: ItemCreate):
    db: Session = SessionLocal()
    db_item = db.query(models.Item).get(item_id)
    if not db_item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.name
    db_item.description = item.description
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db: Session = SessionLocal()
    db_item = db.query(models.Item).get(item_id)
    if not db_item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    db.close()
    return {"message": "Item deleted"}
