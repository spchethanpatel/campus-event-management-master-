import React, { useState } from 'react';
import { User, Mail, Phone, MapPin, Calendar, GraduationCap, Settings, Save, Camera, Bell, Shield, Globe } from 'lucide-react';
import Button from '../components/UI/Button';
import Card from '../components/UI/Card';

const Profile = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [profileData, setProfileData] = useState({
    name: 'John Doe',
    email: 'john.doe@university.edu',
    phone: '+1 (555) 123-4567',
    department: 'Computer Science',
    year: 'Senior',
    college: 'University of Technology',
    location: 'New York, NY',
    bio: 'Passionate computer science student with interests in web development and machine learning.',
    avatar: null
  });

  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: true,
      sms: false
    },
    privacy: {
      profilePublic: true,
      showEmail: false,
      showPhone: false
    },
    preferences: {
      theme: 'light',
      language: 'en',
      timezone: 'EST'
    }
  });

  const handleProfileChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    });
  };

  const handleSettingsChange = (category, key, value) => {
    setSettings({
      ...settings,
      [category]: {
        ...settings[category],
        [key]: value
      }
    });
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'settings', name: 'Settings', icon: Settings },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'privacy', name: 'Privacy', icon: Shield }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Profile & Settings</h1>
          <p className="text-gray-600 mt-2">Manage your account information and preferences</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Card className="p-6">
              <nav className="space-y-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                        activeTab === tab.id
                          ? 'bg-primary-100 text-primary-700'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="font-medium">{tab.name}</span>
                    </button>
                  );
                })}
              </nav>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {activeTab === 'profile' && (
              <Card>
                <Card.Header>
                  <Card.Title>Profile Information</Card.Title>
                </Card.Header>
                <Card.Content>
                  <div className="space-y-6">
                    {/* Avatar Section */}
                    <div className="flex items-center space-x-6">
                      <div className="relative">
                        <div className="h-24 w-24 bg-primary-100 rounded-full flex items-center justify-center">
                          <User className="h-12 w-12 text-primary-600" />
                        </div>
                        <button className="absolute bottom-0 right-0 h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center text-white hover:bg-primary-700 transition-colors">
                          <Camera className="h-4 w-4" />
                        </button>
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{profileData.name}</h3>
                        <p className="text-gray-600">{profileData.email}</p>
                        <Button variant="outline" size="sm" className="mt-2">
                          Change Photo
                        </Button>
                      </div>
                    </div>

                    {/* Form Fields */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="label">Full Name</label>
                        <input
                          type="text"
                          name="name"
                          value={profileData.name}
                          onChange={handleProfileChange}
                          className="input-field"
                        />
                      </div>

                      <div>
                        <label className="label">Email Address</label>
                        <input
                          type="email"
                          name="email"
                          value={profileData.email}
                          onChange={handleProfileChange}
                          className="input-field"
                        />
                      </div>

                      <div>
                        <label className="label">Phone Number</label>
                        <input
                          type="tel"
                          name="phone"
                          value={profileData.phone}
                          onChange={handleProfileChange}
                          className="input-field"
                        />
                      </div>

                      <div>
                        <label className="label">Department</label>
                        <input
                          type="text"
                          name="department"
                          value={profileData.department}
                          onChange={handleProfileChange}
                          className="input-field"
                        />
                      </div>

                      <div>
                        <label className="label">Academic Year</label>
                        <select
                          name="year"
                          value={profileData.year}
                          onChange={handleProfileChange}
                          className="input-field"
                        >
                          <option value="Freshman">Freshman</option>
                          <option value="Sophomore">Sophomore</option>
                          <option value="Junior">Junior</option>
                          <option value="Senior">Senior</option>
                          <option value="Graduate">Graduate</option>
                        </select>
                      </div>

                      <div>
                        <label className="label">College</label>
                        <input
                          type="text"
                          name="college"
                          value={profileData.college}
                          onChange={handleProfileChange}
                          className="input-field"
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label className="label">Location</label>
                        <input
                          type="text"
                          name="location"
                          value={profileData.location}
                          onChange={handleProfileChange}
                          className="input-field"
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label className="label">Bio</label>
                        <textarea
                          name="bio"
                          rows={4}
                          value={profileData.bio}
                          onChange={handleProfileChange}
                          className="input-field"
                          placeholder="Tell us about yourself..."
                        />
                      </div>
                    </div>

                    <div className="flex justify-end">
                      <Button>
                        <Save className="h-4 w-4 mr-2" />
                        Save Changes
                      </Button>
                    </div>
                  </div>
                </Card.Content>
              </Card>
            )}

            {activeTab === 'settings' && (
              <Card>
                <Card.Header>
                  <Card.Title>Account Settings</Card.Title>
                </Card.Header>
                <Card.Content>
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Preferences</h3>
                      <div className="space-y-4">
                        <div>
                          <label className="label">Theme</label>
                          <select
                            value={settings.preferences.theme}
                            onChange={(e) => handleSettingsChange('preferences', 'theme', e.target.value)}
                            className="input-field"
                          >
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="auto">Auto</option>
                          </select>
                        </div>

                        <div>
                          <label className="label">Language</label>
                          <select
                            value={settings.preferences.language}
                            onChange={(e) => handleSettingsChange('preferences', 'language', e.target.value)}
                            className="input-field"
                          >
                            <option value="en">English</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                            <option value="de">German</option>
                          </select>
                        </div>

                        <div>
                          <label className="label">Timezone</label>
                          <select
                            value={settings.preferences.timezone}
                            onChange={(e) => handleSettingsChange('preferences', 'timezone', e.target.value)}
                            className="input-field"
                          >
                            <option value="EST">Eastern Time</option>
                            <option value="CST">Central Time</option>
                            <option value="MST">Mountain Time</option>
                            <option value="PST">Pacific Time</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card.Content>
              </Card>
            )}

            {activeTab === 'notifications' && (
              <Card>
                <Card.Header>
                  <Card.Title>Notification Settings</Card.Title>
                </Card.Header>
                <Card.Content>
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Preferences</h3>
                      <div className="space-y-4">
                        {Object.entries(settings.notifications).map(([key, value]) => (
                          <div key={key} className="flex items-center justify-between">
                            <div>
                              <h4 className="text-sm font-medium text-gray-900 capitalize">
                                {key === 'email' ? 'Email Notifications' : 
                                 key === 'push' ? 'Push Notifications' : 
                                 'SMS Notifications'}
                              </h4>
                              <p className="text-sm text-gray-600">
                                {key === 'email' ? 'Receive notifications via email' : 
                                 key === 'push' ? 'Receive push notifications in browser' : 
                                 'Receive notifications via SMS'}
                              </p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={value}
                                onChange={(e) => handleSettingsChange('notifications', key, e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card.Content>
              </Card>
            )}

            {activeTab === 'privacy' && (
              <Card>
                <Card.Header>
                  <Card.Title>Privacy Settings</Card.Title>
                </Card.Header>
                <Card.Content>
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Visibility</h3>
                      <div className="space-y-4">
                        {Object.entries(settings.privacy).map(([key, value]) => (
                          <div key={key} className="flex items-center justify-between">
                            <div>
                              <h4 className="text-sm font-medium text-gray-900">
                                {key === 'profilePublic' ? 'Public Profile' : 
                                 key === 'showEmail' ? 'Show Email Address' : 
                                 'Show Phone Number'}
                              </h4>
                              <p className="text-sm text-gray-600">
                                {key === 'profilePublic' ? 'Allow others to view your profile' : 
                                 key === 'showEmail' ? 'Display email address on profile' : 
                                 'Display phone number on profile'}
                              </p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={value}
                                onChange={(e) => handleSettingsChange('privacy', key, e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card.Content>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
