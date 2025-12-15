import os

from models import db, Event, Registration, User


def test_student_paid_event_register_uploads_invoice(app, login_student, sample_invoice_bytes):
    with app.app_context():
        event = Event.query.filter_by(is_paid=True).first()
        assert event is not None

    data = {
        "phone_number": "123456",
        "payment_method": "online",
        "invoice": (sample_invoice_bytes, "invoice.png"),
    }

    resp = login_student.post(
        f"/event/{event.id}/register",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=False,
    )

    # Successful registration redirects to student dashboard
    assert resp.status_code in (301, 302)

    with app.app_context():
        student = User.query.filter_by(role="student").first()
        reg = Registration.query.filter_by(event_id=event.id, student_id=student.id).first()
        assert reg is not None
        assert reg.invoice_path is not None

        # Verify file exists in isolated static/invoices folder
        filename = reg.invoice_path.split("/")[-1]
        invoices_dir = os.path.join(app.static_folder, "invoices")
        assert os.path.exists(os.path.join(invoices_dir, filename))
