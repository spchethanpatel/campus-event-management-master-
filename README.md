# Campus Event Management System

A comprehensive event management system designed for educational institutions to manage campus events, student registrations, and administrative tasks.

## 🚧 Project Status

**Current Status**: Database design and backend implementation completed, UI development in progress.

### ✅ Completed Components
- **Database Design**: Complete SQLite database with comprehensive schema
- **Backend API**: Full REST API implementation with FastAPI
- **Authentication**: Student and teacher authentication systems
- **Core Features**: Event management, registration, attendance tracking
- **Multi-College Support**: Scalable architecture for multiple institutions

### 🔄 In Progress
- **Frontend UI**: React-based user interface (partially implemented)
- **UI Polish**: Complete responsive design and user experience

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Database**: SQLite with comprehensive schema
- **API**: RESTful endpoints for all operations
- **Authentication**: JWT-based authentication
- **Features**: Event management, registration, attendance, feedback, reporting

### Frontend (React/TypeScript)
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks
- **Components**: Modular UI components

### Database Schema
- **Colleges**: Multi-tenant support
- **Users**: Students, teachers, admins
- **Events**: Comprehensive event management
- **Registrations**: Student event participation
- **Attendance**: Event attendance tracking
- **Feedback**: Event feedback system

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database
The SQLite database is included with sample data and can be found in the `database/` directory.

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── routers/            # API route handlers
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   └── main.py             # Application entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
├── database/               # SQLite database files
└── README.md              # This file
```

## 🔧 Features

### For Students
- Event browsing and registration
- Personal dashboard
- Attendance tracking
- Feedback submission

### For Teachers
- Event creation and management
- Student registration management
- Attendance tracking
- Analytics and reports

### For Administrators
- Multi-college management
- User management
- System analytics
- Data export capabilities

## 📊 Database Features

- **Multi-tenant architecture** for multiple colleges
- **Comprehensive constraints** for data integrity
- **Automated triggers** for data validation
- **Scalable design** for large institutions

## 🛠️ Development Notes

The project follows modern development practices:
- Clean code architecture
- Comprehensive error handling
- Database optimization
- API documentation
- Modular frontend components

## 📝 Next Steps

1. Complete frontend UI implementation
2. Add responsive design
3. Implement advanced analytics
4. Add mobile app support
5. Deploy to production

## 🤝 Contributing

This project is currently in active development. The database and backend are production-ready, with the frontend UI being the primary focus for completion.

---

**Repository**: [https://github.com/SpMonish84/Campus_Event_Management](https://github.com/SpMonish84/Campus_Event_Management)
