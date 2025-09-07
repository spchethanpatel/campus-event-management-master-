"""SQLAlchemy models for Event Management System database."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class College(Base):
    __tablename__ = "Colleges"
    
    college_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    status = Column(String, nullable=False, default='active')
    
    # Relationships
    admins = relationship("Admin", back_populates="college")
    students = relationship("Student", back_populates="college")
    events = relationship("Event", back_populates="college")

class Admin(Base):
    __tablename__ = "Admins"
    
    admin_id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("Colleges.college_id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String)
    status = Column(String, nullable=False, default='active')
    
    # Relationships
    college = relationship("College", back_populates="admins")
    created_events = relationship("Event", back_populates="creator")

class Student(Base):
    __tablename__ = "Students"
    
    student_id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("Colleges.college_id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    department = Column(String)
    year = Column(String)
    status = Column(String, nullable=False, default='active')
    
    # Relationships
    college = relationship("College", back_populates="students")
    registrations = relationship("Registration", back_populates="student")

class EventType(Base):
    __tablename__ = "EventTypes"
    
    type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Relationships
    events = relationship("Event", back_populates="event_type")

class Event(Base):
    __tablename__ = "Events"
    
    event_id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("Colleges.college_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    type_id = Column(Integer, ForeignKey("EventTypes.type_id"), nullable=False)
    venue = Column(String)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("Admins.admin_id"), nullable=False)
    semester = Column(String, nullable=False)
    status = Column(String, nullable=False, default='active')
    
    # Relationships
    college = relationship("College", back_populates="events")
    event_type = relationship("EventType", back_populates="events")
    creator = relationship("Admin", back_populates="created_events")
    registrations = relationship("Registration", back_populates="event")

class Registration(Base):
    __tablename__ = "Registrations"
    
    registration_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("Students.student_id"), nullable=False)
    event_id = Column(Integer, ForeignKey("Events.event_id"), nullable=False)
    registration_time = Column(String, nullable=False, default=datetime.now)
    status = Column(String, nullable=False, default='registered')
    
    # Relationships
    student = relationship("Student", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
    attendance = relationship("Attendance", back_populates="registration", uselist=False)
    feedback = relationship("Feedback", back_populates="registration", uselist=False)

class Attendance(Base):
    __tablename__ = "Attendance"
    
    attendance_id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("Registrations.registration_id"), nullable=False)
    attended = Column(Integer, nullable=False, default=0)
    check_in_time = Column(String)
    
    # Relationships
    registration = relationship("Registration", back_populates="attendance")

class Feedback(Base):
    __tablename__ = "Feedback"
    
    feedback_id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("Registrations.registration_id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comments = Column(Text)
    submitted_at = Column(String, nullable=False, default=datetime.now)
    
    # Relationships
    registration = relationship("Registration", back_populates="feedback")

class AuditLog(Base):
    __tablename__ = "AuditLogs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    table_name = Column(String, nullable=False)
    record_id = Column(Integer)
    old_data = Column(Text)
    new_data = Column(Text)
    changed_at = Column(String, default=datetime.now)
