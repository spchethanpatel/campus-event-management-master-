# Event Management System - Reports Documentation

## 📊 Comprehensive Reporting System

This documentation covers the advanced reporting capabilities of the Event Management System, including Event Popularity Reports and Student Participation Reports.

---

## 🎯 **Available Reports**

### **1. Event Popularity Report**
- **Purpose**: Analyze event popularity based on registration numbers
- **Sorting**: Events sorted by number of registrations (descending by default)
- **Key Metrics**: Total registrations, attendance rates, feedback scores

### **2. Student Participation Report**
- **Purpose**: Track student engagement and participation levels
- **Sorting**: Students sorted by number of events attended (descending by default)
- **Key Metrics**: Events attended, attendance rates, feedback contributions

---

## 🚀 **API Endpoints**

### **Event Popularity Report**
```http
GET /api/reports/event-popularity
```

**Query Parameters:**
- `start_date` (optional): Filter events from this date (YYYY-MM-DD)
- `end_date` (optional): Filter events until this date (YYYY-MM-DD)
- `college_id` (optional): Filter by specific college
- `event_type_id` (optional): Filter by event type
- `min_registrations` (optional): Minimum number of registrations
- `max_registrations` (optional): Maximum number of registrations
- `limit` (default: 50): Maximum number of results
- `sort_order` (default: "desc"): Sort order ("asc" or "desc")

**Example Request:**
```bash
curl "http://localhost:8000/api/reports/event-popularity?limit=10&sort_order=desc&min_registrations=5"
```

**Response Structure:**
```json
{
  "report_type": "Event Popularity Report",
  "generated_at": "2024-01-15 14:30:00",
  "filters_applied": {
    "limit": 10,
    "sort_order": "desc",
    "min_registrations": 5
  },
  "summary": {
    "total_events": 15,
    "total_registrations": 150,
    "total_attendance": 120,
    "average_registrations_per_event": 10.0,
    "average_attendance_rate": 80.0,
    "average_rating": 4.2,
    "most_popular_event": {
      "title": "Python Workshop 2024",
      "registrations": 25
    },
    "least_popular_event": {
      "title": "Basic SQL Training",
      "registrations": 3
    }
  },
  "events": [
    {
      "event_id": 1,
      "title": "Python Workshop 2024",
      "description": "Learn Python programming...",
      "start_time": "2024-04-15 09:00:00",
      "end_time": "2024-04-15 17:00:00",
      "venue": "Computer Lab A",
      "capacity": 30,
      "status": "completed",
      "college_name": "University of Technology",
      "event_type_name": "Workshop",
      "created_by_name": "John Smith",
      "total_registrations": 25,
      "total_attendance": 20,
      "total_feedback": 18,
      "average_rating": 4.5,
      "attendance_rate": 80.0
    }
  ]
}
```

### **Student Participation Report**
```http
GET /api/reports/student-participation
```

**Query Parameters:**
- `start_date` (optional): Filter events from this date (YYYY-MM-DD)
- `end_date` (optional): Filter events until this date (YYYY-MM-DD)
- `college_id` (optional): Filter by specific college
- `min_events_attended` (optional): Minimum events attended
- `max_events_attended` (optional): Maximum events attended
- `limit` (default: 100): Maximum number of results
- `sort_order` (default: "desc"): Sort order ("asc" or "desc")

**Example Request:**
```bash
curl "http://localhost:8000/api/reports/student-participation?limit=20&sort_order=desc&min_events_attended=2"
```

**Response Structure:**
```json
{
  "report_type": "Student Participation Report",
  "generated_at": "2024-01-15 14:30:00",
  "filters_applied": {
    "limit": 20,
    "sort_order": "desc",
    "min_events_attended": 2
  },
  "summary": {
    "total_students": 50,
    "total_events_registered": 200,
    "total_events_attended": 160,
    "average_events_per_student": 4.0,
    "average_attendance_rate": 80.0,
    "average_feedback_rating": 4.2,
    "most_active_student": {
      "name": "Alice Johnson",
      "events_attended": 8
    },
    "least_active_student": {
      "name": "Bob Smith",
      "events_attended": 1
    },
    "participation_categories": {
      "highly_active": 10,
      "moderately_active": 25,
      "low_active": 15
    }
  },
  "students": [
    {
      "student_id": 1,
      "student_name": "Alice Johnson",
      "student_email": "alice.johnson@university.edu",
      "phone": "+1234567890",
      "semester": "Spring 2024",
      "college_name": "University of Technology",
      "total_events_registered": 8,
      "total_events_attended": 8,
      "total_feedback_submitted": 7,
      "average_feedback_rating": 4.6,
      "attendance_rate": 100.0
    }
  ]
}
```

### **Detailed Student Participation**
```http
GET /api/reports/student-participation/{student_id}
```

**Example Request:**
```bash
curl "http://localhost:8000/api/reports/student-participation/1"
```

**Response Structure:**
```json
{
  "student_info": {
    "student_id": 1,
    "name": "Alice Johnson",
    "email": "alice.johnson@university.edu",
    "phone": "+1234567890",
    "semester": "Spring 2024",
    "college_name": "University of Technology"
  },
  "participation_summary": {
    "total_registrations": 8,
    "total_attended": 8,
    "total_feedback_submitted": 7,
    "attendance_rate": 100.0,
    "average_rating": 4.6
  },
  "participation_records": [
    {
      "event_id": 1,
      "event_title": "Python Workshop 2024",
      "start_time": "2024-04-15 09:00:00",
      "end_time": "2024-04-15 17:00:00",
      "venue": "Computer Lab A",
      "event_type_name": "Workshop",
      "registration_time": "2024-04-10 10:30:00",
      "registration_status": "registered",
      "attended": 1,
      "check_in_time": "2024-04-15 09:15:00",
      "rating": 5,
      "comments": "Excellent workshop!",
      "feedback_submitted_at": "2024-04-15 18:00:00"
    }
  ],
  "generated_at": "2024-01-15 14:30:00"
}
```

