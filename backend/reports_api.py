#!/usr/bin/env python3
"""
Advanced Reports API for Event Management System
- Event Popularity Report (sorted by registrations)
- Student Participation Report (events attended per student)
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
class ReportFilters(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    college_id: Optional[int] = None
    event_type_id: Optional[int] = None
    min_registrations: Optional[int] = None
    max_registrations: Optional[int] = None

# FastAPI app
app = FastAPI(
    title="Event Management Reports API",
    description="Advanced reporting APIs for event popularity and student participation",
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
# EVENT POPULARITY REPORT
# ============================================================================

@app.get("/api/reports/event-popularity", response_model=Dict[str, Any])
async def get_event_popularity_report(
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    college_id: Optional[int] = Query(None, description="Filter by college ID"),
    event_type_id: Optional[int] = Query(None, description="Filter by event type ID"),
    min_registrations: Optional[int] = Query(None, description="Minimum number of registrations"),
    max_registrations: Optional[int] = Query(None, description="Maximum number of registrations"),
    limit: int = Query(50, le=1000, description="Maximum number of results"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order: asc or desc")
):
    """
    Generate Event Popularity Report sorted by number of registrations
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build the main query
        query = """
            SELECT 
                e.event_id,
                e.title,
                e.description,
                e.start_time,
                e.end_time,
                e.venue,
                e.capacity,
                e.status,
                c.name as college_name,
                et.name as event_type_name,
                a.name as created_by_name,
                COUNT(r.registration_id) as total_registrations,
                COUNT(CASE WHEN a_att.attended = 1 THEN 1 END) as total_attendance,
                COUNT(f.feedback_id) as total_feedback,
                ROUND(AVG(f.rating), 2) as average_rating,
                ROUND(COUNT(CASE WHEN a_att.attended = 1 THEN 1 END) * 100.0 / COUNT(r.registration_id), 2) as attendance_rate
            FROM Events e
            LEFT JOIN Colleges c ON e.college_id = c.college_id
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Admins a ON e.created_by = a.admin_id
            LEFT JOIN Registrations r ON e.event_id = r.event_id AND r.status = 'registered'
            LEFT JOIN Attendance a_att ON r.registration_id = a_att.registration_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE 1=1
        """
        
        params = []
        
        # Apply filters
        if start_date:
            query += " AND e.start_time >= ?"
            params.append(f"{start_date} 00:00:00")
        
        if end_date:
            query += " AND e.start_time <= ?"
            params.append(f"{end_date} 23:59:59")
        
        if college_id:
            query += " AND e.college_id = ?"
            params.append(college_id)
        
        if event_type_id:
            query += " AND e.type_id = ?"
            params.append(event_type_id)
        
        # Group by event
        query += " GROUP BY e.event_id"
        
        # Apply registration count filters
        if min_registrations is not None:
            query += " HAVING total_registrations >= ?"
            params.append(min_registrations)
        
        if max_registrations is not None:
            if min_registrations is not None:
                query += " AND total_registrations <= ?"
            else:
                query += " HAVING total_registrations <= ?"
            params.append(max_registrations)
        
        # Sort by registrations
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
        query += f" ORDER BY total_registrations {sort_direction}, e.start_time DESC"
        
        # Apply limit
        query += " LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        events = rows_to_list(cursor.fetchall())
        
        # Calculate summary statistics
        if events:
            total_events = len(events)
            total_registrations = sum(event['total_registrations'] for event in events)
            total_attendance = sum(event['total_attendance'] for event in events)
            avg_registrations = total_registrations / total_events
            avg_attendance_rate = sum(event['attendance_rate'] or 0 for event in events) / total_events
            avg_rating = sum(event['average_rating'] or 0 for event in events) / total_events
            
            # Find most and least popular events
            most_popular = max(events, key=lambda x: x['total_registrations'])
            least_popular = min(events, key=lambda x: x['total_registrations'])
        else:
            total_events = 0
            total_registrations = 0
            total_attendance = 0
            avg_registrations = 0
            avg_attendance_rate = 0
            avg_rating = 0
            most_popular = None
            least_popular = None
        
        conn.close()
        
        return {
            "report_type": "Event Popularity Report",
            "filters_applied": {
                "start_date": start_date,
                "end_date": end_date,
                "college_id": college_id,
                "event_type_id": event_type_id,
                "min_registrations": min_registrations,
                "max_registrations": max_registrations,
                "sort_order": sort_order,
                "limit": limit
            },
            "summary": {
                "total_events": total_events,
                "total_registrations": total_registrations,
                "total_attendance": total_attendance,
                "average_registrations_per_event": round(avg_registrations, 2),
                "average_attendance_rate": round(avg_attendance_rate, 2),
                "average_rating": round(avg_rating, 2),
                "most_popular_event": {
                    "title": most_popular['title'],
                    "registrations": most_popular['total_registrations']
                } if most_popular else None,
                "least_popular_event": {
                    "title": least_popular['title'],
                    "registrations": least_popular['total_registrations']
                } if least_popular else None
            },
            "events": events,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STUDENT PARTICIPATION REPORT
# ============================================================================

@app.get("/api/reports/student-participation", response_model=Dict[str, Any])
async def get_student_participation_report(
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    college_id: Optional[int] = Query(None, description="Filter by college ID"),
    min_events_attended: Optional[int] = Query(None, description="Minimum events attended"),
    max_events_attended: Optional[int] = Query(None, description="Maximum events attended"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order: asc or desc")
):
    """
    Generate Student Participation Report showing how many events each student attended
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build the main query
        query = """
            SELECT 
                s.student_id,
                s.name as student_name,
                s.email as student_email,
                s.phone,
                s.semester,
                c.name as college_name,
                COUNT(DISTINCT r.event_id) as total_events_registered,
                COUNT(DISTINCT CASE WHEN a.attended = 1 THEN r.event_id END) as total_events_attended,
                COUNT(DISTINCT f.feedback_id) as total_feedback_submitted,
                ROUND(AVG(f.rating), 2) as average_feedback_rating,
                ROUND(COUNT(DISTINCT CASE WHEN a.attended = 1 THEN r.event_id END) * 100.0 / COUNT(DISTINCT r.event_id), 2) as attendance_rate
            FROM Students s
            LEFT JOIN Colleges c ON s.college_id = c.college_id
            LEFT JOIN Registrations r ON s.student_id = r.student_id AND r.status = 'registered'
            LEFT JOIN Events e ON r.event_id = e.event_id
            LEFT JOIN Attendance a ON r.registration_id = a.registration_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE 1=1
        """
        
        params = []
        
        # Apply filters
        if start_date:
            query += " AND e.start_time >= ?"
            params.append(f"{start_date} 00:00:00")
        
        if end_date:
            query += " AND e.start_time <= ?"
            params.append(f"{end_date} 23:59:59")
        
        if college_id:
            query += " AND s.college_id = ?"
            params.append(college_id)
        
        # Group by student
        query += " GROUP BY s.student_id"
        
        # Apply events attended filters
        if min_events_attended is not None:
            query += " HAVING total_events_attended >= ?"
            params.append(min_events_attended)
        
        if max_events_attended is not None:
            if min_events_attended is not None:
                query += " AND total_events_attended <= ?"
            else:
                query += " HAVING total_events_attended <= ?"
            params.append(max_events_attended)
        
        # Sort by events attended
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
        query += f" ORDER BY total_events_attended {sort_direction}, s.name ASC"
        
        # Apply limit
        query += " LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        students = rows_to_list(cursor.fetchall())
        
        # Calculate summary statistics
        if students:
            total_students = len(students)
            total_events_registered = sum(student['total_events_registered'] for student in students)
            total_events_attended = sum(student['total_events_attended'] for student in students)
            avg_events_per_student = total_events_registered / total_students
            avg_attendance_rate = sum(student['attendance_rate'] or 0 for student in students) / total_students
            avg_feedback_rating = sum(student['average_feedback_rating'] or 0 for student in students) / total_students
            
            # Find most and least active students
            most_active = max(students, key=lambda x: x['total_events_attended'])
            least_active = min(students, key=lambda x: x['total_events_attended'])
            
            # Participation categories
            highly_active = len([s for s in students if s['total_events_attended'] >= 5])
            moderately_active = len([s for s in students if 2 <= s['total_events_attended'] < 5])
            low_active = len([s for s in students if s['total_events_attended'] < 2])
        else:
            total_students = 0
            total_events_registered = 0
            total_events_attended = 0
            avg_events_per_student = 0
            avg_attendance_rate = 0
            avg_feedback_rating = 0
            most_active = None
            least_active = None
            highly_active = 0
            moderately_active = 0
            low_active = 0
        
        conn.close()
        
        return {
            "report_type": "Student Participation Report",
            "filters_applied": {
                "start_date": start_date,
                "end_date": end_date,
                "college_id": college_id,
                "min_events_attended": min_events_attended,
                "max_events_attended": max_events_attended,
                "sort_order": sort_order,
                "limit": limit
            },
            "summary": {
                "total_students": total_students,
                "total_events_registered": total_events_registered,
                "total_events_attended": total_events_attended,
                "average_events_per_student": round(avg_events_per_student, 2),
                "average_attendance_rate": round(avg_attendance_rate, 2),
                "average_feedback_rating": round(avg_feedback_rating, 2),
                "most_active_student": {
                    "name": most_active['student_name'],
                    "events_attended": most_active['total_events_attended']
                } if most_active else None,
                "least_active_student": {
                    "name": least_active['student_name'],
                    "events_attended": least_active['total_events_attended']
                } if least_active else None,
                "participation_categories": {
                    "highly_active": highly_active,
                    "moderately_active": moderately_active,
                    "low_active": low_active
                }
            },
            "students": students,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DETAILED STUDENT PARTICIPATION
# ============================================================================

@app.get("/api/reports/student-participation/{student_id}", response_model=Dict[str, Any])
async def get_student_detailed_participation(
    student_id: int,
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)")
):
    """
    Get detailed participation report for a specific student
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get student basic info
        cursor.execute("""
            SELECT s.*, c.name as college_name
            FROM Students s
            LEFT JOIN Colleges c ON s.college_id = c.college_id
            WHERE s.student_id = ?
        """, (student_id,))
        
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get detailed participation data
        query = """
            SELECT 
                e.event_id,
                e.title as event_title,
                e.start_time,
                e.end_time,
                e.venue,
                et.name as event_type_name,
                r.registration_time,
                r.status as registration_status,
                a.attended,
                a.check_in_time,
                f.rating,
                f.comments,
                f.submitted_at as feedback_submitted_at
            FROM Events e
            LEFT JOIN EventTypes et ON e.type_id = et.type_id
            LEFT JOIN Registrations r ON e.event_id = r.event_id
            LEFT JOIN Attendance a ON r.registration_id = a.registration_id
            LEFT JOIN Feedback f ON r.registration_id = f.registration_id
            WHERE r.student_id = ?
        """
        
        params = [student_id]
        
        if start_date:
            query += " AND e.start_time >= ?"
            params.append(f"{start_date} 00:00:00")
        
        if end_date:
            query += " AND e.start_time <= ?"
            params.append(f"{end_date} 23:59:59")
        
        query += " ORDER BY e.start_time DESC"
        
        cursor.execute(query, params)
        participation_records = rows_to_list(cursor.fetchall())
        
        # Calculate statistics
        total_registrations = len(participation_records)
        total_attended = sum(1 for record in participation_records if record['attended'] == 1)
        total_feedback = sum(1 for record in participation_records if record['rating'] is not None)
        attendance_rate = (total_attended / total_registrations * 100) if total_registrations > 0 else 0
        avg_rating = sum(record['rating'] for record in participation_records if record['rating'] is not None) / total_feedback if total_feedback > 0 else 0
        
        conn.close()
        
        return {
            "student_info": dict(student),
            "participation_summary": {
                "total_registrations": total_registrations,
                "total_attended": total_attended,
                "total_feedback_submitted": total_feedback,
                "attendance_rate": round(attendance_rate, 2),
                "average_rating": round(avg_rating, 2)
            },
            "participation_records": participation_records,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except HTTPException:
        raise
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
    print("🚀 Starting Event Management Reports API")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📊 Available Reports:")
    print("   - Event Popularity: /api/reports/event-popularity")
    print("   - Student Participation: /api/reports/student-participation")
    uvicorn.run(app, host="0.0.0.0", port=8000)
