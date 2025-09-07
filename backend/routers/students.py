"""Students router for Event Management System CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Student, College
from schemas import StudentCreate, StudentUpdate, Student as StudentSchema, StudentWithCollege

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/", response_model=StudentSchema)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    # Check if college exists
    college = db.query(College).filter(College.college_id == student.college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Check if email already exists
    existing_student = db.query(Student).filter(Student.email == student.email).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.get("/", response_model=List[StudentSchema])
async def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.get("/{student_id}", response_model=StudentSchema)
async def read_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/{student_id}/with-college", response_model=StudentWithCollege)
async def read_student_with_college(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=StudentSchema)
async def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    return student

@router.delete("/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

@router.get("/college/{college_id}", response_model=List[StudentSchema])
async def read_students_by_college(college_id: int, db: Session = Depends(get_db)):
    students = db.query(Student).filter(Student.college_id == college_id).all()
    return students

