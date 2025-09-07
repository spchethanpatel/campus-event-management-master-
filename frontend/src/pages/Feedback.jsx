import React, { useState, useEffect } from 'react';
import { MessageSquare, Star, Calendar, Users, Plus, Eye, Edit, Trash2, Search } from 'lucide-react';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { apiService } from '../services/api';

const Feedback = () => {
  const [feedback, setFeedback] = useState([]);
  const [filteredFeedback, setFilteredFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchFeedback();
  }, []);

  useEffect(() => {
    const filtered = feedback.filter(item =>
      item.student_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.event_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.comment?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredFeedback(filtered);
  }, [feedback, searchTerm]);

  const fetchFeedback = async () => {
    try {
      setLoading(true);
      const response = await apiService.getFeedback();
      setFeedback(response.data);
    } catch (err) {
      setError('Failed to fetch feedback');
      console.error('Error fetching feedback:', err);
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

  const renderStars = (rating) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <Star
          key={i}
          className={`h-4 w-4 ${
            i <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
          }`}
        />
      );
    }
    return stars;
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
          <MessageSquare className="h-12 w-12 mx-auto mb-2" />
          <p className="text-lg font-medium">{error}</p>
        </div>
        <Button onClick={fetchFeedback}>Try Again</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Feedback</h1>
          <p className="text-gray-600 mt-2">View and manage event feedback</p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Add Feedback</span>
        </Button>
      </div>

      {/* Search Bar */}
      <Card>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search feedback by student, event, or comment..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </Card>

      {/* Feedback List */}
      {filteredFeedback.length === 0 ? (
        <Card className="text-center py-12">
          <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchTerm ? 'No feedback found' : 'No feedback yet'}
          </h3>
          <p className="text-gray-600 mb-4">
            {searchTerm ? 'Try adjusting your search terms.' : 'Feedback will appear here once students start submitting it.'}
          </p>
          {!searchTerm && <Button>Add Feedback</Button>}
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredFeedback.map((item) => (
            <Card key={item.feedback_id} className="hover:shadow-md transition-shadow duration-200">
              <div className="space-y-4">
                {/* Feedback Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center">
                      <MessageSquare className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {item.student_name || 'Anonymous'}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {item.event_title || 'Unknown Event'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">
                      {formatDate(item.feedback_date)}
                    </span>
                    <div className="flex space-x-1">
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

                {/* Rating */}
                {item.rating && (
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-700">Rating:</span>
                    <div className="flex space-x-1">
                      {renderStars(item.rating)}
                    </div>
                    <span className="text-sm text-gray-600">({item.rating}/5)</span>
                  </div>
                )}

                {/* Comment */}
                {item.comment && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-700">{item.comment}</p>
                  </div>
                )}

                {/* Additional Info */}
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>Feedback ID: {item.feedback_id}</span>
                  </div>
                  {item.event_id && (
                    <div className="flex items-center space-x-1">
                      <Users className="h-4 w-4" />
                      <span>Event ID: {item.event_id}</span>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Results Summary */}
      {searchTerm && (
        <div className="text-center text-sm text-gray-600">
          Showing {filteredFeedback.length} of {feedback.length} feedback entries
        </div>
      )}
    </div>
  );
};

export default Feedback;
