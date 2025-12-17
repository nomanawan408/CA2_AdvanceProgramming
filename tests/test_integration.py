"""
Integration Tests for DBS Event Management System
Tests core workflows: Student registration, Event creation, Registration system
"""
import pytest
from datetime import datetime, timedelta
from io import BytesIO
from models import db, User, Society, Event, Registration


class TestStudentRegistrationWorkflow:
    """Test complete student registration and event participation workflow"""
    
    def test_complete_student_journey(self, client, app):
        """Test student registration -> login -> browse -> register for event"""
        # Step 1: Student Registration
        resp = client.post("/register", data={
            "student_number": "S7777",
            "name": "Journey Student",
            "email": "journey@test.ie",
            "password": "journey123"
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
        
        # Step 2: Student Login
        resp = client.post("/login", data={
            "email": "journey@test.ie",
            "password": "journey123"
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
        
        # Step 3: Browse Events
        resp = client.get("/student/events")
        assert resp.status_code == 200
        
        # Step 4: Register for a free event
        with app.app_context():
            event = Event.query.filter_by(is_paid=False).first()
            assert event is not None
        
        resp = client.post(f"/event/{event.id}/register", data={
            "phone_number": "0871234567",
            "payment_method": ""
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
        
        # Step 5: Verify registration exists
        with app.app_context():
            student = User.query.filter_by(email="journey@test.ie").first()
            registration = Registration.query.filter_by(
                event_id=event.id, student_id=student.id
            ).first()
            assert registration is not None
            assert registration.phone_number == "0871234567"
    
    def test_paid_event_registration_workflow(self, client, app, sample_invoice_bytes):
        """Test registration for paid event with invoice upload"""
        # Login as existing student
        client.post("/login", data={
            "email": "student@dbs.ie",
            "password": "student123"
        })
        
        with app.app_context():
            event = Event.query.filter_by(is_paid=True).first()
            assert event is not None
        
        # Register for paid event with online payment and invoice
        resp = client.post(f"/event/{event.id}/register", data={
            "phone_number": "0879876543",
            "payment_method": "online",
            "invoice": (sample_invoice_bytes, "test_invoice.png")
        }, content_type="multipart/form-data", follow_redirects=False)
        assert resp.status_code in (301, 302)
        
        # Verify registration was created with invoice
        with app.app_context():
            student = User.query.filter_by(email="student@dbs.ie").first()
            registration = Registration.query.filter_by(
                event_id=event.id, student_id=student.id
            ).first()
            assert registration is not None
            assert registration.payment_method == "online"
            assert registration.invoice_path is not None


class TestEventManagementWorkflow:
    """Test event creation and management workflow"""
    
    def test_organizer_creates_event(self, login_organizer, app):
        """Test organizer creating and managing events"""
        # Create a free event
        future_date = datetime.utcnow() + timedelta(days=10)
        resp = login_organizer.post("/organizer/add-event", data={
            "title": "Organizer Test Event",
            "description": "Event created by organizer",
            "event_date": future_date.strftime("%Y-%m-%dT%H:%M"),
            "location": "Organizer Room",
            "capacity": "25",
            "is_paid": "",
            "cost": "0.0"
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
        
        # Verify event was created
        with app.app_context():
            organizer = User.query.filter_by(email="organizer@dbs.ie").first()
            event = Event.query.filter_by(title="Organizer Test Event").first()
            assert event is not None
            assert event.created_by == organizer.id
            assert event.society_id is not None  # Should be linked to organizer's society
    
    def test_admin_creates_standalone_event(self, login_admin, app):
        """Test admin creating standalone events"""
        # Create a paid standalone event
        future_date = datetime.utcnow() + timedelta(days=15)
        resp = login_admin.post("/admin/add-event", data={
            "title": "Admin Test Event",
            "description": "Event created by admin",
            "event_date": future_date.strftime("%Y-%m-%dT%H:%M"),
            "location": "Admin Room",
            "capacity": "30",
            "society_id": "",
            "is_paid": "on",
            "cost": "45.00"
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
        
        # Verify event was created
        with app.app_context():
            event = Event.query.filter_by(title="Admin Test Event").first()
            assert event is not None
            assert event.society_id is None  # Should be standalone
            assert event.is_paid is True
            assert event.cost == 45.00


class TestRegistrationSystemWorkflow:
    """Test registration system core functionality"""
    
    def test_event_capacity_management(self, login_student, app):
        """Test event capacity prevents overbooking"""
        # Create small capacity event
        with app.app_context():
            organizer = User.query.filter_by(role="organizer").first()
            event = Event(
                title="Capacity Test Event",
                event_date=datetime.utcnow() + timedelta(days=20),
                location="Capacity Room",
                capacity=1,
                is_paid=False,
                cost=0.0,
                created_by=organizer.id
            )
            db.session.add(event)
            db.session.commit()
            
            # Fill event with another student
            other_student = User(student_number="S5555", name="Other", email="other@test.ie", role="student")
            other_student.set_password("pass")
            db.session.add(other_student)
            db.session.commit()
            
            registration = Registration(event_id=event.id, student_id=other_student.id, phone_number="0879999999")
            db.session.add(registration)
            db.session.commit()
            
            assert event.is_full() is True
        
        # Try to register for full event
        resp = login_student.post(f"/event/{event.id}/register", data={
            "phone_number": "0878888888",
            "payment_method": ""
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
        assert resp.headers["Location"].endswith("/")
        
        # Verify no new registration was created
        with app.app_context():
            student = User.query.filter_by(email="student@dbs.ie").first()
            registration = Registration.query.filter_by(
                event_id=event.id, student_id=student.id
            ).first()
            assert registration is None
    
    def test_duplicate_registration_prevention(self, login_student, app):
        """Test students cannot register twice for same event"""
        with app.app_context():
            event = Event.query.filter_by(is_paid=False).first()
            assert event is not None
            event_id = event.id
            
            # Create first registration
            student = User.query.filter_by(email="student@dbs.ie").first()
            registration = Registration(
                event_id=event_id,
                student_id=student.id,
                phone_number="0871234567"
            )
            db.session.add(registration)
            db.session.commit()
        
        # Try to register again
        resp = login_student.post(f"/event/{event_id}/register", data={
            "phone_number": "0877654321",
            "payment_method": ""
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
        assert resp.headers["Location"].endswith("/student/dashboard")
        
        # Verify only one registration exists
        with app.app_context():
            student = User.query.filter_by(email="student@dbs.ie").first()
            registrations = Registration.query.filter_by(
                event_id=event_id, student_id=student.id
            ).all()
            assert len(registrations) == 1
    
    def test_event_unregistration(self, login_student, app):
        """Test student can unregister from events"""
        # Create event and register
        with app.app_context():
            organizer = User.query.filter_by(role="organizer").first()
            event = Event(
                title="Unregistration Test Event",
                event_date=datetime.utcnow() + timedelta(days=25),
                location="Unregistration Room",
                capacity=10,
                is_paid=False,
                cost=0.0,
                created_by=organizer.id
            )
            db.session.add(event)
            db.session.commit()
            event_id = event.id
        
        # Register for event
        resp = login_student.post(f"/event/{event_id}/register", data={
            "phone_number": "0871234567",
            "payment_method": ""
        }, follow_redirects=False)
        assert resp.status_code in (301, 302)
        
        # Verify registration exists
        with app.app_context():
            student = User.query.filter_by(email="student@dbs.ie").first()
            registration = Registration.query.filter_by(
                event_id=event_id, student_id=student.id
            ).first()
            assert registration is not None
        
        # Unregister from event
        resp = login_student.get(f"/event/{event_id}/unregister", follow_redirects=False)
        assert resp.status_code in (301, 302)
        
        # Verify registration was deleted
        with app.app_context():
            registration = Registration.query.filter_by(
                event_id=event_id, student_id=student.id
            ).first()
            assert registration is None


class TestRoleBasedAccessWorkflow:
    """Test role-based access control"""
    
    def test_student_cannot_access_admin_routes(self, login_student):
        """Test students cannot access admin or organizer routes"""
        admin_routes = ["/admin/dashboard", "/admin/events", "/admin/organizers"]
        organizer_routes = ["/organizer/dashboard", "/organizer/add-event"]
        
        for route in admin_routes + organizer_routes:
            resp = login_student.get(route)
            assert resp.status_code in (302, 403)  # Either redirect to login or forbidden
    
    def test_organizer_cannot_access_admin_routes(self, login_organizer):
        """Test organizers cannot access admin routes"""
        admin_routes = ["/admin/dashboard", "/admin/events", "/admin/organizers"]
        
        for route in admin_routes:
            resp = login_organizer.get(route)
            assert resp.status_code in (302, 403)  # Either redirect to login or forbidden
    
    def test_admin_can_access_all_routes(self, login_admin):
        """Test admin can access all routes"""
        routes = [
            "/admin/dashboard",
            "/admin/events", 
            "/admin/organizers",
            "/student/dashboard",
            "/organizer/dashboard"
        ]
        
        for route in routes:
            resp = login_admin.get(route)
            assert resp.status_code in (200, 302)  # Either direct access or redirect
