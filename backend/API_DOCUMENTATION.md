# Event Management System API Documentation

## 🚀 Complete API Endpoints for Event Management

### **Base URL**: `http://localhost:8000`

---

## 📋 **API Endpoints Overview**

### **1. Event Management**
- `POST /api/events/create` - Create a new event
- `GET /api/events` - Get all events (with filtering)
- `GET /api/events/{event_id}` - Get specific event details

### **2. Student Registration**
- `POST /api/registrations/register` - Register student for event
- `GET /api/registrations` - Get registrations (with filtering)

### **3. Attendance Management**
- `POST /api/attendance/mark` - Mark attendance
- `GET /api/attendance` - Get attendance records

### **4. Feedback System**
- `POST /api/feedback/submit` - Submit feedback

### **5. Report Generation**
- `GET /api/reports/events` - Events report
- `GET /api/reports/attendance` - Attendance report
- `GET /api/reports/feedback` - Feedback report

### **6. System Endpoints**
- `GET /api/health` - Health check
- `GET /api/stats` - System statistics

---

## 🎉 **Event Management Endpoints**

### **Create Event**
```http
POST /api/events/create
Content-Type: application/json

{
  "college_id": 1,
  "title": "Python Workshop 2024",
  "description": "Learn Python programming from basics to advanced",
  "type_id": 1,
  "venue": "Computer Lab A",
  "start_time": "2024-04-15 09:00:00",
  "end_time": "2024-04-15 17:00:00",
  "capacity": 30,
  "created_by": 1,
  "semester": "Spring 2024",
  "status": "active"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Event created successfully",
  "event_id": 7,
  "data": { ... }
}
```

### **Get Events**
```http
GET /api/events?college_id=1&event_type_id=1&status=active&limit=50
```

**Response:**
```json
[
  {
    "event_id": 7,
    "title": "Python Workshop 2024",
    "description": "Learn Python programming...",
    "venue": "Computer Lab A",
    "start_time": "2024-04-15 09:00:00",
    "end_time": "2024-04-15 17:00:00",
    "capacity": 30,
    "current_registrations": 5,
    "available_spots": 25,
    "college_name": "University of Technology",
    "event_type_name": "Workshop",
    "created_by_name": "John Smith"
  }
]
```

### **Get Event Details**
```http
GET /api/events/7
```

---

## 📝 **Student Registration Endpoints**

### **Register Student**
```http
POST /api/registrations/register
Content-Type: application/json

{
  "student_id": 1,
  "event_id": 7,
  "status": "registered"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Student registered successfully",
  "registration_id": 15,
  "data": {
    "student_id": 1,
    "event_id": 7,
    "status": "registered"
  }
}
```

### **Get Registrations**
```http
GET /api/registrations?event_id=7&student_id=1&status=registered
```

**Response:**
```json
[
  {
    "registration_id": 15,
    "student_id": 1,
    "event_id": 7,
    "registration_time": "2024-01-15 10:30:00",
    "status": "registered",
    "student_name": "John Doe",
    "student_email": "john.doe@university.edu",
    "event_title": "Python Workshop 2024",
    "event_start": "2024-04-15 09:00:00",
    "college_name": "University of Technology"
  }
]
```

---

## ✅ **Attendance Management Endpoints**

### **Mark Attendance**
```http
POST /api/attendance/mark
Content-Type: application/json

{
  "registration_id": 15,
  "attended": 1,
  "check_in_time": "2024-04-15 09:15:00"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Attendance marked successfully",
  "attendance_id": 8,
  "data": {
    "registration_id": 15,
    "attended": 1,
    "check_in_time": "2024-04-15 09:15:00",
    "student_name": "John Doe",
    "event_title": "Python Workshop 2024"
  }
}
```

### **Get Attendance Records**
```http
GET /api/attendance?event_id=7&registration_id=15
```

**Response:**
```json
[
  {
    "attendance_id": 8,
    "registration_id": 15,
    "attended": 1,
    "check_in_time": "2024-04-15 09:15:00",
    "student_name": "John Doe",
    "student_email": "john.doe@university.edu",
    "event_title": "Python Workshop 2024",
    "event_start": "2024-04-15 09:00:00"
  }
]
```

---

## 💬 **Feedback Endpoints**

### **Submit Feedback**
```http
POST /api/feedback/submit
Content-Type: application/json

{
  "registration_id": 15,
  "rating": 5,
  "comments": "Excellent workshop! Very informative and well-structured."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_id": 12,
  "data": {
    "registration_id": 15,
    "rating": 5,
    "comments": "Excellent workshop! Very informative and well-structured.",
    "student_name": "John Doe",
    "event_title": "Python Workshop 2024"
  }
}
```

---

