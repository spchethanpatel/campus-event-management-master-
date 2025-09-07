#!/usr/bin/env python3
"""
Core Operations API for Event Management System
- Register students to events
- Mark attendance
- Collect feedback (rating 1-5)
- Generate reports (registrations, attendance, feedback)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

# Database configuration
DATABASE_PATH = Path(__file__).parent.parent / "database" / "event_management_db.db"

# Pydantic models
class StudentRegistration(BaseModel):
    student_id: int
    event_id: int

class AttendanceMark(BaseModel):
    registration_id: int
    attended: int  # 1 for attended, 0 for absent
    check_in_time: Optional[str] = None

class FeedbackSubmission(BaseModel):
    registration_id: int
    rating: int  # 1-5 scale
    comments: Optional[str] = None

# FastAPI app
app = FastAPI(
    title="Event Management Core Operations",
    description="Core APIs for student registration, attendance, and feedback",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Get database connection"""
    if not DATABASE_PATH.exists():
        raise HTTPException(status_code=500, detail="Database file not found")
    
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    """Convert SQLite row to dictionary"""
    return dict(row) if row else None

def rows_to_list(rows):
    """Convert SQLite rows to list of dictionaries"""
    return [dict(row) for row in rows]

# ============================================================================
# STUDENT REGISTRATION ENDPOINTS
# ============================================================================

