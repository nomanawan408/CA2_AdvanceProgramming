"""
Database models for DBS Event Management System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for all three roles: superadmin, organizer, student"""
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(50), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # superadmin, organizer, student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    societies = db.relationship('Society', backref='head', lazy=True)
    events_created = db.relationship('Event', backref='creator', lazy=True)
    registrations = db.relationship('Registration', backref='student', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email} - {self.role}>'


class Society(db.Model):
    """Society model - managed by organizers"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    society_head_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='society', lazy=True)
    
    def __repr__(self):
        return f'<Society {self.name}>'


class Event(db.Model):
    """Event model - can be standalone or linked to society"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    cost = db.Column(db.Float, default=0.0)
    society_id = db.Column(db.Integer, db.ForeignKey('society.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('Registration', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def get_registered_count(self):
        """Get number of registered students"""
        return len(self.registrations)
    
    def available_slots(self):
        """Get number of available slots"""
        return self.capacity - self.get_registered_count()
    
    def is_full(self):
        """Check if event is at capacity"""
        return self.get_registered_count() >= self.capacity
    
    def __repr__(self):
        return f'<Event {self.title}>'


class Registration(db.Model):
    """Registration model - links students to events"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    phone_number = db.Column(db.String(20), nullable=True)
    payment_method = db.Column(db.String(20), nullable=True) # 'onsite' or 'online'
    invoice_path = db.Column(db.String(255), nullable=True)
    
    # Unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('event_id', 'student_id', name='unique_registration'),)
    
    def __repr__(self):
        return f'<Registration Event:{self.event_id} Student:{self.student_id}>'
