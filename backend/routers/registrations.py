"""Registrations router for Event Management System CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Registration, Student, Event
from schemas import RegistrationCreate, RegistrationUpdate, Registration as RegistrationSchema, RegistrationWithDetails

router = APIRouter(prefix="/registrations", tags=["registrations"])

@router.post("/", response_model=RegistrationSchema)
async def create_registration(registration: RegistrationCreate, db: Session = Depends(get_db)):
    # Check if student exists
    student = db.query(Student).filter(Student.student_id == registration.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if event exists
    event = db.query(Event).filter(Event.event_id == registration.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if already registered
    existing_registration = db.query(Registration).filter(
        Registration.student_id == registration.student_id,
        Registration.event_id == registration.event_id
    ).first()
    if existing_registration:
        raise HTTPException(status_code=400, detail="Student already registered for this event")
    
    db_registration = Registration(**registration.dict())
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return db_registration

@router.get("/", response_model=List[RegistrationSchema])
async def read_registrations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    registrations = db.query(Registration).offset(skip).limit(limit).all()
    return registrations

@router.get("/{registration_id}", response_model=RegistrationSchema)
async def read_registration(registration_id: int, db: Session = Depends(get_db)):
    registration = db.query(Registration).filter(Registration.registration_id == registration_id).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    return registration

@router.get("/{registration_id}/with-details", response_model=RegistrationWithDetails)
async def read_registration_with_details(registration_id: int, db: Session = Depends(get_db)):
    registration = db.query(Registration).filter(Registration.registration_id == registration_id).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    return registration

@router.put("/{registration_id}", response_model=RegistrationSchema)
async def update_registration(registration_id: int, registration_update: RegistrationUpdate, db: Session = Depends(get_db)):
    registration = db.query(Registration).filter(Registration.registration_id == registration_id).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    update_data = registration_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(registration, field, value)
    
    db.commit()
    db.refresh(registration)
    return registration

@router.delete("/{registration_id}")
async def delete_registration(registration_id: int, db: Session = Depends(get_db)):
    registration = db.query(Registration).filter(Registration.registration_id == registration_id).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    db.delete(registration)
    db.commit()
    return {"message": "Registration deleted successfully"}

@router.get("/student/{student_id}", response_model=List[RegistrationSchema])
async def read_registrations_by_student(student_id: int, db: Session = Depends(get_db)):
    registrations = db.query(Registration).filter(Registration.student_id == student_id).all()
    return registrations

@router.get("/event/{event_id}", response_model=List[RegistrationSchema])
async def read_registrations_by_event(event_id: int, db: Session = Depends(get_db)):
    registrations = db.query(Registration).filter(Registration.event_id == event_id).all()
    return registrations

