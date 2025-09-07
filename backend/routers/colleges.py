"""
Colleges router for Event Management System.
Handles CRUD operations for college entities.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import College
from schemas import CollegeCreate, CollegeUpdate, College as CollegeSchema

router = APIRouter(prefix="/colleges", tags=["colleges"])

@router.post("/", response_model=CollegeSchema)
async def create_college(college: CollegeCreate, db: Session = Depends(get_db)):
    db_college = College(**college.dict())
    db.add(db_college)
    db.commit()
    db.refresh(db_college)
    return db_college

@router.get("/", response_model=List[CollegeSchema])
async def read_colleges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    colleges = db.query(College).offset(skip).limit(limit).all()
    return colleges

@router.get("/{college_id}", response_model=CollegeSchema)
async def read_college(college_id: int, db: Session = Depends(get_db)):
    college = db.query(College).filter(College.college_id == college_id).first()
    if college is None:
        raise HTTPException(status_code=404, detail="College not found")
    return college

@router.put("/{college_id}", response_model=CollegeSchema)
async def update_college(college_id: int, college_update: CollegeUpdate, db: Session = Depends(get_db)):
    college = db.query(College).filter(College.college_id == college_id).first()
    if college is None:
        raise HTTPException(status_code=404, detail="College not found")
    
    update_data = college_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(college, field, value)
    
    db.commit()
    db.refresh(college)
    return college

@router.delete("/{college_id}")
async def delete_college(college_id: int, db: Session = Depends(get_db)):
    college = db.query(College).filter(College.college_id == college_id).first()
    if college is None:
        raise HTTPException(status_code=404, detail="College not found")
    
    db.delete(college)
    db.commit()
    return {"message": "College deleted successfully"}

