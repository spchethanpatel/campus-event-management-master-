import React, { useState, useEffect } from 'react';
import { Building2, MapPin, Phone, Mail, Plus, Eye, Edit, Trash2, Search } from 'lucide-react';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { apiService } from '../services/api';

const Colleges = () => {
  const [colleges, setColleges] = useState([]);
  const [filteredColleges, setFilteredColleges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchColleges();
  }, []);

  useEffect(() => {
    const filtered = colleges.filter(college =>
      college.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      college.location?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      college.contact_email?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredColleges(filtered);
  }, [colleges, searchTerm]);

  const fetchColleges = async () => {
    try {
      setLoading(true);
      const response = await apiService.getColleges();
      setColleges(response.data);
    } catch (err) {
      setError('Failed to fetch colleges');
      console.error('Error fetching colleges:', err);
    } finally {
      setLoading(false);
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
          <Building2 className="h-12 w-12 mx-auto mb-2" />
          <p className="text-lg font-medium">{error}</p>
        </div>
        <Button onClick={fetchColleges}>Try Again</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Colleges</h1>
          <p className="text-gray-600 mt-2">Manage college registrations</p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Add College</span>
        </Button>
      </div>

      {/* Search Bar */}
      <Card>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search colleges by name, location, or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </Card>

      {/* Colleges List */}
      {filteredColleges.length === 0 ? (
        <Card className="text-center py-12">
          <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchTerm ? 'No colleges found' : 'No colleges registered'}
          </h3>
          <p className="text-gray-600 mb-4">
            {searchTerm ? 'Try adjusting your search terms.' : 'Get started by adding your first college.'}
          </p>
          {!searchTerm && <Button>Add College</Button>}
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredColleges.map((college) => (
            <Card key={college.college_id} className="hover:shadow-md transition-shadow duration-200">
              <div className="space-y-4">
                {/* College Header */}
                <div className="flex items-center space-x-3">
                  <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                    <Building2 className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {college.name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      ID: {college.college_id}
                    </p>
                  </div>
                </div>

                {/* College Details */}
                <div className="space-y-2">
                  {college.location && (
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="h-4 w-4 mr-2" />
                      <span className="truncate">{college.location}</span>
                    </div>
                  )}
                  
                  {college.contact_phone && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Phone className="h-4 w-4 mr-2" />
                      <span>{college.contact_phone}</span>
                    </div>
                  )}
                  
                  {college.contact_email && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Mail className="h-4 w-4 mr-2" />
                      <span className="truncate">{college.contact_email}</span>
                    </div>
                  )}
                </div>

                {/* College Info */}
                <div className="text-sm text-gray-600">
                  <p><span className="font-medium">Type:</span> {college.type || 'Not specified'}</p>
                  <p><span className="font-medium">Established:</span> {college.established_year || 'Not specified'}</p>
                </div>

                {/* Description */}
                {college.description && (
                  <p className="text-sm text-gray-600 line-clamp-3">
                    {college.description}
                  </p>
                )}

                {/* Actions */}
                <div className="flex space-x-2 pt-4 border-t border-gray-200">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button variant="danger" size="sm">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Results Summary */}
      {searchTerm && (
        <div className="text-center text-sm text-gray-600">
          Showing {filteredColleges.length} of {colleges.length} colleges
        </div>
      )}
    </div>
  );
};

export default Colleges;
