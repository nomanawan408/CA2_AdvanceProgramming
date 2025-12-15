# Quick Start Guide - DBS Event Management System

## Installation & Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip3 install Flask Flask-SQLAlchemy Flask-Login reportlab
```

### Step 2: Navigate to Project Directory
```bash
cd dbs_event_system
```

### Step 3: Run the Application
```bash
python3 app.py
```

The application will:
- Create the database automatically
- Initialize with sample data
- Start the server on http://localhost:5000

## Quick Test

### Option 1: Run Test Script
```bash
python3 test_app.py
```

### Option 2: Access in Browser
1. Open browser: http://localhost:5000
2. Try logging in with demo accounts

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@dbs.ie | admin123 |
| Organizer | organizer@dbs.ie | org123 |
| Student | student@dbs.ie | student123 |

## Quick Tour

### As Admin (admin@dbs.ie)
1. Login → Dashboard
2. Click "Add Organizer" → Create new organizer
3. Click "Add Society" → Create society with organizer
4. Click "Add Event" → Create standalone event
5. Click "Manage Events" → View all events
6. Click "View" on any event → See registrations
7. Click "Export CSV" or "Export PDF" → Download data

### As Organizer (organizer@dbs.ie)
1. Login → Dashboard
2. See your society: "Tech Society"
3. Click "Create New Event" → Add event for your society
4. Click "View Registrations" → See who registered
5. Export registration data

### As Student (student@dbs.ie)
1. Login → Homepage
2. Browse available events
3. Click "Register Now" on any event
4. Go to Dashboard → See your registrations
5. Click "Unregister" to cancel

### As New Student
1. Click "Register" on homepage
2. Fill in name, email, password
3. Login with new credentials
4. Register for events

## Key URLs

- Homepage (Public Events): http://localhost:5000/
- Login: http://localhost:5000/login
- Register: http://localhost:5000/register
- Admin Dashboard: http://localhost:5000/admin/dashboard
- Organizer Dashboard: http://localhost:5000/organizer/dashboard
- Student Dashboard: http://localhost:5000/student/dashboard

## File Structure Overview

```
dbs_event_system/
├── app.py              # Main application (start here)
├── models.py           # Database models
├── export_routes.py    # Export functionality
├── test_app.py         # Test script
├── instance/
│   └── events.db      # Database (auto-created)
├── templates/         # HTML pages
└── static/            # CSS and JavaScript
```

## Common Tasks

### Add a New Organizer (Admin)
1. Login as admin
2. Dashboard → "Add Organizer"
3. Enter name, email, password
4. Submit

### Create a Society (Admin)
1. Login as admin
2. Dashboard → "Add Society"
3. Enter society name and description
4. Select organizer as society head
5. Submit

### Create an Event (Admin or Organizer)
1. Login
2. Dashboard → "Add Event" or "Create New Event"
3. Fill in event details:
   - Title
   - Description
   - Date & Time
   - Location
   - Capacity
   - Society (optional for admin)
4. Submit

### Register for an Event (Student)
1. Login as student
2. Browse events on homepage
3. Click "Register Now" on desired event
4. Confirmation message appears
5. View in Dashboard

### Export Registration Data (Admin/Organizer)
1. Login
2. Navigate to event
3. Click "View Registrations"
4. Click "Export CSV" or "Export PDF"
5. File downloads automatically

## Troubleshooting

### "Database locked" error
- Stop the server (Ctrl+C)
- Delete `instance/events.db`
- Restart: `python3 app.py`

### "Port already in use"
- Change port in app.py: `app.run(port=5001)`

### "Module not found"
- Install dependencies: `pip3 install -r requirements.txt`

### Can't login
- Use demo credentials exactly as shown
- Check caps lock is off
- Try resetting database (delete events.db and restart)

## Next Steps

1. **Explore the Code**: Start with `app.py` to understand routes
2. **Customize**: Modify templates in `templates/` folder
3. **Add Features**: Extend models in `models.py`
4. **Test**: Use `test_app.py` as reference for testing

## Support

For issues or questions:
1. Check README.md for detailed documentation
2. Review code comments in app.py
3. Test with test_app.py to verify functionality

## Important Notes

- This is a development server (not for production)
- Database is SQLite (simple file-based)
- All passwords are hashed for security
- Sample data is created automatically on first run
- Export files download directly to browser

Enjoy using the DBS Event Management System! 🎉
