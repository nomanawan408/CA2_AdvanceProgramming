# DBS Event Management System - Project Plan

## System Overview
Event Management System for Dublin Business School with three user roles: SuperAdmin, Organizer, and Student.

## Key Requirements Analysis

### User Roles & Permissions
1. **SuperAdmin**
   - Add/manage organizers
   - Add/manage societies
   - Create standalone events (not linked to societies)
   - View all registered students
   - Export student data (CSV/PDF)

2. **Organizer (Society Head)**
   - Create events linked to their society
   - View registered students for their events
   - Export student data for their events (CSV/PDF)

3. **Student**
   - Browse public event listing
   - Register for events
   - View their registrations

### Core Features
- User authentication with role-based access
- Society management (with society heads)
- Event creation and management
- Event registration system
- Student data export (CSV/PDF)
- Public event listing page
- Role-specific dashboards

### Database Models
1. **User** - id, email, password_hash, role (superadmin/organizer/student), name
2. **Society** - id, name, description, society_head_id (FK to User)
3. **Event** - id, title, description, date, location, capacity, society_id (nullable), created_by (FK to User)
4. **Registration** - id, event_id, student_id, registration_date

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite (simple file-based)
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Authentication**: Flask-Login
- **Export**: CSV (built-in), ReportLab (PDF)

## Architecture Pattern
**Layered Pattern** - Simple MVC-like structure:
- Models (database)
- Routes/Controllers (Flask routes)
- Templates (HTML with Jinja2)

## Project Structure
```
dbs_event_system/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── forms.py               # Form handling (optional)
├── requirements.txt       # Dependencies
├── instance/
│   └── events.db         # SQLite database
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── main.js       # JavaScript
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Public event listing
    ├── login.html        # Login page
    ├── register.html     # User registration
    ├── admin/
    │   ├── dashboard.html
    │   ├── add_organizer.html
    │   ├── add_society.html
    │   └── add_event.html
    ├── organizer/
    │   ├── dashboard.html
    │   └── add_event.html
    └── student/
        └── dashboard.html
```

## Development Approach
- Keep code simple and readable (intermediate level)
- Basic error handling
- Simple validation
- Minimal JavaScript (form interactions)
- Clean but not overly complex UI
- Comments in code for clarity

## Implementation Phases
1. Setup Flask project and database models
2. Implement authentication system
3. Build CRUD operations for all entities
4. Create role-specific dashboards
5. Implement event registration
6. Build public event listing page
7. Add export functionality (CSV/PDF)
8. Testing and documentation
