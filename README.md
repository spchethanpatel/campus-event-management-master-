Campus Event Management System

Hey! This is my project for managing campus events. I built it mainly for colleges to manage events, registrations, and keep track of everything in one place.

✅ What’s Done So Far

Database: I created a SQLite database with all the tables we need.

Backend API: Built using FastAPI for handling requests.

Authentication: Students and teachers can log in securely.

Core Features: Event management, registration, and attendance tracking.

Multi-College Support: Can handle multiple colleges in the same system 


🏗️ How It’s Built
Backend

Language/Framework: Python + FastAPI

Database: SQLite

Authentication: JWT-based

Features: Event management, registration, attendance, feedback, and reporting

Frontend

Framework: React + TypeScript

Styling: Tailwind CSS

State Management: React hooks

Components: Modular, reusable components

Database Structure

Colleges: Multi-tenant support

Users: Students, teachers, admins

Events: All event info

Registrations: Student participation

Attendance: Track who attended

Feedback: Collect student feedback

🚀 Quick Start
Backend
cd backend
pip install -r requirements.txt
python main.py

Frontend
cd frontend
npm install
npm run dev

Database

The SQLite database is already included with some sample data. You’ll find it in the database/ folder.

📁 Project Structure
├── backend/                 # FastAPI backend
│   ├── routers/            # API routes
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   └── main.py             # Entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Pages
│   │   └── services/       # API services
├── database/               # SQLite database
└── README.md               # This file

👨‍🎓 Features
For Students

Browse events and register

See personal dashboard

Track attendance

Give feedback

For Teachers

Create/manage events

Manage student registrations

Track attendance

View analytics and reports

For Admins

Manage multiple colleges

Manage users

Check system stats

Export data

🛠️ Notes from Me

Tried to follow clean code practices

Added error handling where possible

Made database optimized for queries

Frontend is modular, so adding new pages is easy

Backend has API docs at /docs
