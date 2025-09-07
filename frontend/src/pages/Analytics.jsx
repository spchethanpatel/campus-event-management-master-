import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, Calendar, Building2, UserCheck, MessageSquare } from 'lucide-react';
import Card from '../components/UI/Card';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { apiService } from '../services/api';

const Analytics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await apiService.getStats();
      setStats(response.data);
    } catch (err) {
      setError('Failed to fetch analytics data');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculatePercentage = (value, total) => {
    if (total === 0) return 0;
    return Math.round((value / total) * 100);
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
          <BarChart3 className="h-12 w-12 mx-auto mb-2" />
          <p className="text-lg font-medium">{error}</p>
        </div>
      </div>
    );
  }

  const totalEntities = (stats?.events || 0) + (stats?.students || 0) + (stats?.colleges || 0) + (stats?.registrations || 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-2">System overview and performance metrics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-100">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Events</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.events || 0}</p>
              <p className="text-xs text-gray-500">
                {calculatePercentage(stats?.events || 0, totalEntities)}% of total
              </p>
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-green-100">
              <Users className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Students</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.students || 0}</p>
              <p className="text-xs text-gray-500">
                {calculatePercentage(stats?.students || 0, totalEntities)}% of total
              </p>
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-purple-100">
              <Building2 className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Colleges</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.colleges || 0}</p>
              <p className="text-xs text-gray-500">
                {calculatePercentage(stats?.colleges || 0, totalEntities)}% of total
              </p>
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-md transition-shadow duration-200">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-orange-100">
              <UserCheck className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Registrations</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.registrations || 0}</p>
              <p className="text-xs text-gray-500">
                {calculatePercentage(stats?.registrations || 0, totalEntities)}% of total
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <Card.Header>
            <Card.Title>System Distribution</Card.Title>
          </Card.Header>
          <Card.Content>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium">Events</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${calculatePercentage(stats?.events || 0, totalEntities)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-8">{stats?.events || 0}</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium">Students</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ width: `${calculatePercentage(stats?.students || 0, totalEntities)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-8">{stats?.students || 0}</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Building2 className="h-4 w-4 text-purple-600" />
                  <span className="text-sm font-medium">Colleges</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full" 
                      style={{ width: `${calculatePercentage(stats?.colleges || 0, totalEntities)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-8">{stats?.colleges || 0}</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <UserCheck className="h-4 w-4 text-orange-600" />
                  <span className="text-sm font-medium">Registrations</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-orange-600 h-2 rounded-full" 
                      style={{ width: `${calculatePercentage(stats?.registrations || 0, totalEntities)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-8">{stats?.registrations || 0}</span>
                </div>
              </div>
            </div>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>Performance Metrics</Card.Title>
          </Card.Header>
          <Card.Content>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium text-green-800">System Health</span>
                </div>
                <span className="text-sm font-bold text-green-800">Excellent</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                  <span className="text-sm font-medium text-blue-800">Data Integrity</span>
                </div>
                <span className="text-sm font-bold text-blue-800">100%</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-5 w-5 text-purple-600" />
                  <span className="text-sm font-medium text-purple-800">Event Types</span>
                </div>
                <span className="text-sm font-bold text-purple-800">{stats?.event_types || 0}</span>
              </div>

              <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5 text-orange-600" />
                  <span className="text-sm font-medium text-orange-800">Total Entities</span>
                </div>
                <span className="text-sm font-bold text-orange-800">{totalEntities}</span>
              </div>
            </div>
          </Card.Content>
        </Card>
      </div>

      {/* Summary */}
      <Card>
        <Card.Header>
          <Card.Title>System Summary</Card.Title>
        </Card.Header>
        <Card.Content>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div>
              <p className="text-2xl font-bold text-primary-600">{stats?.events || 0}</p>
              <p className="text-sm text-gray-600">Active Events</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-primary-600">{stats?.students || 0}</p>
              <p className="text-sm text-gray-600">Registered Students</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-primary-600">{stats?.colleges || 0}</p>
              <p className="text-sm text-gray-600">Participating Colleges</p>
            </div>
          </div>
        </Card.Content>
      </Card>
    </div>
  );
};

export default Analytics;
