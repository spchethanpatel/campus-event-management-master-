import React, { useState, useEffect } from 'react';
import { Calendar, Users, MapPin, Clock, Plus, Eye, UserCheck, GraduationCap, Building2, Mail, Phone, BookOpen, Award } from 'lucide-react';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { apiService } from '../services/api';

const StudentDashboard = () => {
  const [activeTab, setActiveTab] = useState('events');
  const [events, setEvents] = useState([]);
  const [registrations, setRegistrations] = useState([]);
  const [studentInfo, setStudentInfo] = useState({
    student_id: 1,
    name: 'John Doe',
    email: 'john.doe@university.edu',
    college_id: 1,
    college_name: 'University of Technology',
    department: 'Computer Science',
    year: 'Senior',
    status: 'active'
  });
  const [loading, setLoading] = useState(true);
  const [showRegistrationForm, setShowRegistrationForm] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [eventsRes, registrationsRes] = await Promise.all([
        apiService.getEvents(),
        apiService.getRegistrations()
      ]);
      setEvents(eventsRes.data);
      setRegistrations(registrationsRes.data.filter(reg => reg.student_id === studentInfo.student_id));
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterForEvent = (event) => {
    setSelectedEvent(event);
    setShowRegistrationForm(true);
  };

  const handleRegistrationSubmit = async (e) => {
    e.preventDefault();
    try {
      await apiService.createRegistration({
        student_id: studentInfo.student_id,
        event_id: selectedEvent.event_id
      });
      setShowRegistrationForm(false);
      setSelectedEvent(null);
      fetchData(); // Refresh data
      alert('Successfully registered for the event!');
    } catch (error) {
      console.error('Registration failed:', error);
      alert('Registration failed. Please try again.');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const tabs = [
    { id: 'events', name: 'Available Events', icon: Calendar },
    { id: 'registrations', name: 'My Registrations', icon: UserCheck },
    { id: 'profile', name: 'Profile', icon: GraduationCap }
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                <GraduationCap className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Student Portal</h1>
                <p className="text-gray-600">Welcome back, {studentInfo.name}</p>
              </div>
            </div>
            <div className="mt-4 sm:mt-0">
              <Button onClick={() => setActiveTab('profile')}>
                <GraduationCap className="h-4 w-4 mr-2" />
                View Profile
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Student Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Building2 className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">College</p>
                <p className="text-lg font-semibold text-gray-900">{studentInfo.college_name}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <BookOpen className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Department</p>
                <p className="text-lg font-semibold text-gray-900">{studentInfo.department}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Award className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Year</p>
                <p className="text-lg font-semibold text-gray-900">{studentInfo.year}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <UserCheck className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Registrations</p>
                <p className="text-lg font-semibold text-gray-900">{registrations.length}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                      activeTab === tab.id
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.name}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'events' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Available Events</h2>
              <p className="text-sm text-gray-600">{events.length} events available</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {events.map((event) => (
                <Card key={event.event_id} className="hover:shadow-lg transition-shadow duration-200">
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">{event.title}</h3>
                        <p className="text-sm text-primary-600 font-medium">{event.event_type_name}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        event.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {event.status}
                      </span>
                    </div>

                    <div className="space-y-2 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="h-4 w-4 mr-2" />
                        <span>{formatDate(event.start_time)}</span>
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Clock className="h-4 w-4 mr-2" />
                        <span>{formatTime(event.start_time)} - {formatTime(event.end_time)}</span>
                      </div>
                      {event.venue && (
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin className="h-4 w-4 mr-2" />
                          <span>{event.venue}</span>
                        </div>
                      )}
                      <div className="flex items-center text-sm text-gray-600">
                        <Users className="h-4 w-4 mr-2" />
                        <span>Capacity: {event.capacity}</span>
                      </div>
                    </div>

                    {event.description && (
                      <p className="text-sm text-gray-600 mb-4 line-clamp-3">{event.description}</p>
                    )}

                    <Button 
                      className="w-full"
                      onClick={() => handleRegisterForEvent(event)}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Register for Event
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'registrations' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">My Registrations</h2>
              <p className="text-sm text-gray-600">{registrations.length} registrations</p>
            </div>

            <Card>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Event
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {registrations.map((registration) => {
                      const event = events.find(e => e.event_id === registration.event_id);
                      return (
                        <tr key={registration.registration_id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{event?.title}</div>
                              <div className="text-sm text-gray-500">{event?.event_type_name}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {event ? formatDate(event.start_time) : 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {event ? `${formatTime(event.start_time)} - ${formatTime(event.end_time)}` : 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              registration.status === 'registered' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {registration.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <Button variant="outline" size="sm">
                              <Eye className="h-4 w-4 mr-1" />
                              View
                            </Button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'profile' && (
          <Card>
            <Card.Header>
              <Card.Title>Student Profile</Card.Title>
            </Card.Header>
            <Card.Content>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="label">Student ID</label>
                    <p className="text-sm text-gray-900">{studentInfo.student_id}</p>
                  </div>
                  <div>
                    <label className="label">Full Name</label>
                    <p className="text-sm text-gray-900">{studentInfo.name}</p>
                  </div>
                  <div>
                    <label className="label">Email</label>
                    <p className="text-sm text-gray-900">{studentInfo.email}</p>
                  </div>
                  <div>
                    <label className="label">College ID</label>
                    <p className="text-sm text-gray-900">{studentInfo.college_id}</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="label">College</label>
                    <p className="text-sm text-gray-900">{studentInfo.college_name}</p>
                  </div>
                  <div>
                    <label className="label">Department</label>
                    <p className="text-sm text-gray-900">{studentInfo.department}</p>
                  </div>
                  <div>
                    <label className="label">Academic Year</label>
                    <p className="text-sm text-gray-900">{studentInfo.year}</p>
                  </div>
                  <div>
                    <label className="label">Status</label>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      studentInfo.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {studentInfo.status}
                    </span>
                  </div>
                </div>
              </div>
            </Card.Content>
          </Card>
        )}
      </div>

      {/* Registration Modal */}
      {showRegistrationForm && selectedEvent && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Register for Event</h3>
              <form onSubmit={handleRegistrationSubmit}>
                <div className="mb-4">
                  <h4 className="font-medium text-gray-900">{selectedEvent.title}</h4>
                  <p className="text-sm text-gray-600">{selectedEvent.event_type_name}</p>
                  <p className="text-sm text-gray-600">{formatDate(selectedEvent.start_time)}</p>
                </div>
                
                <div className="flex justify-end space-x-3">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => setShowRegistrationForm(false)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit">
                    Confirm Registration
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;
