import React, { useState, useEffect } from 'react';
import { UserCheck, Calendar, Users, Building2, Plus, Eye, Edit, Trash2, Search } from 'lucide-react';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { apiService } from '../services/api';

const Registrations = () => {
  const [registrations, setRegistrations] = useState([]);
  const [filteredRegistrations, setFilteredRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchRegistrations();
  }, []);

  useEffect(() => {
    const filtered = registrations.filter(registration =>
      registration.student_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      registration.event_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      registration.status?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredRegistrations(filtered);
  }, [registrations, searchTerm]);

  const fetchRegistrations = async () => {
    try {
      setLoading(true);
      const response = await apiService.getRegistrations();
      setRegistrations(response.data);
    } catch (err) {
      setError('Failed to fetch registrations');
      console.error('Error fetching registrations:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
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
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <UserCheck className="h-12 w-12 mx-auto mb-2" />
          <p className="text-lg font-medium">{error}</p>
        </div>
        <Button onClick={fetchRegistrations}>Try Again</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Registrations</h1>
          <p className="text-gray-600 mt-2">Manage event registrations</p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>New Registration</span>
        </Button>
      </div>

      {/* Search Bar */}
      <Card>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search registrations by student, event, or status..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </Card>

      {/* Registrations List */}
      {filteredRegistrations.length === 0 ? (
        <Card className="text-center py-12">
          <UserCheck className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchTerm ? 'No registrations found' : 'No registrations yet'}
          </h3>
          <p className="text-gray-600 mb-4">
            {searchTerm ? 'Try adjusting your search terms.' : 'Get started by creating your first registration.'}
          </p>
          {!searchTerm && <Button>New Registration</Button>}
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredRegistrations.map((registration) => (
            <Card key={registration.registration_id} className="hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <UserCheck className="h-6 w-6 text-primary-600" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {registration.student_name || 'Unknown Student'}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Registration ID: {registration.registration_id}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          {formatDate(registration.registration_date)}
                        </span>
                      </div>
                    </div>
                    
                    <div className="mt-2 flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <Users className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          {registration.event_title || 'Unknown Event'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(registration.status)}`}>
                    {registration.status || 'Unknown'}
                  </span>
                  
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="danger" size="sm">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Results Summary */}
      {searchTerm && (
        <div className="text-center text-sm text-gray-600">
          Showing {filteredRegistrations.length} of {registrations.length} registrations
        </div>
      )}
    </div>
  );
};

export default Registrations;
