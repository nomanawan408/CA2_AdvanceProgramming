"""
DBS Event Management System - Main Application
A simple Flask application for managing events at Dublin Business School
"""
from flask import Flask, send_from_directory
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


# ============== INVOICE SERVING ROUTE ==============

@app.route('/invoices/<filename>')
def serve_invoice(filename):
    """Serve invoice files securely"""
    invoices_dir = os.path.join(app.static_folder, 'invoices')
    try:
        return send_from_directory(invoices_dir, filename)
    except (FileNotFoundError, Exception) as e:
        # Handle both standard FileNotFoundError and Werkzeug NotFound
        return "Invoice file not found", 404


# ============== DATABASE INITIALIZATION ==============

def init_db():
    """Initialize database with empty schema"""
    with app.app_context():
        db.create_all()
        print("Database initialized with empty schema")
        print("Visit http://localhost:5000/ to create first admin account")
