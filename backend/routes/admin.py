from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from backend.decorators import admin_required
from models import db, Event, Society, User, Registration


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/dashboard", endpoint="admin_dashboard")
@admin_required
def admin_dashboard():
    """Admin dashboard with system overview"""
    total_users = User.query.count()
    total_societies = Society.query.count()
    total_events = Event.query.count()
    total_registrations = Registration.query.count()

    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_societies=total_societies,
        total_events=total_events,
        total_registrations=total_registrations,
        recent_events=recent_events,
    )


@admin_bp.route("/admin/organizers", endpoint="admin_organizers")
@admin_required
def admin_organizers():
    """List all organizers"""
    organizers = User.query.filter_by(role="organizer").all()
    return render_template("admin/organizers.html", organizers=organizers)


@admin_bp.route("/admin/add-organizer", methods=["GET", "POST"], endpoint="admin_add_organizer")
@admin_required
def admin_add_organizer():
    """Add new organizer"""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return render_template("admin/add_organizer.html")

        organizer = User(name=name, email=email, role="organizer")
        organizer.set_password(password)
        db.session.add(organizer)
        db.session.commit()

        flash(f"Organizer {name} added successfully", "success")
        return redirect(url_for("admin.admin_organizers"))

    return render_template("admin/add_organizer.html")


@admin_bp.route("/admin/societies", endpoint="admin_societies")
@admin_required
def admin_societies():
    """List all societies"""
    societies = Society.query.all()
    return render_template("admin/societies.html", societies=societies)


@admin_bp.route("/admin/add-society", methods=["GET", "POST"], endpoint="admin_add_society")
@admin_required
def admin_add_society():
    """Add new society"""
    organizers = User.query.filter_by(role="organizer").all()

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        society_head_id = request.form.get("society_head_id")

        if Society.query.filter_by(name=name).first():
            flash("Society name already exists", "danger")
            return render_template("admin/add_society.html", organizers=organizers)

        society = Society(
            name=name,
            description=description,
            society_head_id=society_head_id,
        )
        db.session.add(society)
        db.session.commit()

        flash(f"Society {name} added successfully", "success")
        return redirect(url_for("admin.admin_societies"))

    return render_template("admin/add_society.html", organizers=organizers)


@admin_bp.route("/admin/events", endpoint="admin_events")
@admin_required
def admin_events():
    """List all events"""
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template("admin/events.html", events=events)


@admin_bp.route("/admin/add-event", methods=["GET", "POST"], endpoint="admin_add_event")
@admin_required
def admin_add_event():
    """Add new standalone event (admin only)"""
    societies = Society.query.all()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        event_date = request.form.get("event_date")
        location = request.form.get("location")
        capacity = request.form.get("capacity")
        society_id = request.form.get("society_id")
        is_paid = request.form.get("is_paid") == "on"
        cost = float(request.form.get("cost")) if is_paid else 0.0

        # Convert date string to datetime
        event_date_obj = datetime.strptime(event_date, "%Y-%m-%dT%H:%M")

        event = Event(
            title=title,
            description=description,
            event_date=event_date_obj,
            location=location,
            capacity=int(capacity),
            is_paid=is_paid,
            cost=cost,
            society_id=int(society_id) if society_id else None,
            created_by=current_user.id,
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Event "{title}" created successfully', "success")
        return redirect(url_for("admin.admin_events"))

    return render_template("admin/add_event.html", societies=societies)


@admin_bp.route("/admin/delete-event/<int:event_id>", endpoint="admin_delete_event")
@admin_required
def admin_delete_event(event_id):
    """Delete an event"""
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{event.title}" deleted successfully', "success")
    return redirect(url_for("admin.admin_events"))
