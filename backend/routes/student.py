import os

from datetime import datetime
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from backend.decorators import student_required
from models import Event, Registration, Society


student_bp = Blueprint("student", __name__)


@student_bp.route("/student/dashboard", endpoint="student_dashboard")
@student_required
def student_dashboard():
    """Student dashboard with their registrations"""
    my_registrations = Registration.query.filter_by(student_id=current_user.id).all()
    return render_template("student/dashboard.html", registrations=my_registrations)


@student_bp.route("/event/<int:event_id>/register", methods=["GET", "POST"], endpoint="register_event")
@login_required
def register_event(event_id):
    """Register for an event"""
    if current_user.role != "student":
        flash("Only students can register for events", "danger")
        return redirect(url_for("public.index"))

    event = Event.query.get_or_404(event_id)

    # Check if already registered
    existing = Registration.query.filter_by(
        event_id=event_id, student_id=current_user.id
    ).first()
    if existing:
        flash("You are already registered for this event", "warning")
        return redirect(url_for("student.student_dashboard"))

    # Check capacity
    if event.is_full():
        flash("Sorry, this event is full", "danger")
        return redirect(url_for("public.index"))

    if request.method == "POST":
        phone_number = request.form.get("phone_number")
        payment_method = request.form.get("payment_method")
        invoice_path = None

        # Validate phone number
        if not phone_number or phone_number.strip() == "":
            flash("Phone number is required", "danger")
            return redirect(url_for("student.register_event", event_id=event_id))

        # Validate payment method for paid events
        if event.is_paid and not payment_method:
            flash("Payment method is required for paid events", "danger")
            return redirect(url_for("student.register_event", event_id=event_id))

        # Handle file upload for online payment
        if payment_method == "online" and "invoice" in request.files:
            invoice_file = request.files["invoice"]
            if invoice_file.filename != "":
                try:
                    upload_folder = os.path.join(current_app.static_folder, "invoices")
                    os.makedirs(upload_folder, exist_ok=True)
                    filename = f"{current_user.id}_{event_id}_{invoice_file.filename}"
                    file_path = os.path.join(upload_folder, filename)
                    invoice_file.save(file_path)
                    invoice_path = os.path.join("static", "invoices", filename)
                except Exception as e:
                    flash(f"Error uploading invoice: {str(e)}", "danger")
                    return redirect(url_for("student.register_event", event_id=event_id))
            else:
                flash("Invoice file is required for online payment", "danger")
                return redirect(url_for("student.register_event", event_id=event_id))

        # Create registration
        registration = Registration(
            event_id=event_id,
            student_id=current_user.id,
            phone_number=phone_number,
            payment_method=payment_method,
            invoice_path=invoice_path,
        )
        from models import db

        db.session.add(registration)
        db.session.commit()

        flash(f'Successfully registered for "{event.title}"', "success")
        return redirect(url_for("student.student_dashboard"))

    return render_template("register_event.html", event=event)


@student_bp.route("/event/<int:event_id>/unregister", endpoint="unregister_event")
@student_required
def unregister_event(event_id):
    """Unregister from an event"""
    registration = Registration.query.filter_by(
        event_id=event_id, student_id=current_user.id
    ).first()

    if registration:
        from models import db

        db.session.delete(registration)
        db.session.commit()
        flash("Successfully unregistered from event", "success")

    return redirect(url_for("student.student_dashboard"))


@student_bp.route("/student/events", endpoint="browse_events")
@student_required
def browse_events():
    """Browse all available events"""
    # Get all upcoming events that the student hasn't registered for yet
    registered_event_ids = [r.event_id for r in 
                         Registration.query.filter_by(student_id=current_user.id).all()]
    
    # Get upcoming events (excluding past events)
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date.asc()).all()
    
    # Separate events into registered and available
    registered_events = [e for e in upcoming_events if e.id in registered_event_ids]
    available_events = [e for e in upcoming_events if e.id not in registered_event_ids]
    
    return render_template(
        "student/browse_events.html",
        available_events=available_events,
        registered_events=registered_events
    )
