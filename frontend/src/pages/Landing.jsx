import React from 'react';
import { Calendar, Users, GraduationCap, Settings, User, LogIn, UserPlus, ArrowRight, Star, CheckCircle } from 'lucide-react';
import Button from '../components/UI/Button';
import Card from '../components/UI/Card';
import { Link } from 'react-router-dom';

const Landing = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Calendar className="h-8 w-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900">EventHub</span>
            </div>
            
            <nav className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-primary-600 transition-colors">Features</a>
              <a href="#about" className="text-gray-600 hover:text-primary-600 transition-colors">About</a>
              <a href="#contact" className="text-gray-600 hover:text-primary-600 transition-colors">Contact</a>
            </nav>

            <div className="flex items-center space-x-4">
              <Link to="/student-login">
                <Button variant="outline" size="sm">
                  <LogIn className="h-4 w-4 mr-2" />
                  Login
                </Button>
              </Link>
              <Link to="/student-login">
                <Button size="sm">
                  <UserPlus className="h-4 w-4 mr-2" />
                  Sign Up
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Welcome to{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-purple-600">
                EventHub
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              The ultimate event management platform for educational institutions. 
              Seamlessly organize, manage, and track events with our intuitive system.
            </p>
            
            {/* Login Options */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Card className="p-8 hover:shadow-lg transition-all duration-300 border-2 hover:border-primary-200">
                <div className="text-center">
                  <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <GraduationCap className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Student Portal</h3>
                  <p className="text-gray-600 mb-4">Access events, register, and manage your participation</p>
                  <Link to="/student-login" className="w-full">
                    <Button className="w-full">
                      <LogIn className="h-4 w-4 mr-2" />
                      Student Login
                    </Button>
                  </Link>
                </div>
              </Card>

              <Card className="p-8 hover:shadow-lg transition-all duration-300 border-2 hover:border-primary-200">
                <div className="text-center">
                  <div className="h-16 w-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Users className="h-8 w-8 text-purple-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Teacher Portal</h3>
                  <p className="text-gray-600 mb-4">Create events, manage students, and track attendance</p>
                  <Link to="/teacher-login" className="w-full">
                    <Button className="w-full">
                      <LogIn className="h-4 w-4 mr-2" />
                      Teacher Login
                    </Button>
                  </Link>
                </div>
              </Card>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/events">
                <Button size="lg" className="flex items-center">
                  Get Started
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
              <Button variant="outline" size="lg">
                Learn More
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Why Choose EventHub?</h2>
            <p className="text-xl text-gray-600">Powerful features designed for educational excellence</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="text-center p-8 hover:shadow-lg transition-all duration-300">
              <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Calendar className="h-6 w-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Event Management</h3>
              <p className="text-gray-600">Create, schedule, and manage events with ease. Full calendar integration and automated notifications.</p>
            </Card>

            <Card className="text-center p-8 hover:shadow-lg transition-all duration-300">
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Student Tracking</h3>
              <p className="text-gray-600">Track student participation, attendance, and engagement across all events and activities.</p>
            </Card>

            <Card className="text-center p-8 hover:shadow-lg transition-all duration-300">
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Settings className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Easy Administration</h3>
              <p className="text-gray-600">Intuitive admin panel for teachers and administrators to manage all aspects of the system.</p>
            </Card>

            <Card className="text-center p-8 hover:shadow-lg transition-all duration-300">
              <div className="h-12 w-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Star className="h-6 w-6 text-orange-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Feedback System</h3>
              <p className="text-gray-600">Collect and analyze feedback from students to continuously improve your events.</p>
            </Card>

            <Card className="text-center p-8 hover:shadow-lg transition-all duration-300">
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Attendance Tracking</h3>
              <p className="text-gray-600">Automated attendance tracking with QR codes and digital check-ins for seamless management.</p>
            </Card>

            <Card className="text-center p-8 hover:shadow-lg transition-all duration-300">
              <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <User className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Profile Management</h3>
              <p className="text-gray-600">Comprehensive profile management for students and teachers with customizable settings.</p>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to Get Started?</h2>
          <p className="text-xl text-primary-100 mb-8">
            Join thousands of educational institutions already using EventHub to manage their events.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" className="bg-white text-primary-600 hover:bg-gray-100">
              <UserPlus className="h-4 w-4 mr-2" />
              Create Account
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-primary-600">
              <LogIn className="h-4 w-4 mr-2" />
              Sign In
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Calendar className="h-6 w-6 text-primary-400" />
                <span className="text-xl font-bold">EventHub</span>
              </div>
              <p className="text-gray-400">The ultimate event management platform for educational institutions.</p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Support</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Account</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Student Login</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Teacher Login</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Sign Up</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Profile Settings</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <ul className="space-y-2 text-gray-400">
                <li>support@eventhub.com</li>
                <li>+1 (555) 123-4567</li>
                <li>123 Education St, Campus City</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 EventHub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
