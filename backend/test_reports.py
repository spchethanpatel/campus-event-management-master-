#!/usr/bin/env python3
"""
Test Script for Reports API
Tests: Event Popularity Report, Student Participation Report
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
API_BASE = "http://localhost:8000"

def test_api_connection():
    """Test if Reports API is running"""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Reports API is running and healthy")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_event_popularity_report():
    """Test Event Popularity Report"""
    print("\n📊 TESTING EVENT POPULARITY REPORT")
    print("-" * 50)
    
    try:
        # Test basic report
        response = requests.get(f"{API_BASE}/api/reports/event-popularity")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Event Popularity Report generated successfully")
            print(f"   Report Type: {result['report_type']}")
            print(f"   Total Events: {result['summary']['total_events']}")
            print(f"   Total Registrations: {result['summary']['total_registrations']}")
            print(f"   Average Registrations per Event: {result['summary']['average_registrations_per_event']}")
            print(f"   Generated at: {result['generated_at']}")
            
            if result['summary']['most_popular_event']:
                most_popular = result['summary']['most_popular_event']
                print(f"   Most Popular Event: {most_popular['title']} ({most_popular['registrations']} registrations)")
            
            if result['events']:
                print(f"\n🏆 Top 5 Most Popular Events:")
                for i, event in enumerate(result['events'][:5], 1):
                    print(f"   {i}. {event['title']} - {event['total_registrations']} registrations")
            
            return result
        else:
            print(f"❌ Event Popularity Report failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating Event Popularity Report: {e}")
        return None

def test_event_popularity_with_filters():
    """Test Event Popularity Report with filters"""
    print("\n🔍 TESTING EVENT POPULARITY REPORT WITH FILTERS")
    print("-" * 50)
    
    try:
        # Test with various filters
        params = {
            "limit": 10,
            "sort_order": "desc",
            "min_registrations": 1
        }
        
        response = requests.get(f"{API_BASE}/api/reports/event-popularity", params=params)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Filtered Event Popularity Report generated")
            print(f"   Filters applied: {result['filters_applied']}")
            print(f"   Events returned: {len(result['events'])}")
            
            if result['events']:
                print(f"   Sample filtered results:")
                for event in result['events'][:3]:
                    print(f"     - {event['title']}: {event['total_registrations']} registrations")
            
            return result
        else:
            print(f"❌ Filtered Event Popularity Report failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating filtered Event Popularity Report: {e}")
        return None

def test_student_participation_report():
    """Test Student Participation Report"""
    print("\n👥 TESTING STUDENT PARTICIPATION REPORT")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/api/reports/student-participation")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Student Participation Report generated successfully")
            print(f"   Report Type: {result['report_type']}")
            print(f"   Total Students: {result['summary']['total_students']}")
            print(f"   Total Events Attended: {result['summary']['total_events_attended']}")
            print(f"   Average Events per Student: {result['summary']['average_events_per_student']}")
            print(f"   Generated at: {result['generated_at']}")
            
            if result['summary']['most_active_student']:
                most_active = result['summary']['most_active_student']
                print(f"   Most Active Student: {most_active['name']} ({most_active['events_attended']} events)")
            
            # Show participation categories
            categories = result['summary']['participation_categories']
            print(f"\n📊 Participation Categories:")
            print(f"   Highly Active (5+ events): {categories['highly_active']} students")
            print(f"   Moderately Active (2-4 events): {categories['moderately_active']} students")
            print(f"   Low Active (<2 events): {categories['low_active']} students")
            
            if result['students']:
                print(f"\n🏆 Top 5 Most Active Students:")
                for i, student in enumerate(result['students'][:5], 1):
                    print(f"   {i}. {student['student_name']} - {student['total_events_attended']} events attended")
            
            return result
        else:
            print(f"❌ Student Participation Report failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating Student Participation Report: {e}")
        return None

def test_student_participation_with_filters():
    """Test Student Participation Report with filters"""
    print("\n🔍 TESTING STUDENT PARTICIPATION REPORT WITH FILTERS")
    print("-" * 50)
    
    try:
        # Test with filters
        params = {
            "limit": 10,
            "sort_order": "desc",
            "min_events_attended": 1
        }
        
        response = requests.get(f"{API_BASE}/api/reports/student-participation", params=params)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Filtered Student Participation Report generated")
            print(f"   Filters applied: {result['filters_applied']}")
            print(f"   Students returned: {len(result['students'])}")
            
            if result['students']:
                print(f"   Sample filtered results:")
                for student in result['students'][:3]:
                    print(f"     - {student['student_name']}: {student['total_events_attended']} events attended")
            
            return result
        else:
            print(f"❌ Filtered Student Participation Report failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating filtered Student Participation Report: {e}")
        return None

def test_detailed_student_participation():
    """Test detailed student participation for a specific student"""
    print("\n👤 TESTING DETAILED STUDENT PARTICIPATION")
    print("-" * 50)
    
    try:
        # Test with student ID 1
        student_id = 1
        response = requests.get(f"{API_BASE}/api/reports/student-participation/{student_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Detailed Student Participation Report generated")
            print(f"   Student: {result['student_info']['name']}")
            print(f"   Email: {result['student_info']['email']}")
            print(f"   College: {result['student_info']['college_name']}")
            
            summary = result['participation_summary']
            print(f"\n📊 Participation Summary:")
            print(f"   Total Registrations: {summary['total_registrations']}")
            print(f"   Total Attended: {summary['total_attended']}")
            print(f"   Attendance Rate: {summary['attendance_rate']}%")
            print(f"   Total Feedback Submitted: {summary['total_feedback_submitted']}")
            print(f"   Average Rating: {summary['average_rating']}/5")
            
            if result['participation_records']:
                print(f"\n📋 Recent Participation Records:")
                for record in result['participation_records'][:3]:
                    status = "✅ Attended" if record['attended'] == 1 else "❌ Absent"
                    rating = f" ({record['rating']}/5)" if record['rating'] else ""
                    print(f"     - {record['event_title']}: {status}{rating}")
            
            return result
        else:
            print(f"❌ Detailed Student Participation Report failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating Detailed Student Participation Report: {e}")
        return None

def test_report_performance():
    """Test report generation performance"""
    print("\n⚡ TESTING REPORT PERFORMANCE")
    print("-" * 50)
    
    import time
    
    # Test Event Popularity Report performance
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE}/api/reports/event-popularity?limit=100")
        end_time = time.time()
        
        if response.status_code == 200:
            duration = end_time - start_time
            result = response.json()
            print(f"✅ Event Popularity Report (100 events): {duration:.2f} seconds")
            print(f"   Events processed: {len(result['events'])}")
        else:
            print(f"❌ Event Popularity Report performance test failed")
    except Exception as e:
        print(f"❌ Error in Event Popularity Report performance test: {e}")
    
    # Test Student Participation Report performance
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE}/api/reports/student-participation?limit=100")
        end_time = time.time()
        
        if response.status_code == 200:
            duration = end_time - start_time
            result = response.json()
            print(f"✅ Student Participation Report (100 students): {duration:.2f} seconds")
            print(f"   Students processed: {len(result['students'])}")
        else:
            print(f"❌ Student Participation Report performance test failed")
    except Exception as e:
        print(f"❌ Error in Student Participation Report performance test: {e}")

def main():
    """Run all reports tests"""
    print("🧪 REPORTS API TESTING SUITE")
    print("=" * 60)
    
    # Test API connection
    if not test_api_connection():
        print("\n❌ API is not running. Please start the server first:")
        print("   python reports_api.py")
        return
    
    # Run tests
    event_report = test_event_popularity_report()
    event_filtered_report = test_event_popularity_with_filters()
    student_report = test_student_participation_report()
    student_filtered_report = test_student_participation_with_filters()
    detailed_student_report = test_detailed_student_participation()
    test_report_performance()
    
    print("\n" + "=" * 60)
    print("🎉 REPORTS TESTING COMPLETED!")
    print("=" * 60)
    
    # Summary
    tests_passed = sum([
        event_report is not None,
        event_filtered_report is not None,
        student_report is not None,
        student_filtered_report is not None,
        detailed_student_report is not None
    ])
    
    total_tests = 5
    print(f"✅ Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All reports working perfectly!")
        print("\n📊 Available Reports:")
        print("   - Event Popularity Report: /api/reports/event-popularity")
        print("   - Student Participation Report: /api/reports/student-participation")
        print("   - Detailed Student Participation: /api/reports/student-participation/{student_id}")
    elif tests_passed >= 3:
        print("✅ Most reports working - minor issues detected")
    else:
        print("❌ Multiple issues detected - check the output above")

if __name__ == "__main__":
    main()