## 📊 **Report Generation Endpoints**

### **Events Report**
```http
GET /api/reports/events?start_date=2024-01-01&end_date=2024-12-31&college_id=1
```

**Response:**
```json
{
  "summary": {
    "total_events": 10,
    "total_registrations": 150,
    "total_attendance": 120,
    "average_rating": 4.2,
    "attendance_rate": 80.0
  },
  "events": [
    {
      "event_id": 7,
      "title": "Python Workshop 2024",
      "college_name": "University of Technology",
      "event_type_name": "Workshop",
      "total_registrations": 25,
      "total_attendance": 20,
      "avg_rating": 4.5
    }
  ]
}
```

### **Attendance Report**
```http
GET /api/reports/attendance?event_id=7&start_date=2024-01-01&end_date=2024-12-31
```

**Response:**
```json
{
  "attendance_report": [
    {
      "event_id": 7,
      "event_title": "Python Workshop 2024",
      "start_time": "2024-04-15 09:00:00",
      "total_registrations": 25,
      "attended_count": 20,
      "attendance_rate": 80.0
    }
  ],
  "generated_at": "2024-01-15 14:30:00"
}
```

### **Feedback Report**
```http
GET /api/reports/feedback?event_id=7&min_rating=4
```

**Response:**
```json
{
  "summary": [
    {
      "event_id": 7,
      "event_title": "Python Workshop 2024",
      "total_feedback": 15,
      "average_rating": 4.5,
      "min_rating": 3,
      "max_rating": 5
    }
  ],
  "detailed_feedback": [
    {
      "feedback_id": 12,
      "registration_id": 15,
      "rating": 5,
      "comments": "Excellent workshop!",
      "submitted_at": "2024-04-15 18:00:00",
      "student_name": "John Doe",
      "event_title": "Python Workshop 2024"
    }
  ],
  "generated_at": "2024-01-15 14:30:00"
}
```

---

## 🔧 **System Endpoints**

### **Health Check**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "database_connected": true,
  "total_events": 10,
  "timestamp": "2024-01-15 14:30:00"
}
```

### **System Statistics**
```http
GET /api/stats
```

**Response:**
```json
{
  "colleges": 4,
  "students": 8,
  "events": 10,
  "registrations": 25,
  "attendance": 20,
  "feedback": 15,
  "attendance_rate": 80.0,
  "average_rating": 4.2
}
```

---

## 🚀 **How to Use the API**

### **1. Start the API Server**
```bash
cd backend
python api_endpoints.py
```

### **2. Access API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **3. Test the API**
```bash
python api_test.py
```

### **4. Example Usage with curl**

**Create an Event:**
```bash
curl -X POST "http://localhost:8000/api/events/create" \
     -H "Content-Type: application/json" \
     -d '{
       "college_id": 1,
       "title": "API Test Event",
       "description": "Testing API",
       "type_id": 1,
       "venue": "Test Lab",
       "start_time": "2024-04-20 10:00:00",
       "end_time": "2024-04-20 16:00:00",
       "capacity": 20,
       "created_by": 1,
       "semester": "Spring 2024"
     }'
```

**Register a Student:**
```bash
curl -X POST "http://localhost:8000/api/registrations/register" \
     -H "Content-Type: application/json" \
     -d '{
       "student_id": 1,
       "event_id": 7,
       "status": "registered"
     }'
```

**Mark Attendance:**
```bash
curl -X POST "http://localhost:8000/api/attendance/mark" \
     -H "Content-Type: application/json" \
     -d '{
       "registration_id": 15,
       "attended": 1,
       "check_in_time": "2024-04-15 09:15:00"
     }'
```

**Submit Feedback:**
```bash
curl -X POST "http://localhost:8000/api/feedback/submit" \
     -H "Content-Type: application/json" \
     -d '{
       "registration_id": 15,
       "rating": 5,
       "comments": "Great event!"
     }'
```

---

## 📋 **Error Handling**

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `500` - Internal Server Error

Error responses include detailed messages:
```json
{
  "detail": "Student already registered for this event"
}
```

---

## 🔒 **Data Validation**

- **Event Creation**: Validates college, event type, and admin existence
- **Registration**: Checks event capacity and prevents duplicate registrations
- **Attendance**: Ensures registration exists before marking attendance
- **Feedback**: Validates rating (1-5) and requires attendance

---

## 📊 **Key Features**

✅ **Complete CRUD Operations** for all entities
✅ **Data Validation** and error handling
✅ **Comprehensive Reporting** with statistics
✅ **Real-time Statistics** and health monitoring
✅ **Flexible Filtering** for all endpoints
✅ **RESTful Design** following best practices
✅ **Interactive Documentation** with Swagger UI
✅ **Comprehensive Testing** suite included
