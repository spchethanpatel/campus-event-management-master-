#!/usr/bin/env python3
"""
API Testing Script for Event Management System
Tests all endpoints: Events, Registrations, Attendance, Reports
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
API_BASE = "http://localhost:8000"

def test_api_connection():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_create_event():
    """Test event creation"""
    print("\n🎉 TESTING EVENT CREATION")
    print("-" * 40)
    
    # Create a future event
    future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    end_date = (datetime.now() + timedelta(days=7, hours=4)).strftime("%Y-%m-%d %H:%M:%S")
    
    event_data = {
        "college_id": 1,
        "title": "API Test Workshop",
        "description": "Testing event creation via API",
        "type_id": 1,
        "venue": "Test Lab",
        "start_time": future_date,
        "end_time": end_date,
        "capacity": 25,
        "created_by": 1,
        "semester": "Spring 2024",
        "status": "active"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/events/create", json=event_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Event created successfully")
            print(f"   Event ID: {result['event_id']}")
            print(f"   Title: {result['data']['title']}")
            return result['event_id']
        else:
            print(f"❌ Event creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating event: {e}")
        return None

def test_get_events():
    """Test getting events"""
    print("\n📋 TESTING GET EVENTS")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_BASE}/api/events")
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Retrieved {len(events)} events")
            
            if events:
                event = events[0]
                print(f"   Sample event: {event['title']}")
                print(f"   College: {event['college_name']}")
                print(f"   Type: {event['event_type_name']}")
                print(f"   Capacity: {event['capacity']}")
                print(f"   Available spots: {event['available_spots']}")
            
            return events
        else:
            print(f"❌ Failed to get events: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting events: {e}")
        return []

def test_register_student(event_id):
    """Test student registration"""
    print("\n📝 TESTING STUDENT REGISTRATION")
    print("-" * 40)
    
    if not event_id:
        print("❌ No event ID available for registration test")
        return None
    
    registration_data = {
        "student_id": 1,
        "event_id": event_id,
        "status": "registered"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/registrations/register", json=registration_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Student registered successfully")
            print(f"   Registration ID: {result['registration_id']}")
            print(f"   Student ID: {result['data']['student_id']}")
            print(f"   Event ID: {result['data']['event_id']}")
            return result['registration_id']
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error registering student: {e}")
        return None

def test_mark_attendance(registration_id):
    """Test marking attendance"""
    print("\n✅ TESTING ATTENDANCE MARKING")
    print("-" * 40)
    
    if not registration_id:
        print("❌ No registration ID available for attendance test")
        return None
    
    attendance_data = {
        "registration_id": registration_id,
        "attended": 1,
        "check_in_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/attendance/mark", json=attendance_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Attendance marked successfully")
            print(f"   Attendance ID: {result['attendance_id']}")
            print(f"   Student: {result['data']['student_name']}")
            print(f"   Event: {result['data']['event_title']}")
            print(f"   Attended: {result['data']['attended']}")
            return result['attendance_id']
        else:
            print(f"❌ Attendance marking failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error marking attendance: {e}")
        return None

def test_submit_feedback(registration_id):
    """Test feedback submission"""
    print("\n💬 TESTING FEEDBACK SUBMISSION")
    print("-" * 40)
    
    if not registration_id:
        print("❌ No registration ID available for feedback test")
        return None
    
    feedback_data = {
        "registration_id": registration_id,
        "rating": 5,
        "comments": "Excellent workshop! Very informative and well-structured."
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/feedback/submit", json=feedback_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Feedback submitted successfully")
            print(f"   Feedback ID: {result['feedback_id']}")
            print(f"   Rating: {result['data']['rating']}")
            print(f"   Comments: {result['data']['comments']}")
            return result['feedback_id']
        else:
            print(f"❌ Feedback submission failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error submitting feedback: {e}")
        return None

def test_reports():
    """Test report generation"""
    print("\n📊 TESTING REPORT GENERATION")
    print("-" * 40)
    
    # Test events report
    try:
        response = requests.get(f"{API_BASE}/api/reports/events")
        if response.status_code == 200:
            report = response.json()
            print(f"✅ Events report generated")
            print(f"   Total events: {report['summary']['total_events']}")
            print(f"   Total registrations: {report['summary']['total_registrations']}")
            print(f"   Total attendance: {report['summary']['total_attendance']}")
            print(f"   Average rating: {report['summary']['average_rating']}")
            print(f"   Attendance rate: {report['summary']['attendance_rate']}%")
        else:
            print(f"❌ Events report failed: {response.text}")
    except Exception as e:
        print(f"❌ Error generating events report: {e}")
    
    # Test attendance report
    try:
        response = requests.get(f"{API_BASE}/api/reports/attendance")
        if response.status_code == 200:
            report = response.json()
            print(f"✅ Attendance report generated")
            print(f"   Generated at: {report['generated_at']}")
            print(f"   Records: {len(report['attendance_report'])}")
        else:
            print(f"❌ Attendance report failed: {response.text}")
    except Exception as e:
        print(f"❌ Error generating attendance report: {e}")
    
    # Test feedback report
    try:
        response = requests.get(f"{API_BASE}/api/reports/feedback")
        if response.status_code == 200:
            report = response.json()
            print(f"✅ Feedback report generated")
            print(f"   Generated at: {report['generated_at']}")
            print(f"   Summary records: {len(report['summary'])}")
            print(f"   Detailed records: {len(report['detailed_feedback'])}")
        else:
            print(f"❌ Feedback report failed: {response.text}")
    except Exception as e:
        print(f"❌ Error generating feedback report: {e}")

def test_system_stats():
    """Test system statistics"""
    print("\n📈 TESTING SYSTEM STATISTICS")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_BASE}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ System statistics retrieved")
            print(f"   Colleges: {stats['colleges']}")
            print(f"   Students: {stats['students']}")
            print(f"   Events: {stats['events']}")
            print(f"   Registrations: {stats['registrations']}")
            print(f"   Attendance: {stats['attendance']}")
            print(f"   Feedback: {stats['feedback']}")
            print(f"   Attendance rate: {stats['attendance_rate']}%")
            print(f"   Average rating: {stats['average_rating']}")
        else:
            print(f"❌ System stats failed: {response.text}")
    except Exception as e:
        print(f"❌ Error getting system stats: {e}")

def main():
    """Run all API tests"""
    print("🧪 API TESTING SUITE - EVENT MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Test API connection
    if not test_api_connection():
        print("\n❌ API is not running. Please start the server first:")
        print("   python api_endpoints.py")
        return
    
    # Run tests in sequence
    event_id = test_create_event()
    events = test_get_events()
    registration_id = test_register_student(event_id)
    attendance_id = test_mark_attendance(registration_id)
    feedback_id = test_submit_feedback(registration_id)
    test_reports()
    test_system_stats()
    
    print("\n" + "=" * 60)
    print("🎉 API TESTING COMPLETED!")
    print("=" * 60)
    
    if all([event_id, registration_id, attendance_id, feedback_id]):
        print("✅ All core functionalities working correctly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
