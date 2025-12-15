from datetime import datetime, timedelta

from models import db, Event, Registration, User


def test_event_available_slots_and_is_full(app):
    with app.app_context():
        organizer = User.query.filter_by(role="organizer").first()
        assert organizer is not None

        event = Event(
            title="Capacity Event",
            description="",
            event_date=datetime.utcnow() + timedelta(days=1),
            location="X",
            capacity=2,
            is_paid=False,
            cost=0.0,
            society_id=None,
            created_by=organizer.id,
        )
        db.session.add(event)
        db.session.commit()

        assert event.get_registered_count() == 0
        assert event.available_slots() == 2
        assert event.is_full() is False

        student1 = User.query.filter_by(role="student").first()
        assert student1 is not None
        reg1 = Registration(event_id=event.id, student_id=student1.id)
        db.session.add(reg1)
        db.session.commit()

        assert event.get_registered_count() == 1
        assert event.available_slots() == 1
        assert event.is_full() is False

        student2 = User(name="Student2", email="student2@dbs.ie", role="student")
        student2.set_password("student123")
        db.session.add(student2)
        db.session.commit()

        reg2 = Registration(event_id=event.id, student_id=student2.id)
        db.session.add(reg2)
        db.session.commit()

        assert event.get_registered_count() == 2
        assert event.available_slots() == 0
        assert event.is_full() is True
