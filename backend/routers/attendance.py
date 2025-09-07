"""Attendance router for Event Management System CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Attendance, Registration
from schemas import AttendanceCreate, AttendanceUpdate, Attendance as AttendanceSchema, AttendanceWithDetails

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.post("/", response_model=AttendanceSchema)
async def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    # Check if registration exists
    registration = db.query(Registration).filter(Registration.registration_id == attendance.registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if attendance already exists for this registration
    existing_attendance = db.query(Attendance).filter(Attendance.registration_id == attendance.registration_id).first()
    if existing_attendance:
        raise HTTPException(status_code=400, detail="Attendance already recorded for this registration")
    
    db_attendance = Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.get("/", response_model=List[AttendanceSchema])
async def read_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).offset(skip).limit(limit).all()
    return attendance

@router.get("/{attendance_id}", response_model=AttendanceSchema)
async def read_attendance_record(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance

@router.get("/{attendance_id}/with-details", response_model=AttendanceWithDetails)
async def read_attendance_with_details(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance

@router.put("/{attendance_id}", response_model=AttendanceSchema)
async def update_attendance(attendance_id: int, attendance_update: AttendanceUpdate, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    update_data = attendance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)
    
    db.commit()
    db.refresh(attendance)
    return attendance

@router.delete("/{attendance_id}")
async def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    db.delete(attendance)
    db.commit()
    return {"message": "Attendance record deleted successfully"}

@router.get("/registration/{registration_id}", response_model=AttendanceSchema)
async def read_attendance_by_registration(registration_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.registration_id == registration_id).first()
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance record not found for this registration")
    return attendance