---

## 🛠️ **Standalone Report Generation**

### **Using the Report Generator Script**

```bash
# Generate all reports
python generate_reports.py

# The script will create:
# - event_popularity_report_YYYYMMDD_HHMMSS.json
# - student_participation_report_YYYYMMDD_HHMMSS.json
# - event_popularity_report_YYYYMMDD_HHMMSS.csv
# - student_participation_report_YYYYMMDD_HHMMSS.csv
```

### **Programmatic Usage**

```python
from generate_reports import ReportGenerator

generator = ReportGenerator()
generator.connect_db()

# Generate Event Popularity Report
event_report = generator.generate_event_popularity_report(
    start_date="2024-01-01",
    end_date="2024-12-31",
    college_id=1,
    sort_order="desc",
    limit=20
)

# Generate Student Participation Report
student_report = generator.generate_student_participation_report(
    start_date="2024-01-01",
    end_date="2024-12-31",
    college_id=1,
    min_events_attended=2,
    sort_order="desc",
    limit=50
)

# Export to files
generator.export_to_json(event_report, "event_report.json")
generator.export_to_csv(event_report, "event_report.csv")

generator.close_db()
```

---

## 📈 **Key Metrics Explained**

### **Event Popularity Metrics**
- **Total Registrations**: Number of students who registered for the event
- **Total Attendance**: Number of students who actually attended
- **Attendance Rate**: Percentage of registered students who attended
- **Total Feedback**: Number of feedback submissions received
- **Average Rating**: Average feedback rating (1-5 scale)

### **Student Participation Metrics**
- **Total Events Registered**: Number of events the student registered for
- **Total Events Attended**: Number of events the student actually attended
- **Attendance Rate**: Percentage of registered events that were attended
- **Total Feedback Submitted**: Number of feedback submissions made
- **Average Feedback Rating**: Average rating given by the student

### **Participation Categories**
- **Highly Active**: Students who attended 5+ events
- **Moderately Active**: Students who attended 2-4 events
- **Low Active**: Students who attended less than 2 events

---

## 🧪 **Testing the Reports**

### **Run API Tests**
```bash
python test_reports.py
```

### **Test Individual Endpoints**
```bash
# Test Event Popularity Report
curl "http://localhost:8000/api/reports/event-popularity?limit=5"

# Test Student Participation Report
curl "http://localhost:8000/api/reports/student-participation?limit=5"

# Test Detailed Student Participation
curl "http://localhost:8000/api/reports/student-participation/1"
```

---

## 🚀 **Starting the Reports API**

```bash
# Start the Reports API server
python reports_api.py

# Access the API documentation
# Swagger UI: http://localhost:8000/docs
# Health Check: http://localhost:8000/api/health
```

---

## 📊 **Report Examples**

### **Most Popular Events**
```json
{
  "events": [
    {
      "title": "Python Workshop 2024",
      "total_registrations": 25,
      "attendance_rate": 80.0,
      "average_rating": 4.5
    },
    {
      "title": "Data Science Bootcamp",
      "total_registrations": 20,
      "attendance_rate": 85.0,
      "average_rating": 4.3
    }
  ]
}
```

### **Most Active Students**
```json
{
  "students": [
    {
      "student_name": "Alice Johnson",
      "total_events_attended": 8,
      "attendance_rate": 100.0,
      "average_feedback_rating": 4.6
    },
    {
      "student_name": "Bob Smith",
      "total_events_attended": 6,
      "attendance_rate": 85.7,
      "average_feedback_rating": 4.2
    }
  ]
}
```

---

## 🔧 **Customization Options**

### **Filtering Options**
- **Date Range**: Filter events/participation within specific time periods
- **College**: Focus on specific colleges or institutions
- **Event Type**: Analyze specific types of events (workshops, seminars, etc.)
- **Registration Count**: Filter events by popularity thresholds
- **Participation Level**: Focus on students with specific activity levels

### **Sorting Options**
- **Ascending/Descending**: Sort by any metric in either direction
- **Multiple Criteria**: Primary sort by main metric, secondary by date/name

### **Export Formats**
- **JSON**: Full structured data with all details
- **CSV**: Tabular format for spreadsheet analysis
- **Custom Fields**: Select specific fields for export

---

## 📋 **Best Practices**

1. **Use Filters**: Apply relevant filters to focus on specific data subsets
2. **Limit Results**: Use appropriate limits to avoid overwhelming responses
3. **Regular Generation**: Generate reports regularly for trend analysis
4. **Export Data**: Save reports in both JSON and CSV formats for different use cases
5. **Monitor Performance**: Use the performance testing features to ensure optimal response times

---

## 🎯 **Use Cases**

### **Event Organizers**
- Identify most popular event types
- Analyze attendance patterns
- Track feedback trends
- Plan future events based on popularity data

### **Student Affairs**
- Monitor student engagement levels
- Identify highly active students for recognition
- Support students with low participation
- Analyze participation by college or semester

### **Administrators**
- Generate institutional reports
- Track system-wide engagement metrics
- Identify trends and patterns
- Make data-driven decisions

---

## 🚨 **Error Handling**

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (student/event not found)
- `500`: Internal Server Error

Error responses include detailed messages:
```json
{
  "detail": "Student not found"
}
```

---

## 📞 **Support**

For issues or questions about the reporting system:
1. Check the API documentation at `/docs`
2. Run the test suite with `python test_reports.py`
3. Verify database connectivity and data integrity
4. Review the generated logs for detailed error information
