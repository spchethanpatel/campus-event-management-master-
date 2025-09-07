import React, { useState, useEffect } from 'react';
import { Calendar, MapPin, Clock, Users, Eye, UserCheck, X, Plus, Filter, Search } from 'lucide-react';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { apiService } from '../services/api';

const EventsPage = () => {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showEventDialog, setShowEventDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [eventTypes, setEventTypes] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    filterEvents();
  }, [events, searchTerm, filterType]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // First check if backend is running
      try {
        await apiService.healthCheck();
      } catch (healthError) {
        throw new Error('Backend server is not running. Please start the backend server on http://localhost:8000');
      }
      
      const [eventsRes, eventTypesRes] = await Promise.all([
        apiService.getEvents(),
        apiService.getEventTypes()
      ]);
      setEvents(eventsRes.data);
      setEventTypes(eventTypesRes.data);
    } catch (err) {
      const errorMessage = err.message || 'Failed to fetch events';
      setError(errorMessage);
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterEvents = () => {
    let filtered = events;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(event =>
        event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.event_type_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.venue?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by event type
    if (filterType !== 'all') {
      filtered = filtered.filter(event => event.type_id.toString() === filterType);
    }

    setFilteredEvents(filtered);
  };

  const handleEventClick = (event) => {
    setSelectedEvent(event);
    setShowEventDialog(true);
  };

  const handleRegisterForEvent = async (event) => {
    try {
      // For demo purposes, using a mock student ID
      const registrationData = {
        student_id: 1, // This should come from user authentication
        event_id: event.event_id
      };
      
      await apiService.createRegistration(registrationData);
      alert('Successfully registered for the event!');
      setShowEventDialog(false);
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

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return {
      date: date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }),
      time: date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    };
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Events</h1>
                <p className="text-gray-600 mt-2">Discover and register for exciting events</p>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Card className="text-center py-12">
            <div className="text-red-600 mb-4">
              <Calendar className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Connection Error</h3>
              <p className="text-gray-600 mb-4">{error}</p>
            </div>
            <div className="space-y-4">
              <Button onClick={fetchData} className="mr-4">
                Try Again
              </Button>
              <Button variant="outline" onClick={() => window.location.href = '/'}>
                Back to Home
              </Button>
            </div>
            <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h4 className="font-medium text-yellow-800 mb-2">Troubleshooting Steps:</h4>
              <ul className="text-sm text-yellow-700 text-left space-y-1">
                <li>1. Make sure the backend server is running on http://localhost:8000</li>
                <li>2. Check if the database file exists in the database folder</li>
                <li>3. Verify that all required Python packages are installed</li>
                <li>4. Check the browser console for more detailed error information</li>
              </ul>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Events</h1>
              <p className="text-gray-600 mt-2">Discover and register for exciting events</p>
            </div>
            <div className="mt-4 sm:mt-0">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Event
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filter */}
        <Card className="p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search events by title, description, or venue..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="md:w-48">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="all">All Event Types</option>
                {eventTypes.map((type) => (
                  <option key={type.type_id} value={type.type_id.toString()}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </Card>

        {/* Events Grid */}
        <div className="mb-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              {filteredEvents.length} Events Found
            </h2>
            <p className="text-sm text-gray-600">
              {searchTerm || filterType !== 'all' ? 'Filtered results' : 'All events'}
            </p>
          </div>
        </div>

        {filteredEvents.length === 0 ? (
          <Card className="text-center py-12">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No events found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || filterType !== 'all' 
                ? 'Try adjusting your search or filter criteria.' 
                : 'No events are currently available.'}
            </p>
            {(searchTerm || filterType !== 'all') && (
              <Button onClick={() => {
                setSearchTerm('');
                setFilterType('all');
              }}>
                Clear Filters
              </Button>
            )}
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredEvents.map((event) => {
              const { date, time } = formatDateTime(event.start_time);
              const endTime = formatTime(event.end_time);
              
              return (
                <Card 
                  key={event.event_id} 
                  className="hover:shadow-lg transition-all duration-200 cursor-pointer group"
                  onClick={() => handleEventClick(event)}
                >
                  <div className="p-6">
                    {/* Event Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2">
                          {event.title}
                        </h3>
                        <p className="text-sm text-primary-600 font-medium mt-1">
                          {event.event_type_name}
                        </p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        event.status === 'active' ? 'bg-green-100 text-green-800' : 
                        event.status === 'completed' ? 'bg-blue-100 text-blue-800' : 
                        'bg-red-100 text-red-800'
                      }`}>
                        {event.status}
                      </span>
                    </div>

                    {/* Event Details */}
                    <div className="space-y-3 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="h-4 w-4 mr-2 flex-shrink-0" />
                        <span>{date}</span>
                      </div>
                      
                      <div className="flex items-center text-sm text-gray-600">
                        <Clock className="h-4 w-4 mr-2 flex-shrink-0" />
                        <span>{time} - {endTime}</span>
                      </div>
                      
                      {event.venue && (
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin className="h-4 w-4 mr-2 flex-shrink-0" />
                          <span className="line-clamp-1">{event.venue}</span>
                        </div>
                      )}
                      
                      <div className="flex items-center text-sm text-gray-600">
                        <Users className="h-4 w-4 mr-2 flex-shrink-0" />
                        <span>Capacity: {event.capacity}</span>
                      </div>
                    </div>

                    {/* Event Description */}
                    {event.description && (
                      <p className="text-sm text-gray-600 line-clamp-3 mb-4">
                        {event.description}
                      </p>
                    )}

                    {/* Action Button */}
                    <Button 
                      className="w-full group-hover:bg-primary-700 transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEventClick(event);
                      }}
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      View Details
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Event Detail Dialog */}
      {showEventDialog && selectedEvent && (
        <EventDetailDialog
          event={selectedEvent}
          onClose={() => setShowEventDialog(false)}
          onRegister={() => handleRegisterForEvent(selectedEvent)}
        />
      )}
    </div>
  );
};

// Event Detail Dialog Component
const EventDetailDialog = ({ event, onClose, onRegister }) => {
  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return {
      date: date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      }),
      time: date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    };
  };

  const formatEndTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const { date, time } = formatDateTime(event.start_time);
  const endTime = formatEndTime(event.end_time);

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-4 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white mb-4">
        {/* Dialog Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
              <Calendar className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Event Details</h2>
              <p className="text-sm text-gray-600">Complete event information</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Event Content */}
        <div className="space-y-6">
          {/* Event Title and Type */}
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">{event.title}</h3>
            <div className="flex items-center space-x-4">
              <span className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium">
                {event.event_type_name}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                event.status === 'active' ? 'bg-green-100 text-green-800' : 
                event.status === 'completed' ? 'bg-blue-100 text-blue-800' : 
                'bg-red-100 text-red-800'
              }`}>
                {event.status}
              </span>
            </div>
          </div>

          {/* Event Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <Calendar className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Date</p>
                  <p className="text-sm text-gray-600">{date}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Clock className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Time</p>
                  <p className="text-sm text-gray-600">{time} - {endTime}</p>
                </div>
              </div>

              {event.venue && (
                <div className="flex items-center space-x-3">
                  <MapPin className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Venue</p>
                    <p className="text-sm text-gray-600">{event.venue}</p>
                  </div>
                </div>
              )}

              <div className="flex items-center space-x-3">
                <Users className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Capacity</p>
                  <p className="text-sm text-gray-600">{event.capacity} participants</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-900 mb-2">College</p>
                <p className="text-sm text-gray-600">{event.college_name}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-900 mb-2">Event ID</p>
                <p className="text-sm text-gray-600">#{event.event_id}</p>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-900 mb-2">Semester</p>
                <p className="text-sm text-gray-600">{event.semester || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Event Description */}
          {event.description && (
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Description</h4>
              <p className="text-gray-700 leading-relaxed">{event.description}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-6 border-t border-gray-200">
            <Button 
              className="flex-1"
              onClick={onRegister}
              disabled={event.status !== 'active'}
            >
              <UserCheck className="h-4 w-4 mr-2" />
              {event.status === 'active' ? 'Register for Event' : 'Registration Closed'}
            </Button>
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={onClose}
            >
              Close
            </Button>
          </div>

          {event.status !== 'active' && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> Registration is not available for {event.status} events.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EventsPage;