@app.post("/api/register-student", response_model=Dict[str, Any])
async def register_student(registration: StudentRegistration):
    """
    Register a student for an event
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate student exists
        cursor.execute("SELECT student_id, name FROM Students WHERE student_id = ?", (registration.student_id,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Validate event exists and is active
        cursor.execute("""
            SELECT event_id, title, capacity, start_time, status 
            FROM Events 
            WHERE event_id = ? AND status = 'active'
        """, (registration.event_id,))
        
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or not active")
        
        # Check if event has started
        if datetime.now() > datetime.fromisoformat(event['start_time'].replace(' ', 'T')):
            raise HTTPException(status_code=400, detail="Cannot register for events that have already started")
        
        # Check if already registered
        cursor.execute("""
            SELECT registration_id 
            FROM Registrations 
            WHERE student_id = ? AND event_id = ?
        """, (registration.student_id, registration.event_id))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Student already registered for this event")
        
        # Check capacity
        cursor.execute("""
            SELECT COUNT(*) as reg_count 
            FROM Registrations 
            WHERE event_id = ? AND status = 'registered'
        """, (registration.event_id,))
        
        reg_count = cursor.fetchone()['reg_count']
        if reg_count >= event['capacity']:
            raise HTTPException(status_code=400, detail="Event is at full capacity")
        
        # Register student
        cursor.execute("""
            INSERT INTO Registrations (student_id, event_id, status) 
            VALUES (?, ?, 'registered')
        """, (registration.student_id, registration.event_id))
        
        registration_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Student registered successfully",
            "registration_id": registration_id,
            "student_name": student['name'],
            "event_title": event['title'],
            "available_spots": event['capacity'] - reg_count - 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/event-registrations/{event_id}", response_model=List[Dict[str, Any]])
async def get_event_registrations(event_id: int):
    """
    Get all registrations for a specific event
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.registration_id, r.registration_time, r.status,
                   s.student_id, s.name as student_name, s.email as student_email,
                   e.title as event_title, e.start_time
            FROM Registrations r
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            WHERE r.event_id = ?
            ORDER BY r.registration_time DESC
        """, (event_id,))
        
        registrations = rows_to_list(cursor.fetchall())
        conn.close()
        
        return registrations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ATTENDANCE MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/mark-attendance", response_model=Dict[str, Any])
async def mark_attendance(attendance: AttendanceMark):
    """
    Mark attendance for a registration
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate registration exists
        cursor.execute("""
            SELECT r.*, s.name as student_name, e.title as event_title, e.start_time
            FROM Registrations r
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            WHERE r.registration_id = ?
        """, (attendance.registration_id,))
        
        registration = cursor.fetchone()
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        # Check if attendance already marked
        cursor.execute("""
            SELECT attendance_id FROM Attendance WHERE registration_id = ?
        """, (attendance.registration_id,))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Attendance already marked for this registration")
        
        # Mark attendance
        check_in_time = attendance.check_in_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO Attendance (registration_id, attended, check_in_time) 
            VALUES (?, ?, ?)
        """, (attendance.registration_id, attendance.attended, check_in_time))
        
        attendance_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Attendance marked successfully",
            "attendance_id": attendance_id,
            "student_name": registration['student_name'],
            "event_title": registration['event_title'],
            "attended": attendance.attended,
            "check_in_time": check_in_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/event-attendance/{event_id}", response_model=Dict[str, Any])
async def get_event_attendance(event_id: int):
    """
    Get attendance records for a specific event
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get event details
        cursor.execute("SELECT title, start_time FROM Events WHERE event_id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Get attendance records
        cursor.execute("""
            SELECT a.attendance_id, a.attended, a.check_in_time,
                   s.name as student_name, s.email as student_email,
                   r.registration_time
            FROM Attendance a
            JOIN Registrations r ON a.registration_id = r.registration_id
            JOIN Students s ON r.student_id = s.student_id
            WHERE r.event_id = ?
            ORDER BY a.check_in_time DESC
        """, (event_id,))
        
        attendance_records = rows_to_list(cursor.fetchall())
        
        # Calculate statistics
        total_registrations = len(attendance_records)
        attended_count = sum(1 for record in attendance_records if record['attended'] == 1)
        attendance_percentage = (attended_count / total_registrations * 100) if total_registrations > 0 else 0
        
        conn.close()
        
        return {
            "event_id": event_id,
            "event_title": event['title'],
            "event_start": event['start_time'],
            "total_registrations": total_registrations,
            "attended_count": attended_count,
            "attendance_percentage": round(attendance_percentage, 2),
            "attendance_records": attendance_records
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FEEDBACK COLLECTION ENDPOINTS
# ============================================================================

@app.post("/api/submit-feedback", response_model=Dict[str, Any])
async def submit_feedback(feedback: FeedbackSubmission):
    """
    Submit feedback for an event (rating 1-5)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate rating
        if not 1 <= feedback.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Validate registration exists and has attendance
        cursor.execute("""
            SELECT r.*, s.name as student_name, e.title as event_title
            FROM Registrations r
            JOIN Students s ON r.student_id = s.student_id
            JOIN Events e ON r.event_id = e.event_id
            JOIN Attendance a ON r.registration_id = a.registration_id
            WHERE r.registration_id = ? AND a.attended = 1
        """, (feedback.registration_id,))
        
        registration = cursor.fetchone()
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found or student did not attend")
        
        # Check if feedback already submitted
        cursor.execute("""
            SELECT feedback_id FROM Feedback WHERE registration_id = ?
        """, (feedback.registration_id,))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Feedback already submitted for this registration")
        
        # Submit feedback
        cursor.execute("""
            INSERT INTO Feedback (registration_id, rating, comments) 
            VALUES (?, ?, ?)
        """, (feedback.registration_id, feedback.rating, feedback.comments))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id,
            "student_name": registration['student_name'],
            "event_title": registration['event_title'],
            "rating": feedback.rating,
            "comments": feedback.comments
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/event-feedback/{event_id}", response_model=Dict[str, Any])
async def get_event_feedback(event_id: int):
    """
    Get feedback for a specific event
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get event details
        cursor.execute("SELECT title, start_time FROM Events WHERE event_id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Get feedback records
        cursor.execute("""
            SELECT f.feedback_id, f.rating, f.comments, f.submitted_at,
                   s.name as student_name, s.email as student_email
            FROM Feedback f
            JOIN Registrations r ON f.registration_id = r.registration_id
            JOIN Students s ON r.student_id = s.student_id
            WHERE r.event_id = ?
            ORDER BY f.submitted_at DESC
        """, (event_id,))
        
        feedback_records = rows_to_list(cursor.fetchall())
        
        # Calculate statistics
        if feedback_records:
            ratings = [record['rating'] for record in feedback_records]
            average_rating = sum(ratings) / len(ratings)
            min_rating = min(ratings)
            max_rating = max(ratings)
        else:
            average_rating = 0
            min_rating = 0
            max_rating = 0
        
        conn.close()
        
        return {
            "event_id": event_id,
            "event_title": event['title'],
            "event_start": event['start_time'],
            "total_feedback": len(feedback_records),
            "average_rating": round(average_rating, 2),
            "min_rating": min_rating,
            "max_rating": max_rating,
            "feedback_records": feedback_records
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# REPORT GENERATION ENDPOINTS
# ============================================================================

@app.get("/api/reports/registrations", response_model=Dict[str, Any])
async def get_registrations_report(
    event_id: Optional[int] = Query(None),
    college_id: Optional[int] = Query(None)
):
    """
    Get total registrations per event report
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT e.event_id, e.title, e.start_time, e.capacity,
                   c.name as college_name, et.name as event_type_name,
                   COUNT(r.registration_id) as total_registrations
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Registrations r ON e.event_id = r.event_id AND r.status = 'registered'
            WHERE 1=1
        """
        params = []
        
        if event_id:
            query += " AND e.event_id = ?"
            params.append(event_id)
        
        if college_id:
            query += " AND e.college_id = ?"
            params.append(college_id)
        
        query += " GROUP BY e.event_id ORDER BY e.start_time DESC"
        
        cursor.execute(query, params)
        events = rows_to_list(cursor.fetchall())
        
        # Calculate summary
        total_events = len(events)
        total_registrations = sum(event['total_registrations'] for event in events)
        
        conn.close()
        
        return {
            "summary": {
                "total_events": total_events,
                "total_registrations": total_registrations,
                "average_registrations_per_event": round(total_registrations / total_events, 2) if total_events > 0 else 0
            },
            "events": events,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/attendance-percentage", response_model=Dict[str, Any])
async def get_attendance_percentage_report(
    event_id: Optional[int] = Query(None),
    college_id: Optional[int] = Query(None)
):
    """
    Get attendance percentage report
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT e.event_id, e.title, e.start_time,
                   c.name as college_name,
                   COUNT(r.registration_id) as total_registrations,
                   COUNT(a.attendance_id) as attended_count,
                   ROUND(COUNT(a.attendance_id) * 100.0 / COUNT(r.registration_id), 2) as attendance_percentage
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN Registrations r ON e.event_id = r.event_id AND r.status = 'registered'
            LEFT JOIN Attendance a ON r.registration_id = a.registration_id AND a.attended = 1
            WHERE 1=1
        """
        params = []
        
        if event_id:
            query += " AND e.event_id = ?"
            params.append(event_id)
        
        if college_id:
            query += " AND e.college_id = ?"
            params.append(college_id)
        
        query += " GROUP BY e.event_id ORDER BY e.start_time DESC"
        
        cursor.execute(query, params)
        events = rows_to_list(cursor.fetchall())
        
        # Calculate summary statistics
        if events:
            total_registrations = sum(event['total_registrations'] for event in events)
            total_attended = sum(event['attended_count'] for event in events)
            overall_attendance_percentage = (total_attended / total_registrations * 100) if total_registrations > 0 else 0
            average_attendance_percentage = sum(event['attendance_percentage'] for event in events) / len(events)
        else:
            total_registrations = 0
            total_attended = 0
            overall_attendance_percentage = 0
            average_attendance_percentage = 0
        
        conn.close()
        
        return {
            "summary": {
                "total_events": len(events),
                "total_registrations": total_registrations,
                "total_attended": total_attended,
                "overall_attendance_percentage": round(overall_attendance_percentage, 2),
                "average_attendance_percentage": round(average_attendance_percentage, 2)
            },
            "events": events,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/average-feedback", response_model=Dict[str, Any])
async def get_average_feedback_report(
    event_id: Optional[int] = Query(None),
    college_id: Optional[int] = Query(None)
):
    """
    Get average feedback score report
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT e.event_id, e.title, e.start_time,
                   c.name as college_name,
                   COUNT(f.feedback_id) as total_feedback,
                   AVG(f.rating) as average_rating,
                   MIN(f.rating) as min_rating,
                   MAX(f.rating) as max_rating
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN Registrations r ON e.event_id = r.event_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE f.feedback_id IS NOT NULL
        """
        params = []
        
        if event_id:
            query += " AND e.event_id = ?"
            params.append(event_id)
        
        if college_id:
            query += " AND e.college_id = ?"
            params.append(college_id)
        
        query += " GROUP BY e.event_id ORDER BY e.start_time DESC"
        
        cursor.execute(query, params)
        events = rows_to_list(cursor.fetchall())
        
        # Calculate summary statistics
        if events:
            total_feedback = sum(event['total_feedback'] for event in events)
            overall_average_rating = sum(event['average_rating'] * event['total_feedback'] for event in events) / total_feedback if total_feedback > 0 else 0
            average_rating_per_event = sum(event['average_rating'] for event in events) / len(events)
        else:
            total_feedback = 0
            overall_average_rating = 0
            average_rating_per_event = 0
        
        conn.close()
        
        return {
            "summary": {
                "total_events_with_feedback": len(events),
                "total_feedback": total_feedback,
                "overall_average_rating": round(overall_average_rating, 2),
                "average_rating_per_event": round(average_rating_per_event, 2)
            },
            "events": events,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """System health check"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM Events")
        event_count = cursor.fetchone()['count']
        conn.close()
        
        return {
            "status": "healthy",
            "database_connected": True,
            "total_events": event_count,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Event Management Core Operations API")
    print("📖 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
