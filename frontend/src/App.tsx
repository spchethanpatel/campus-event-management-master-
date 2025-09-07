import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Landing from './pages/Landing';
import StudentLogin from './pages/StudentLogin';
import TeacherLogin from './pages/TeacherLogin';
import StudentDashboard from './pages/StudentDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import EventsPage from './pages/EventsPage';
import Profile from './pages/Profile';
import Dashboard from './pages/Dashboard';
import Events from './pages/Events';
import Students from './pages/Students';
import Colleges from './pages/Colleges';
import Registrations from './pages/Registrations';
import Feedback from './pages/Feedback';
import Analytics from './pages/Analytics';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/student-login" element={<StudentLogin />} />
        <Route path="/teacher-login" element={<TeacherLogin />} />
        <Route path="/events" element={<EventsPage />} />
        
        {/* Dashboard Routes */}
        <Route path="/student-dashboard" element={<StudentDashboard />} />
        <Route path="/teacher-dashboard" element={<TeacherDashboard />} />
        
        {/* Protected Routes with Layout */}
        <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
        <Route path="/profile" element={<Layout><Profile /></Layout>} />
        <Route path="/admin-events" element={<Layout><Events /></Layout>} />
        <Route path="/students" element={<Layout><Students /></Layout>} />
        <Route path="/colleges" element={<Layout><Colleges /></Layout>} />
        <Route path="/registrations" element={<Layout><Registrations /></Layout>} />
        <Route path="/feedback" element={<Layout><Feedback /></Layout>} />
        <Route path="/analytics" element={<Layout><Analytics /></Layout>} />
      </Routes>
    </Router>
  );
}

export default App;
