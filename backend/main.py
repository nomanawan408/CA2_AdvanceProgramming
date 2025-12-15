"""
DBS Event Management System - Main Application
A simple Flask application for managing events at Dublin Business School
"""
from flask import Flask
from flask_login import LoginManager
from models import db, User, Society, Event, Registration
from datetime import datetime
import os

from backend.routes import (
    public_bp,
    admin_bp,
    organizer_bp,
    student_bp,
    exports_bp,
    registrations_bp,
)

# Paths for frontend assets (templates and static files)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend', 'static')

# Initialize Flask app pointing at the frontend folders
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['SECRET_KEY'] = 'dbs-event-system-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'public.login'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# Register blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(organizer_bp)
app.register_blueprint(student_bp)
app.register_blueprint(exports_bp)
app.register_blueprint(registrations_bp)


# ============== DATABASE INITIALIZATION ==============

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin exists
        if not User.query.filter_by(email='admin@dbs.ie').first():
            # Create superadmin
            admin = User(name='Super Admin', email='admin@dbs.ie', role='superadmin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample organizer
            organizer = User(name='John Organizer', email='organizer@dbs.ie', role='organizer')
            organizer.set_password('org123')
            db.session.add(organizer)
            
            # Create sample student
            student = User(name='Jane Student', email='student@dbs.ie', role='student')
            student.set_password('student123')
            db.session.add(student)
            
            db.session.commit()
            
            # Create sample society
            society = Society(
                name='Tech Society',
                description='Technology and Innovation Club',
                society_head_id=organizer.id
            )
            db.session.add(society)
            db.session.commit()
            
            # Create sample free event
            free_event = Event(
                title='Welcome Day 2025 (Free)',
                description='Welcome event for new students',
                event_date=datetime(2025, 1, 15, 10, 0),
                location='Main Hall',
                capacity=100,
                is_paid=False,
                cost=0.0,
                society_id=society.id,
                created_by=organizer.id
            )
            db.session.add(free_event)
            
            # Create sample paid event
            paid_event = Event(
                title='Cyber Security Workshop (Paid)',
                description='Advanced workshop on cyber security techniques.',
                event_date=datetime(2025, 2, 20, 14, 0),
                location='Lecture Theatre 1',
                capacity=30,
                is_paid=True,
                cost=25.00,
                society_id=society.id,
                created_by=organizer.id
            )
            db.session.add(paid_event)
            db.session.commit()
            
            print("Database initialized with sample data")
            print("Admin: admin@dbs.ie / admin123")
            print("Organizer: organizer@dbs.ie / org123")
            print("Student: student@dbs.ie / student123")
