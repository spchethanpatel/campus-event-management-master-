import React, { useState, useEffect } from 'react';
import { Calendar, Users, Building2, UserCheck, TrendingUp, Activity } from 'lucide-react';
import Card from '../components/UI/Card';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { apiService } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await apiService.getStats();
        setStats(response.data);
      } catch (err) {
        setError('Failed to fetch statistics');
        console.error('Error fetching stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    {
      title: 'Total Events',
      value: stats?.events || 0,
      icon: Calendar,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Total Students',
      value: stats?.students || 0,
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Colleges',
      value: stats?.colleges || 0,
      icon: Building2,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Registrations',
      value: stats?.registrations || 0,
      icon: UserCheck,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ];

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
          <Activity className="h-12 w-12 mx-auto mb-2" />
          <p className="text-lg font-medium">{error}</p>
        </div>
        <p className="text-gray-600">Please check your backend connection and try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to EventHub - Your Event Management System</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <Card>
        <Card.Header>
          <Card.Title>Quick Actions</Card.Title>
        </Card.Header>
        <Card.Content>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200">
              <Calendar className="h-8 w-8 text-primary-600 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Create Event</h3>
              <p className="text-sm text-gray-600">Add a new event to the system</p>
            </div>
            <div className="text-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200">
              <Users className="h-8 w-8 text-primary-600 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Add Student</h3>
              <p className="text-sm text-gray-600">Register a new student</p>
            </div>
            <div className="text-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200">
              <Building2 className="h-8 w-8 text-primary-600 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Add College</h3>
              <p className="text-sm text-gray-600">Register a new college</p>
            </div>
          </div>
        </Card.Content>
      </Card>

      {/* Recent Activity */}
      <Card>
        <Card.Header>
          <Card.Title>System Status</Card.Title>
        </Card.Header>
        <Card.Content>
          <div className="flex items-center space-x-2">
            <div className="h-3 w-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">All systems operational</span>
          </div>
          <div className="mt-4 text-sm text-gray-600">
            <p>• Database connection: Active</p>
            <p>• API endpoints: Responding</p>
            <p>• Last updated: {new Date().toLocaleString()}</p>
          </div>
        </Card.Content>
      </Card>
    </div>
  );
};

export default Dashboard;
