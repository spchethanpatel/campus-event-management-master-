"""Pydantic schemas for Event Management System API validation."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# College schemas
class CollegeBase(BaseModel):
    name: str
    location: Optional[str] = None
    status: str = 'active'

class CollegeCreate(CollegeBase):
    pass

class CollegeUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

class College(CollegeBase):
    college_id: int
    
    class Config:
        from_attributes = True

# Admin schemas
class AdminBase(BaseModel):
    college_id: int
    name: str
    email: str
    role: Optional[str] = None
    status: str = 'active'

class AdminCreate(AdminBase):
    pass

class AdminUpdate(BaseModel):
    college_id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

class Admin(AdminBase):
    admin_id: int
    
    class Config:
        from_attributes = True

class AdminWithCollege(Admin):
    college: College

# Student schemas
class StudentBase(BaseModel):
    college_id: int
    name: str
    email: str
    department: Optional[str] = None
    year: Optional[str] = None
    status: str = 'active'

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    college_id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    status: Optional[str] = None

class Student(StudentBase):
    student_id: int
    
    class Config:
        from_attributes = True

class StudentWithCollege(Student):
    college: College

# EventType schemas
class EventTypeBase(BaseModel):
    name: str

class EventTypeCreate(EventTypeBase):
    pass

class EventType(EventTypeBase):
    type_id: int
    
    class Config:
        from_attributes = True

# Event schemas
class EventBase(BaseModel):
    college_id: int
    title: str
    description: Optional[str] = None
    type_id: int
    venue: Optional[str] = None
    start_time: str
    end_time: str
    capacity: int
    created_by: int
    semester: str
    status: str = 'active'

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    college_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    type_id: Optional[int] = None
    venue: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    capacity: Optional[int] = None
    created_by: Optional[int] = None
    semester: Optional[str] = None
    status: Optional[str] = None

class Event(EventBase):
    event_id: int
    
    class Config:
        from_attributes = True

class EventWithDetails(Event):
    college: College
    event_type: EventType
    creator: Admin

# Registration schemas
class RegistrationBase(BaseModel):
    student_id: int
    event_id: int
    status: str = 'registered'

class RegistrationCreate(RegistrationBase):
    pass

class RegistrationUpdate(BaseModel):
    student_id: Optional[int] = None
    event_id: Optional[int] = None
    status: Optional[str] = None

class Registration(RegistrationBase):
    registration_id: int
    registration_time: str
    
    class Config:
        from_attributes = True

class RegistrationWithDetails(Registration):
    student: Student
    event: Event

# Attendance schemas
class AttendanceBase(BaseModel):
    registration_id: int
    attended: int = 0
    check_in_time: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    registration_id: Optional[int] = None
    attended: Optional[int] = None
    check_in_time: Optional[str] = None

class Attendance(AttendanceBase):
    attendance_id: int
    
    class Config:
        from_attributes = True

class AttendanceWithDetails(Attendance):
    registration: Registration

# Feedback schemas
class FeedbackBase(BaseModel):
    registration_id: int
    rating: int
    comments: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    registration_id: Optional[int] = None
    rating: Optional[int] = None
    comments: Optional[str] = None

class Feedback(FeedbackBase):
    feedback_id: int
    submitted_at: str
    
    class Config:
        from_attributes = True

class FeedbackWithDetails(Feedback):
    registration: Registration

# AuditLog schemas
class AuditLogBase(BaseModel):
    action: str
    table_name: str
    record_id: Optional[int] = None
    old_data: Optional[str] = None
    new_data: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    log_id: int
    changed_at: str
    
    class Config:
        from_attributes = True

# Response schemas
class MessageResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    database_path: str
