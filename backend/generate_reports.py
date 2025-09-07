#!/usr/bin/env python3
"""
Dedicated Report Generation Scripts
- Event Popularity Report
- Student Participation Report
- Export to CSV/JSON formats
"""

import sqlite3
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Database configuration
DATABASE_PATH = Path(__file__).parent.parent / "database" / "event_management_db.db"

class ReportGenerator:
    def __init__(self):
        self.conn = None
    
    def connect_db(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(str(DATABASE_PATH))
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def generate_event_popularity_report(self, 
                                       start_date: Optional[str] = None,
                                       end_date: Optional[str] = None,
                                       college_id: Optional[int] = None,
                                       event_type_id: Optional[int] = None,
                                       min_registrations: Optional[int] = None,
                                       max_registrations: Optional[int] = None,
                                       sort_order: str = "desc",
                                       limit: int = 50) -> Dict[str, Any]:
        """
        Generate Event Popularity Report sorted by number of registrations
        """
        print("📊 Generating Event Popularity Report...")
        
        cursor = self.conn.cursor()
        
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
        events = [dict(row) for row in cursor.fetchall()]
        
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
        
        report = {
            "report_type": "Event Popularity Report",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
            "events": events
        }
        
        print(f"✅ Generated report with {total_events} events")
        return report
    
    def generate_student_participation_report(self,
                                            start_date: Optional[str] = None,
                                            end_date: Optional[str] = None,
                                            college_id: Optional[int] = None,
                                            min_events_attended: Optional[int] = None,
                                            max_events_attended: Optional[int] = None,
                                            sort_order: str = "desc",
                                            limit: int = 100) -> Dict[str, Any]:
        """
        Generate Student Participation Report showing how many events each student attended
        """
        print("👥 Generating Student Participation Report...")
        
        cursor = self.conn.cursor()
        
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
        students = [dict(row) for row in cursor.fetchall()]
        
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
        
        report = {
            "report_type": "Student Participation Report",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
            "students": students
        }
        
        print(f"✅ Generated report with {total_students} students")
        return report
    
    def export_to_json(self, report: Dict[str, Any], filename: str):
        """Export report to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ Report exported to JSON: {filename}")
        except Exception as e:
            print(f"❌ Failed to export JSON: {e}")
    
    def export_to_csv(self, report: Dict[str, Any], filename: str):
        """Export report to CSV file"""
        try:
            if report['report_type'] == 'Event Popularity Report':
                self._export_events_to_csv(report['events'], filename)
            elif report['report_type'] == 'Student Participation Report':
                self._export_students_to_csv(report['students'], filename)
            print(f"✅ Report exported to CSV: {filename}")
        except Exception as e:
            print(f"❌ Failed to export CSV: {e}")
    
    def _export_events_to_csv(self, events: List[Dict[str, Any]], filename: str):
        """Export events data to CSV"""
        if not events:
            return
        
        fieldnames = [
            'event_id', 'title', 'start_time', 'end_time', 'venue', 'capacity',
            'college_name', 'event_type_name', 'total_registrations',
            'total_attendance', 'attendance_rate', 'total_feedback', 'average_rating'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for event in events:
                writer.writerow({field: event.get(field, '') for field in fieldnames})
    
    def _export_students_to_csv(self, students: List[Dict[str, Any]], filename: str):
        """Export students data to CSV"""
        if not students:
            return
        
        fieldnames = [
            'student_id', 'student_name', 'student_email', 'college_name',
            'total_events_registered', 'total_events_attended', 'attendance_rate',
            'total_feedback_submitted', 'average_feedback_rating'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for student in students:
                writer.writerow({field: student.get(field, '') for field in fieldnames})

def main():
    """Main function to generate reports"""
    print("📊 EVENT MANAGEMENT REPORTS GENERATOR")
    print("=" * 50)
    
    generator = ReportGenerator()
    
    if not generator.connect_db():
        return
    
    try:
        # Generate Event Popularity Report
        print("\n1. EVENT POPULARITY REPORT")
        print("-" * 30)
        event_report = generator.generate_event_popularity_report(
            sort_order="desc",
            limit=20
        )
        
        # Print summary
        summary = event_report['summary']
        print(f"📈 Summary:")
        print(f"   Total Events: {summary['total_events']}")
        print(f"   Total Registrations: {summary['total_registrations']}")
        print(f"   Average Registrations per Event: {summary['average_registrations_per_event']}")
        if summary['most_popular_event']:
            print(f"   Most Popular: {summary['most_popular_event']['title']} ({summary['most_popular_event']['registrations']} registrations)")
        
        # Show top 5 events
        print(f"\n🏆 Top 5 Most Popular Events:")
        for i, event in enumerate(event_report['events'][:5], 1):
            print(f"   {i}. {event['title']} - {event['total_registrations']} registrations")
        
        # Generate Student Participation Report
        print("\n\n2. STUDENT PARTICIPATION REPORT")
        print("-" * 30)
        student_report = generator.generate_student_participation_report(
            sort_order="desc",
            limit=20
        )
        
        # Print summary
        summary = student_report['summary']
        print(f"👥 Summary:")
        print(f"   Total Students: {summary['total_students']}")
        print(f"   Total Events Attended: {summary['total_events_attended']}")
        print(f"   Average Events per Student: {summary['average_events_per_student']}")
        if summary['most_active_student']:
            print(f"   Most Active: {summary['most_active_student']['name']} ({summary['most_active_student']['events_attended']} events)")
        
        # Show participation categories
        categories = summary['participation_categories']
        print(f"\n📊 Participation Categories:")
        print(f"   Highly Active (5+ events): {categories['highly_active']} students")
        print(f"   Moderately Active (2-4 events): {categories['moderately_active']} students")
        print(f"   Low Active (<2 events): {categories['low_active']} students")
        
        # Show top 5 most active students
        print(f"\n🏆 Top 5 Most Active Students:")
        for i, student in enumerate(student_report['students'][:5], 1):
            print(f"   {i}. {student['student_name']} - {student['total_events_attended']} events attended")
        
        # Export reports
        print("\n\n3. EXPORTING REPORTS")
        print("-" * 30)
        
        # Export to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        event_json_file = f"event_popularity_report_{timestamp}.json"
        student_json_file = f"student_participation_report_{timestamp}.json"
        
        generator.export_to_json(event_report, event_json_file)
        generator.export_to_json(student_report, student_json_file)
        
        # Export to CSV
        event_csv_file = f"event_popularity_report_{timestamp}.csv"
        student_csv_file = f"student_participation_report_{timestamp}.csv"
        
        generator.export_to_csv(event_report, event_csv_file)
        generator.export_to_csv(student_report, student_csv_file)
        
        print(f"\n🎉 Reports generated successfully!")
        print(f"📁 Files created:")
        print(f"   - {event_json_file}")
        print(f"   - {student_json_file}")
        print(f"   - {event_csv_file}")
        print(f"   - {student_csv_file}")
        
    finally:
        generator.close_db()

if __name__ == "__main__":
    main()
