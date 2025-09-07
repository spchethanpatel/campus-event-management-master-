"""Events router for Event Management System CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Event, College, EventType, Admin
from schemas import EventCreate, EventUpdate, Event as EventSchema, EventWithDetails

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventSchema)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    # Check if college exists
    college = db.query(College).filter(College.college_id == event.college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Check if event type exists
    event_type = db.query(EventType).filter(EventType.type_id == event.type_id).first()
    if not event_type:
        raise HTTPException(status_code=404, detail="Event type not found")
    
    # Check if admin exists
    admin = db.query(Admin).filter(Admin.admin_id == event.created_by).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[EventSchema])
async def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=EventSchema)
async def read_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/{event_id}/with-details", response_model=EventWithDetails)
async def read_event_with_details(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/{event_id}", response_model=EventSchema)
async def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}

@router.get("/college/{college_id}", response_model=List[EventSchema])
async def read_events_by_college(college_id: int, db: Session = Depends(get_db)):
    events = db.query(Event).filter(Event.college_id == college_id).all()
    return events

@router.get("/type/{type_id}", response_model=List[EventSchema])
async def read_events_by_type(type_id: int, db: Session = Depends(get_db)):
    events = db.query(Event).filter(Event.type_id == type_id).all()
    return events

