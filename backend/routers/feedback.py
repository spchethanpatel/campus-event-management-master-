"""Feedback router for Event Management System CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Feedback, Registration
from schemas import FeedbackCreate, FeedbackUpdate, Feedback as FeedbackSchema, FeedbackWithDetails

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("/", response_model=FeedbackSchema)
async def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    # Check if registration exists
    registration = db.query(Registration).filter(Registration.registration_id == feedback.registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if feedback already exists for this registration
    existing_feedback = db.query(Feedback).filter(Feedback.registration_id == feedback.registration_id).first()
    if existing_feedback:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this registration")
    
    # Validate rating (assuming 1-5 scale)
    if not 1 <= feedback.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/", response_model=List[FeedbackSchema])
async def read_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).offset(skip).limit(limit).all()
    return feedback

@router.get("/{feedback_id}", response_model=FeedbackSchema)
async def read_feedback_record(feedback_id: int, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback record not found")
    return feedback

@router.get("/{feedback_id}/with-details", response_model=FeedbackWithDetails)
async def read_feedback_with_details(feedback_id: int, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback record not found")
    return feedback

@router.put("/{feedback_id}", response_model=FeedbackSchema)
async def update_feedback(feedback_id: int, feedback_update: FeedbackUpdate, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback record not found")
    
    update_data = feedback_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)
    
    db.commit()
    db.refresh(feedback)
    return feedback

@router.delete("/{feedback_id}")
async def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback record not found")
    
    db.delete(feedback)
    db.commit()
    return {"message": "Feedback record deleted successfully"}

@router.get("/registration/{registration_id}", response_model=FeedbackSchema)
async def read_feedback_by_registration(registration_id: int, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.registration_id == registration_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback record not found for this registration")
    return feedback

