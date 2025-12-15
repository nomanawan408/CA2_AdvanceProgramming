# DBS Event Management System

A simple event management system for Dublin Business School built with Flask and Tailwind CSS.

## Overview

This system allows Dublin Business School to manage events, societies, and student registrations efficiently. It features three distinct user roles with specific permissions and capabilities.

## Features

### User Roles

1. **SuperAdmin**
   - Add and manage organizers
   - Create and manage societies
   - Create standalone events (not linked to societies)
   - View all events and registrations
   - Export student registration data (CSV/PDF)

2. **Organizer (Society Head)**
   - Create events linked to their society
   - View registrations for their events
   - Export registration data for their events (CSV/PDF)

3. **Student**
   - Browse public event listings
   - Register for events
   - View their registered events
   - Unregister from events

### Core Functionality

- **Authentication System**: Secure login with role-based access control
- **Society Management**: Create societies with assigned organizers as heads
- **Event Management**: Create, view, and delete events
- **Event Registration**: Students can register for events with capacity limits
- **Data Export**: Export registered student data in CSV or PDF format
- **Public Event Listing**: One-page website showing all available events

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Authentication**: Flask-Login
- **PDF Generation**: ReportLab

## Project Structure

```
dbs_event_system/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── export_routes.py            # CSV/PDF export functionality
├── requirements.txt            # Python dependencies
├── test_app.py                 # Test script
├── README.md                   # This file
├── instance/
│   └── events.db              # SQLite database
├── static/
│   ├── css/
│   │   └── style.css          # Custom CSS
│   └── js/
│       └── main.js            # JavaScript
└── templates/
    ├── base.html              # Base template
    ├── index.html             # Public event listing
    ├── login.html             # Login page
    ├── register.html          # Student registration
    ├── registrations.html     # View event registrations
    ├── admin/                 # Admin templates
    │   ├── dashboard.html
    │   ├── add_organizer.html
    │   ├── add_society.html
    │   ├── add_event.html
    │   ├── organizers.html
    │   ├── societies.html
    │   └── events.html
    ├── organizer/             # Organizer templates
    │   ├── dashboard.html
    │   ├── add_event.html
    │   └── events.html
    └── student/               # Student templates
        └── dashboard.html
```

## Database Models

### User
- `id`: Primary key
- `email`: Unique email address
- `password_hash`: Hashed password
- `name`: Full name
- `role`: User role (superadmin/organizer/student)
- `created_at`: Account creation timestamp

### Society
- `id`: Primary key
- `name`: Society name (unique)
- `description`: Society description
- `society_head_id`: Foreign key to User (organizer)
- `created_at`: Creation timestamp

### Event
- `id`: Primary key
- `title`: Event title
- `description`: Event description
- `event_date`: Date and time of event
- `location`: Event location
- `capacity`: Maximum number of attendees
- `society_id`: Foreign key to Society (nullable for standalone events)
- `created_by`: Foreign key to User (creator)
- `created_at`: Creation timestamp

### Registration
- `id`: Primary key
- `event_id`: Foreign key to Event
- `student_id`: Foreign key to User (student)
- `registration_date`: Registration timestamp
- Unique constraint on (event_id, student_id) to prevent duplicate registrations

## Installation

1. **Install Dependencies**
   ```bash
   pip3 install Flask Flask-SQLAlchemy Flask-Login reportlab
   ```

2. **Initialize Database**
   ```bash
   python3 app.py
   ```
   This will create the database and populate it with sample data.

## Running the Application

1. **Start the Flask Server**
   ```bash
   python3 app.py
   ```

2. **Access the Application**
   Open your browser and navigate to: `http://localhost:5000`

## Default Login Credentials

The system comes with pre-configured demo accounts:

- **Admin**: admin@dbs.ie / admin123
- **Organizer**: organizer@dbs.ie / org123
- **Student**: student@dbs.ie / student123

## Usage Guide

### For SuperAdmin

1. **Login** with admin credentials
2. **Add Organizers**: Navigate to "Add Organizer" to create organizer accounts
3. **Create Societies**: Navigate to "Add Society" and assign an organizer as society head
4. **Create Events**: Navigate to "Add Event" to create standalone events or link to societies
5. **View Registrations**: Click on any event to view registered students
6. **Export Data**: Use CSV or PDF export buttons on the registrations page

### For Organizers

1. **Login** with organizer credentials
2. **View Your Society**: See your assigned society on the dashboard
3. **Create Events**: Click "Create New Event" to add events for your society
4. **Manage Registrations**: View and export registration data for your events

### For Students

1. **Register** for a new account or **Login** with existing credentials
2. **Browse Events**: View all available events on the homepage
3. **Register for Events**: Click "Register Now" on any event card
4. **View Registrations**: Check your dashboard to see registered events
5. **Unregister**: Click "Unregister" to cancel your registration

## Key Features Explained

### Role-Based Access Control

The system uses decorators to enforce role-based permissions:
- `@admin_required`: Only superadmin can access
- `@organizer_required`: Superadmin and organizers can access
- `@student_required`: Only students can access
- `@login_required`: Any authenticated user can access

### Event Registration

- Students can only register once per event
- System checks event capacity before allowing registration
- Automatic validation prevents duplicate registrations
- Students can unregister from events

### Data Export

Both CSV and PDF export formats are available:
- **CSV**: Simple comma-separated values for spreadsheet import
- **PDF**: Professional formatted report with event details and student list

### Public Event Listing

The homepage (`/`) displays all events with:
- Event details (title, date, location, capacity)
- Society information (if linked)
- Registration status for logged-in students
- Registration buttons for available events

## Architecture Pattern

The system follows a **Layered Architecture** pattern:

1. **Presentation Layer**: HTML templates with Tailwind CSS
2. **Application Layer**: Flask routes and business logic
3. **Data Layer**: SQLAlchemy ORM models
4. **Database Layer**: SQLite database

## Security Features

- Password hashing using Werkzeug security
- Session-based authentication with Flask-Login
- Role-based access control
- CSRF protection (Flask default)
- SQL injection prevention (SQLAlchemy ORM)

## Testing

Run the test script to verify system functionality:

```bash
python3 test_app.py
```

This will test:
- Database connectivity
- User authentication
- Society and event creation
- Registration system

## Development Notes

This is an **intermediate-level** implementation designed for educational purposes:
- Simple, readable code with comments
- Basic error handling
- Clean but not overly complex UI
- Standard Flask patterns and best practices
- SQLite for easy setup (no external database required)

## Future Enhancements

Potential improvements for production use:
- Email notifications for event registrations
- Event categories and filtering
- Image uploads for events
- Calendar view for events
- User profile management
- Event attendance tracking
- Advanced reporting and analytics
- PostgreSQL or MySQL for production database

## Troubleshooting

### Database Issues
If you encounter database errors, delete the `instance/events.db` file and restart the application to reinitialize.

### Port Already in Use
If port 5000 is already in use, modify the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip3 install -r requirements.txt
```

## License

This project is created for educational purposes as part of the Dublin Business School Advanced Programming Techniques module (B9CY108).

## Author

Created for DBS Event Management System Assignment
Module: Advanced Programming Techniques (B9CY108)
Programme: MSc Cyber Security
