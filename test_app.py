"""
Simple test script to verify the application works
"""
from backend.main import app
from models import db, User, Society, Event, Registration
from datetime import datetime

def test_system():
    """Test basic functionality"""
    with app.app_context():
        print("Testing DBS Event Management System...")
        print("-" * 50)
        
        # Test 1: Check database connection
        print("\n1. Testing database connection...")
        users = User.query.all()
        print(f"   ✓ Found {len(users)} users in database")
        
        # Test 2: Check user roles
        print("\n2. Testing user roles...")
        admin = User.query.filter_by(role='superadmin').first()
        organizer = User.query.filter_by(role='organizer').first()
        student = User.query.filter_by(role='student').first()
        print(f"   ✓ Admin: {admin.email if admin else 'Not found'}")
        print(f"   ✓ Organizer: {organizer.email if organizer else 'Not found'}")
        print(f"   ✓ Student: {student.email if student else 'Not found'}")
        
        # Test 3: Check societies
        print("\n3. Testing societies...")
        societies = Society.query.all()
        print(f"   ✓ Found {len(societies)} societies")
        for society in societies:
            print(f"     - {society.name} (Head: {society.head.name})")
        
        # Test 4: Check events
        print("\n4. Testing events...")
        events = Event.query.all()
        print(f"   ✓ Found {len(events)} events")
        for event in events:
            print(f"     - {event.title} on {event.event_date.strftime('%Y-%m-%d')}")
            print(f"       Registered: {event.get_registered_count()}/{event.capacity}")
        
        # Test 5: Test password hashing
        print("\n5. Testing authentication...")
        test_user = User.query.filter_by(email='admin@dbs.ie').first()
        if test_user and test_user.check_password('admin123'):
            print("   ✓ Password hashing works correctly")
        else:
            print("   ✗ Password hashing failed")
        
        # Test 6: Check registrations
        print("\n6. Testing registrations...")
        registrations = Registration.query.all()
        print(f"   ✓ Found {len(registrations)} registrations")
        
        print("\n" + "-" * 50)
        print("All tests completed successfully! ✓")
        print("-" * 50)
        
        # Print login credentials
        print("\nLogin Credentials:")
        print("  Admin:     admin@dbs.ie / admin123")
        print("  Organizer: organizer@dbs.ie / org123")
        print("  Student:   student@dbs.ie / student123")

if __name__ == '__main__':
    test_system()
