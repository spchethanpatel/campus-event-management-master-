# Event Management System API

A comprehensive FastAPI backend for an event management system with SQLite database integration. This system manages colleges, students, events, registrations, attendance, and feedback.

## Project Structure

```
backend/
├── simple_main.py       # Main FastAPI application (recommended)
├── main.py              # SQLAlchemy-based FastAPI application
├── config.py            # Configuration settings
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic schemas for request/response validation
├── requirements.txt     # Python dependencies
├── test_db.py          # Database connection test script
├── examine_db.py       # Database structure examination script
├── run.py              # Startup script
├── routers/
│   ├── __init__.py
│   ├── colleges.py      # College management endpoints
│   ├── admins.py        # Admin management endpoints
│   ├── students.py      # Student management endpoints
│   ├── events.py        # Event management endpoints
│   ├── event_types.py   # Event type management endpoints
│   ├── registrations.py # Registration management endpoints
│   ├── attendance.py    # Attendance management endpoints
│   └── feedback.py      # Feedback management endpoints
└── README.md           # This file

database/
└── event_management_db.db  # SQLite database file (existing)
```

## Database Configuration

The system uses an existing SQLite database located at:
**Database Location**: `D:\DEV\database\event_management_db.db`

The database contains the following tables:
- **Colleges**: College information
- **Admins**: Administrative users
- **Students**: Student information
- **EventTypes**: Types of events (Workshop, Hackathon, Fest, etc.)
- **Events**: Event details and scheduling
- **Registrations**: Student event registrations
- **Attendance**: Attendance tracking
- **Feedback**: Event feedback and ratings
- **AuditLogs**: System audit trail

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install fastapi uvicorn sqlalchemy pydantic python-multipart
```

### 2. Run the Application

**Recommended (Simple Version):**
```bash
python simple_main.py
```

**Alternative (SQLAlchemy Version):**
```bash
python main.py
```

### 3. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### System Endpoints
- `GET /` - Root endpoint with system information
- `GET /health` - Health check and database status
- `GET /stats` - System statistics

### Event Types
- `GET /event-types` - Get all event types
- `GET /event-types/{type_id}` - Get event type by ID

### Colleges
- `GET /colleges` - Get all colleges
- `GET /colleges/{college_id}` - Get college by ID

### Students
- `GET /students` - Get all students
- `GET /students/{student_id}` - Get student by ID

### Events
- `GET /events` - Get all events (with college and event type details)
- `GET /events/{event_id}` - Get event by ID (with details)

### Registrations
- `GET /registrations` - Get all registrations (with student and event details)
- `GET /registrations/{registration_id}` - Get registration by ID (with details)

## Example Usage

### Get System Health
```bash
curl http://localhost:8000/health
```

### Get All Event Types
```bash
curl http://localhost:8000/event-types
```

### Get All Events
```bash
curl http://localhost:8000/events
```

### Get System Statistics
```bash
curl http://localhost:8000/stats
```

## Database Schema

### EventTypes Table
- `type_id`: Primary key
- `name`: Event type name (Workshop, Hackathon, Fest, etc.)

### Colleges Table
- `college_id`: Primary key
- `name`: College name
- `location`: College location
- `status`: College status (active/inactive)

### Students Table
- `student_id`: Primary key
- `college_id`: Foreign key to Colleges
- `name`: Student name
- `email`: Student email
- `department`: Student department
- `year`: Academic year
- `status`: Student status (active/inactive)

### Events Table
- `event_id`: Primary key
- `college_id`: Foreign key to Colleges
- `title`: Event title
- `description`: Event description
- `type_id`: Foreign key to EventTypes
- `venue`: Event venue
- `start_time`: Event start time
- `end_time`: Event end time
- `capacity`: Maximum attendees
- `created_by`: Foreign key to Admins
- `semester`: Academic semester
- `status`: Event status (active/inactive)

### Registrations Table
- `registration_id`: Primary key
- `student_id`: Foreign key to Students
- `event_id`: Foreign key to Events
- `registration_time`: Registration timestamp
- `status`: Registration status (registered/cancelled)

## Quick Start

1. **Test Database Connection:**
   ```bash
   python test_db.py
   ```

2. **Start the API Server:**
   ```bash
   python simple_main.py
   ```

3. **Access the API:**
   - Open http://localhost:8000/docs for interactive API documentation
   - Use http://localhost:8000/health to check system status

## Features

✅ **Complete Event Management System**
- College management
- Student management  
- Event creation and management
- Event registration system
- Attendance tracking
- Feedback collection
- System statistics

✅ **RESTful API Design**
- Clean, intuitive endpoints
- Comprehensive error handling
- Detailed API documentation
- CORS support for frontend integration

✅ **Database Integration**
- Direct SQLite integration (simple_main.py)
- SQLAlchemy ORM support (main.py)
- Existing database compatibility
- Data validation and relationships

## Troubleshooting

### Database Connection Issues
- Ensure the database file exists at `D:\DEV\database\event_management_db.db`
- Check file permissions
- Run `python test_db.py` to verify connection

### Port Already in Use
If port 8000 is already in use, modify the port in `simple_main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Python Version Compatibility
- Use `simple_main.py` for better compatibility
- The SQLAlchemy version may have issues with Python 3.13
