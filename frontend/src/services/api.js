import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('Network Error: Backend server is not running');
      throw new Error('Unable to connect to server. Please make sure the backend is running on http://localhost:8001');
    }
    
    return Promise.reject(error);
  }
);

// API endpoints
export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),
  
  // Statistics
  getStats: () => api.get('/stats'),
  
  // Colleges
  getColleges: () => api.get('/api/v1/colleges'),
  getCollege: (id) => api.get(`/api/v1/colleges/${id}`),
  createCollege: (data) => api.post('/api/v1/colleges', data),
  updateCollege: (id, data) => api.put(`/api/v1/colleges/${id}`, data),
  deleteCollege: (id) => api.delete(`/api/v1/colleges/${id}`),
  
  // Students
  getStudents: () => api.get('/api/v1/students'),
  getStudent: (id) => api.get(`/api/v1/students/${id}`),
  createStudent: (data) => api.post('/api/v1/students', data),
  updateStudent: (id, data) => api.put(`/api/v1/students/${id}`, data),
  deleteStudent: (id) => api.delete(`/api/v1/students/${id}`),
  
  // Events
  getEvents: () => api.get('/api/v1/events'),
  getEvent: (id) => api.get(`/api/v1/events/${id}`),
  createEvent: (data) => api.post('/api/v1/events', data),
  updateEvent: (id, data) => api.put(`/api/v1/events/${id}`, data),
  deleteEvent: (id) => api.delete(`/api/v1/events/${id}`),
  
  // Event Types
  getEventTypes: () => api.get('/api/v1/event-types'),
  getEventType: (id) => api.get(`/api/v1/event-types/${id}`),
  createEventType: (data) => api.post('/api/v1/event-types', data),
  updateEventType: (id, data) => api.put(`/api/v1/event-types/${id}`, data),
  deleteEventType: (id) => api.delete(`/api/v1/event-types/${id}`),
  
  // Registrations
  getRegistrations: () => api.get('/api/v1/registrations'),
  getRegistration: (id) => api.get(`/api/v1/registrations/${id}`),
  createRegistration: (data) => api.post('/api/v1/registrations', data),
  updateRegistration: (id, data) => api.put(`/api/v1/registrations/${id}`, data),
  deleteRegistration: (id) => api.delete(`/api/v1/registrations/${id}`),
  
  // Attendance
  getAttendance: () => api.get('/api/v1/attendance'),
  getAttendanceByEvent: (eventId) => api.get(`/api/v1/attendance/event/${eventId}`),
  markAttendance: (data) => api.post('/api/v1/attendance', data),
  updateAttendance: (id, data) => api.put(`/api/v1/attendance/${id}`, data),
  
  // Feedback
  getFeedback: () => api.get('/api/v1/feedback'),
  getFeedbackByEvent: (eventId) => api.get(`/api/v1/feedback/event/${eventId}`),
  createFeedback: (data) => api.post('/api/v1/feedback', data),
  updateFeedback: (id, data) => api.put(`/api/v1/feedback/${id}`, data),
  deleteFeedback: (id) => api.delete(`/api/v1/feedback/${id}`),
  
  // Admins
  getAdmins: () => api.get('/api/v1/admins'),
  getAdmin: (id) => api.get(`/api/v1/admins/${id}`),
  createAdmin: (data) => api.post('/api/v1/admins', data),
  updateAdmin: (id, data) => api.put(`/api/v1/admins/${id}`, data),
  deleteAdmin: (id) => api.delete(`/api/v1/admins/${id}`),
};

export default api;
