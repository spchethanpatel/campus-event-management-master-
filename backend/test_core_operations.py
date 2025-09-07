#!/usr/bin/env python3
"""
Test Script for Core Operations API
Tests: Student Registration, Attendance Marking, Feedback Collection, Reports
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
            print("✅ Core Operations API is running and healthy")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_student_registration():
    """Test student registration functionality"""
    print("\n📝 TESTING STUDENT REGISTRATION")
    print("-" * 50)
    
    # Test data
    registration_data = {
        "student_id": 1,
        "event_id": 1
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/register-student", json=registration_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Student registered successfully")
            print(f"   Registration ID: {result['registration_id']}")
            print(f"   Student: {result['student_name']}")
            print(f"   Event: {result['event_title']}")
            print(f"   Available spots: {result['available_spots']}")
            return result['registration_id']
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error registering student: {e}")
        return None

def test_get_event_registrations(event_id):
    """Test getting event registrations"""
    print(f"\n📋 TESTING GET EVENT REGISTRATIONS (Event ID: {event_id})")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/api/event-registrations/{event_id}")
        if response.status_code == 200:
            registrations = response.json()
            print(f"✅ Retrieved {len(registrations)} registrations")
            
            if registrations:
                for reg in registrations[:3]:  # Show first 3
                    print(f"   - {reg['student_name']} ({reg['student_email']}) - {reg['status']}")
            
            return registrations
        else:
            print(f"❌ Failed to get registrations: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting registrations: {e}")
        return []

def test_mark_attendance(registration_id):
    """Test marking attendance"""
    print(f"\n✅ TESTING ATTENDANCE MARKING (Registration ID: {registration_id})")
    print("-" * 50)
    
    attendance_data = {
        "registration_id": registration_id,
        "attended": 1,
        "check_in_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/mark-attendance", json=attendance_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Attendance marked successfully")
            print(f"   Attendance ID: {result['attendance_id']}")
            print(f"   Student: {result['student_name']}")
            print(f"   Event: {result['event_title']}")
            print(f"   Attended: {result['attended']}")
            print(f"   Check-in time: {result['check_in_time']}")
            return result['attendance_id']
        else:
            print(f"❌ Attendance marking failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error marking attendance: {e}")
        return None

def test_get_event_attendance(event_id):
    """Test getting event attendance"""
    print(f"\n📊 TESTING GET EVENT ATTENDANCE (Event ID: {event_id})")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/api/event-attendance/{event_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved attendance data")
            print(f"   Event: {result['event_title']}")
            print(f"   Total registrations: {result['total_registrations']}")
            print(f"   Attended count: {result['attended_count']}")
            print(f"   Attendance percentage: {result['attendance_percentage']}%")
            
            if result['attendance_records']:
                print("   Recent attendance records:")
                for record in result['attendance_records'][:3]:
                    status = "✅ Attended" if record['attended'] == 1 else "❌ Absent"
                    print(f"     - {record['student_name']}: {status}")
            
            return result
        else:
            print(f"❌ Failed to get attendance: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting attendance: {e}")
        return None

def test_submit_feedback(registration_id):
    """Test feedback submission"""
    print(f"\n💬 TESTING FEEDBACK SUBMISSION (Registration ID: {registration_id})")
    print("-" * 50)
    
    feedback_data = {
        "registration_id": registration_id,
        "rating": 5,
        "comments": "Excellent event! Very informative and well-organized. The speaker was engaging and the content was relevant to my studies."
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/submit-feedback", json=feedback_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Feedback submitted successfully")
            print(f"   Feedback ID: {result['feedback_id']}")
            print(f"   Student: {result['student_name']}")
            print(f"   Event: {result['event_title']}")
            print(f"   Rating: {result['rating']}/5")
            print(f"   Comments: {result['comments'][:50]}...")
            return result['feedback_id']
        else:
            print(f"❌ Feedback submission failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error submitting feedback: {e}")
        return None

def test_get_event_feedback(event_id):
    """Test getting event feedback"""
    print(f"\n📈 TESTING GET EVENT FEEDBACK (Event ID: {event_id})")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/api/event-feedback/{event_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved feedback data")
            print(f"   Event: {result['event_title']}")
            print(f"   Total feedback: {result['total_feedback']}")
            print(f"   Average rating: {result['average_rating']}/5")
            print(f"   Rating range: {result['min_rating']} - {result['max_rating']}")
            
            if result['feedback_records']:
                print("   Recent feedback:")
                for feedback in result['feedback_records'][:3]:
                    print(f"     - {feedback['student_name']}: {feedback['rating']}/5 - {feedback['comments'][:30]}...")
            
            return result
        else:
            print(f"❌ Failed to get feedback: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting feedback: {e}")
        return None

def test_registrations_report():
    """Test registrations report"""
    print("\n📊 TESTING REGISTRATIONS REPORT")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/api/reports/registrations")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Registrations report generated")
            print(f"   Total events: {result['summary']['total_events']}")
            print(f"   Total registrations: {result['summary']['total_registrations']}")
            print(f"   Average registrations per event: {result['summary']['average_registrations_per_event']}")
            print(f"   Generated at: {result['generated_at']}")
            
            if result['events']:
                print("   Top events by registrations:")
                for event in result['events'][:3]:
                    print(f"     - {event['title']}: {event['total_registrations']} registrations")
            
            return result
        else:
            print(f"❌ Registrations report failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating registrations report: {e}")
        return None

def test_attendance_percentage_report():
    """Test attendance percentage report"""
    print("\n📈 TESTING ATTENDANCE PERCENTAGE REPORT")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/api/reports/attendance-percentage")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Attendance percentage report generated")
            print(f"   Total events: {result['summary']['total_events']}")
            print(f"   Total registrations: {result['summary']['total_registrations']}")
            print(f"   Total attended: {result['summary']['total_attended']}")
            print(f"   Overall attendance percentage: {result['summary']['overall_attendance_percentage']}%")
            print(f"   Average attendance percentage: {result['summary']['average_attendance_percentage']}%")
            print(f"   Generated at: {result['generated_at']}")
            
            if result['events']:
                print("   Event attendance rates:")
                for event in result['events'][:3]:
                    print(f"     - {event['title']}: {event['attendance_percentage']}% ({event['attended_count']}/{event['total_registrations']})")
            
            return result
        else:
            print(f"❌ Attendance percentage report failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating attendance percentage report: {e}")
        return None

def test_average_feedback_report():
    """Test average feedback report"""
    print("\n⭐ TESTING AVERAGE FEEDBACK REPORT")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/api/reports/average-feedback")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Average feedback report generated")
            print(f"   Events with feedback: {result['summary']['total_events_with_feedback']}")
            print(f"   Total feedback: {result['summary']['total_feedback']}")
            print(f"   Overall average rating: {result['summary']['overall_average_rating']}/5")
            print(f"   Average rating per event: {result['summary']['average_rating_per_event']}/5")
            print(f"   Generated at: {result['generated_at']}")
            
            if result['events']:
                print("   Event feedback ratings:")
                for event in result['events'][:3]:
                    print(f"     - {event['title']}: {event['average_rating']}/5 ({event['total_feedback']} reviews)")
            
            return result
        else:
            print(f"❌ Average feedback report failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating average feedback report: {e}")
        return None

def main():
    """Run all core operations tests"""
    print("🧪 CORE OPERATIONS API TESTING SUITE")
    print("=" * 60)
    
    # Test API connection
    if not test_api_connection():
        print("\n❌ API is not running. Please start the server first:")
        print("   python core_operations.py")
        return
    
    # Run tests in sequence
    registration_id = test_student_registration()
    registrations = test_get_event_registrations(1)
    attendance_id = test_mark_attendance(registration_id) if registration_id else None
    attendance_data = test_get_event_attendance(1)
    feedback_id = test_submit_feedback(registration_id) if registration_id else None
    feedback_data = test_get_event_feedback(1)
    
    # Test reports
    registrations_report = test_registrations_report()
    attendance_report = test_attendance_percentage_report()
    feedback_report = test_average_feedback_report()
    
    print("\n" + "=" * 60)
    print("🎉 CORE OPERATIONS TESTING COMPLETED!")
    print("=" * 60)
    
    # Summary
    tests_passed = sum([
        registration_id is not None,
        len(registrations) > 0,
        attendance_id is not None,
        attendance_data is not None,
        feedback_id is not None,
        feedback_data is not None,
        registrations_report is not None,
        attendance_report is not None,
        feedback_report is not None
    ])
    
    total_tests = 9
    print(f"✅ Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All core operations working perfectly!")
    elif tests_passed >= 6:
        print("✅ Most operations working - minor issues detected")
    else:
        print("❌ Multiple issues detected - check the output above")

if __name__ == "__main__":
    main()
