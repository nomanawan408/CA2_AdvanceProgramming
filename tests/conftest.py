import os
from datetime import datetime, timedelta
from io import BytesIO

import pytest

from backend.main import app as flask_app
from models import db, User, Society, Event, Registration


@pytest.fixture()
def app(tmp_path):
    """Create a fresh app + database for each test session."""

    test_db_path = tmp_path / "test.db"

    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{test_db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY="test-secret",
    )

    # Isolate static folder so invoice uploads don't pollute repo
    static_dir = tmp_path / "static"
    invoices_dir = static_dir / "invoices"
    invoices_dir.mkdir(parents=True, exist_ok=True)
    flask_app.static_folder = str(static_dir)

    with flask_app.app_context():
        db.drop_all()
        db.create_all()

        # Users
        admin = User(name="Admin", email="admin@dbs.ie", role="superadmin")
        admin.set_password("admin123")

        organizer = User(name="Organizer", email="organizer@dbs.ie", role="organizer")
        organizer.set_password("org123")

        student = User(name="Student", email="student@dbs.ie", role="student")
        student.set_password("student123")

        db.session.add_all([admin, organizer, student])
        db.session.commit()

        # Society + Events
        society = Society(
            name="Tech Society",
            description="Test society",
            society_head_id=organizer.id,
        )
        db.session.add(society)
        db.session.commit()

        paid_event = Event(
            title="Paid Event",
            description="Paid event desc",
            event_date=datetime.utcnow() + timedelta(days=7),
            location="Test Location",
            capacity=5,
            is_paid=True,
            cost=10.0,
            society_id=society.id,
            created_by=organizer.id,
        )
        free_event = Event(
            title="Free Event",
            description="Free event desc",
            event_date=datetime.utcnow() + timedelta(days=7),
            location="Test Location",
            capacity=5,
            is_paid=False,
            cost=0.0,
            society_id=society.id,
            created_by=organizer.id,
        )
        db.session.add_all([paid_event, free_event])
        db.session.commit()

    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


@pytest.fixture()
def login_admin(client):
    login(client, "admin@dbs.ie", "admin123")
    return client


@pytest.fixture()
def login_organizer(client):
    login(client, "organizer@dbs.ie", "org123")
    return client


@pytest.fixture()
def login_student(client):
    login(client, "student@dbs.ie", "student123")
    return client


@pytest.fixture()
def sample_invoice_bytes():
    return BytesIO(b"fake-invoice-content")
