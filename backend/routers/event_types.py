"""Event_Types router for Event Management System CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import EventType
from schemas import EventTypeCreate, EventType as EventTypeSchema

router = APIRouter(prefix="/event-types", tags=["event-types"])

@router.post("/", response_model=EventTypeSchema)
async def create_event_type(event_type: EventTypeCreate, db: Session = Depends(get_db)):
    db_event_type = EventType(**event_type.dict())
    db.add(db_event_type)
    db.commit()
    db.refresh(db_event_type)
    return db_event_type

@router.get("/", response_model=List[EventTypeSchema])
async def read_event_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    event_types = db.query(EventType).offset(skip).limit(limit).all()
    return event_types

@router.get("/{type_id}", response_model=EventTypeSchema)
async def read_event_type(type_id: int, db: Session = Depends(get_db)):
    event_type = db.query(EventType).filter(EventType.type_id == type_id).first()
    if event_type is None:
        raise HTTPException(status_code=404, detail="Event type not found")
    return event_type

@router.delete("/{type_id}")
async def delete_event_type(type_id: int, db: Session = Depends(get_db)):
    event_type = db.query(EventType).filter(EventType.type_id == type_id).first()
    if event_type is None:
        raise HTTPException(status_code=404, detail="Event type not found")
    
    db.delete(event_type)
    db.commit()
    return {"message": "Event type deleted successfully"}

