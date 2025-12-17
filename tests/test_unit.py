"""
Unit Tests for DBS Event Management System
Tests core functionality: User, Event, Registration models and basic routes
"""
import pytest
from datetime import datetime, timedelta
from models import db, User, Society, Event, Registration


class TestUserModel:
    """Test User model core functionality"""
    
    def test_user_creation(self, app):
        """Test basic user creation"""
        with app.app_context():
            user = User(
                student_number="S1234",
                name="Test Student",
                email="test@test.ie",
                role="student"
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.student_number == "S1234"
            assert user.name == "Test Student"
            assert user.email == "test@test.ie"
            assert user.role == "student"
    
    def test_password_hashing(self, app):
        """Test password hashing functionality"""
        with app.app_context():
            user = User(
                student_number="S1235",
                name="Test User",
                email="user@test.ie",
                role="student"
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            assert user.check_password("password123") is True
            assert user.check_password("wrongpassword") is False
            assert user.password_hash != "password123"


class TestEventModel:
    """Test Event model core functionality"""
    
    def test_event_creation(self, app):
        """Test basic event creation"""
        with app.app_context():
            organizer = User.query.filter_by(role="organizer").first()
            event = Event(
                title="Test Event",
                description="Test event description",
                event_date=datetime.utcnow() + timedelta(days=7),
                location="Test Room",
                capacity=50,
                is_paid=False,
                cost=0.0,
                created_by=organizer.id
            )
            db.session.add(event)
            db.session.commit()
            
            assert event.id is not None
            assert event.title == "Test Event"
            assert event.capacity == 50
            assert event.is_paid is False
    
    def test_event_capacity_methods(self, app):
        """Test event capacity management methods"""
        with app.app_context():
            organizer = User.query.filter_by(role="organizer").first()
            event = Event(
                title="Capacity Test Event",
                event_date=datetime.utcnow() + timedelta(days=7),
                location="Test Room",
                capacity=2,
                is_paid=False,
                cost=0.0,
                created_by=organizer.id
            )
            db.session.add(event)
            db.session.commit()
            
            # Test empty event
            assert event.get_registered_count() == 0
            assert event.available_slots() == 2
            assert event.is_full() is False
            
            # Add one registration
            student = User.query.filter_by(role="student").first()
            registration = Registration(event_id=event.id, student_id=student.id, phone_number="0871234567")
            db.session.add(registration)
            db.session.commit()
            
            assert event.get_registered_count() == 1
            assert event.available_slots() == 1
            assert event.is_full() is False
            
            # Fill capacity
            student2 = User(student_number="S9999", name="Student2", email="std2@test.ie", role="student")
            student2.set_password("pass")
            db.session.add(student2)
            db.session.commit()
            
            registration2 = Registration(event_id=event.id, student_id=student2.id, phone_number="0877654321")
            db.session.add(registration2)
            db.session.commit()
            
            assert event.get_registered_count() == 2
            assert event.available_slots() == 0
            assert event.is_full() is True


class TestRegistrationModel:
    """Test Registration model core functionality"""
    
    def test_registration_creation(self, app):
        """Test basic registration creation"""
        with app.app_context():
            event = Event.query.first()
            student = User.query.filter_by(role="student").first()
            
            registration = Registration(
                event_id=event.id,
                student_id=student.id,
                phone_number="0871234567",
                payment_method="onsite"
            )
            db.session.add(registration)
            db.session.commit()
            
            assert registration.id is not None
            assert registration.event_id == event.id
            assert registration.student_id == student.id
            assert registration.phone_number == "0871234567"
            assert registration.payment_method == "onsite"


class TestBasicRoutes:
    """Test basic route functionality"""
    
    def test_homepage(self, client):
        """Test homepage loads"""
        resp = client.get("/")
        assert resp.status_code == 200
    
    def test_login_page(self, client):
        """Test login page loads"""
        resp = client.get("/login")
        assert resp.status_code == 200
    
    def test_register_page(self, client):
        """Test registration page loads"""
        resp = client.get("/register")
        assert resp.status_code == 200
    
    def test_valid_login(self, client):
        """Test valid login functionality"""
        resp = client.post("/login", data={
            "email": "student@dbs.ie",
            "password": "student123"
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
    
    def test_invalid_login(self, client):
        """Test invalid login handling"""
        resp = client.post("/login", data={
            "email": "wrong@test.ie",
            "password": "wrongpassword"
        })
        assert resp.status_code == 200
    
    def test_student_registration(self, client):
        """Test student registration"""
        resp = client.post("/register", data={
            "student_number": "S8888",
            "name": "New Student",
            "email": "newstudent@test.ie",
            "password": "password123"
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
    
    def test_protected_routes_without_login(self, client):
        """Test protected routes redirect when not logged in"""
        protected_routes = [
            "/student/dashboard",
            "/organizer/dashboard", 
            "/admin/dashboard"
        ]
        
        for route in protected_routes:
            resp = client.get(route)
            assert resp.status_code in (302, 403)
    
    def test_student_dashboard_access(self, login_student):
        """Test student can access their dashboard"""
        resp = login_student.get("/student/dashboard")
        assert resp.status_code == 200
    
    def test_organizer_dashboard_access(self, login_organizer):
        """Test organizer can access their dashboard"""
        resp = login_organizer.get("/organizer/dashboard")
        assert resp.status_code == 200
    
    def test_admin_dashboard_access(self, login_admin):
        """Test admin can access their dashboard"""
        resp = login_admin.get("/admin/dashboard")
        assert resp.status_code == 200
