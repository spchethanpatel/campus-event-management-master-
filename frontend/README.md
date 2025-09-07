# EventHub Frontend

A modern React frontend for the Event Management System built with Vite, TypeScript, and Tailwind CSS.

## Features

- 🎨 **Modern UI**: Built with Tailwind CSS for beautiful, responsive design
- ⚡ **Fast Development**: Powered by Vite for lightning-fast development experience
- 🔧 **TypeScript**: Full TypeScript support for better development experience
- 📱 **Responsive**: Mobile-first design that works on all devices
- 🎯 **Component-Based**: Reusable UI components for consistency
- 🔄 **Real-time Updates**: Live data from the backend API

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icons

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend server running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout/         # Layout components (Navbar, Layout)
│   └── UI/             # Basic UI components (Button, Card, etc.)
├── pages/              # Page components
│   ├── Dashboard.jsx   # Main dashboard
│   ├── Events.jsx      # Events management
│   ├── Students.jsx    # Students management
│   ├── Colleges.jsx    # Colleges management
│   ├── Registrations.jsx # Registrations management
│   ├── Feedback.jsx    # Feedback management
│   └── Analytics.jsx   # Analytics and reports
├── services/           # API services
│   └── api.js         # API client configuration
├── App.tsx            # Main app component
├── main.tsx           # App entry point
└── index.css          # Global styles with Tailwind
```

## API Integration

The frontend connects to the backend API running on `http://localhost:8000`. The API service is configured in `src/services/api.js` with:

- Automatic request/response interceptors
- Error handling
- Authentication token management
- Base URL configuration

## Features Overview

### Dashboard
- System statistics overview
- Quick action buttons
- System health status

### Events Management
- View all events
- Event details with date, time, location
- Create, edit, delete events
- Event type filtering

### Students Management
- Student directory
- Search and filter students
- Student profile management
- College association

### Colleges Management
- College directory
- College information management
- Contact details
- Student associations

### Registrations
- Event registration tracking
- Registration status management
- Student-event associations

### Feedback
- Event feedback collection
- Rating system
- Comment management
- Feedback analytics

### Analytics
- System performance metrics
- Data distribution charts
- Usage statistics
- Health monitoring

## Styling

The application uses Tailwind CSS with a custom design system:

- **Primary Colors**: Blue theme for main actions
- **Secondary Colors**: Gray scale for text and backgrounds
- **Components**: Consistent button, card, and form styles
- **Responsive**: Mobile-first responsive design
- **Dark Mode**: Ready for dark mode implementation

## Development

### Adding New Pages

1. Create a new component in `src/pages/`
2. Add the route in `src/App.tsx`
3. Add navigation link in `src/components/Layout/Navbar.jsx`

### Adding New Components

1. Create component in appropriate folder under `src/components/`
2. Export from component file
3. Import and use in pages

### API Integration

1. Add new endpoints in `src/services/api.js`
2. Use the `apiService` object for API calls
3. Handle loading states and errors appropriately

## Production Build

To build for production:

```bash
npm run build
```

The built files will be in the `dist/` directory, ready for deployment.

## Contributing

1. Follow the existing code structure
2. Use TypeScript for type safety
3. Follow Tailwind CSS conventions
4. Add proper error handling
5. Test on different screen sizes

## License

This project is part of the Event Management System.