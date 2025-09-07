"""Admins router for Event Management System CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Admin, College
from schemas import AdminCreate, AdminUpdate, Admin as AdminSchema, AdminWithCollege

router = APIRouter(prefix="/admins", tags=["admins"])

@router.post("/", response_model=AdminSchema)
async def create_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    # Check if college exists
    college = db.query(College).filter(College.college_id == admin.college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Check if email already exists
    existing_admin = db.query(Admin).filter(Admin.email == admin.email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_admin = Admin(**admin.dict())
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.get("/", response_model=List[AdminSchema])
async def read_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    admins = db.query(Admin).offset(skip).limit(limit).all()
    return admins

@router.get("/{admin_id}", response_model=AdminSchema)
async def read_admin(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

@router.get("/{admin_id}/with-college", response_model=AdminWithCollege)
async def read_admin_with_college(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

@router.put("/{admin_id}", response_model=AdminSchema)
async def update_admin(admin_id: int, admin_update: AdminUpdate, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    update_data = admin_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(admin, field, value)
    
    db.commit()
    db.refresh(admin)
    return admin

@router.delete("/{admin_id}")
async def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    db.delete(admin)
    db.commit()
    return {"message": "Admin deleted successfully"}

@router.get("/college/{college_id}", response_model=List[AdminSchema])
async def read_admins_by_college(college_id: int, db: Session = Depends(get_db)):
    admins = db.query(Admin).filter(Admin.college_id == college_id).all()
    return admins

