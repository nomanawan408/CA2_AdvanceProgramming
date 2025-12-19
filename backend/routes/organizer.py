from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from backend.decorators import organizer_required
from models import db, Event, Society


organizer_bp = Blueprint("organizer", __name__)


@organizer_bp.route("/organizer/dashboard", endpoint="organizer_dashboard")
@organizer_required
def organizer_dashboard():
    """Organizer dashboard"""
    # Get organizer's society
    society = Society.query.filter_by(society_head_id=current_user.id).first()

    # Get organizer's events
    my_events = Event.query.filter_by(created_by=current_user.id).order_by(
        Event.event_date.desc()
    ).all()

    return render_template("organizer/dashboard.html", society=society, my_events=my_events)


@organizer_bp.route("/organizer/add-event", methods=["GET", "POST"], endpoint="organizer_add_event")
@organizer_required
def organizer_add_event():
    """Add new event linked to organizer's society"""
    society = Society.query.filter_by(society_head_id=current_user.id).first()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        event_date = request.form.get("event_date")
        location = request.form.get("location")
        capacity = request.form.get("capacity")
        is_paid = request.form.get("is_paid") == "on"
        cost = float(request.form.get("cost")) if is_paid else 0.0

        event_date_obj = datetime.strptime(event_date, "%Y-%m-%dT%H:%M")

        event = Event(
            title=title,
            description=description,
            event_date=event_date_obj,
            location=location,
            capacity=int(capacity),
            is_paid=is_paid,
            cost=cost,
            society_id=society.id if society else None,
            created_by=current_user.id,
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Event "{title}" created successfully', "success")
        return redirect(url_for("organizer.organizer_dashboard"))

    return render_template("organizer/add_event.html", society=society)


@organizer_bp.route("/organizer/edit-event/<int:event_id>", methods=["GET", "POST"], endpoint="organizer_edit_event")
@organizer_required
def organizer_edit_event(event_id):
    """Edit existing event (organizer only for their own events)"""
    event = Event.query.get_or_404(event_id)
    
    # Check if event belongs to current organizer
    if event.created_by != current_user.id:
        flash("Access denied. You can only edit your own events.", "danger")
        return redirect(url_for("organizer.organizer_events"))
    
    society = Society.query.filter_by(society_head_id=current_user.id).first()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        event_date = request.form.get("event_date")
        location = request.form.get("location")
        capacity = request.form.get("capacity")
        is_paid = request.form.get("is_paid") == "on"
        cost = float(request.form.get("cost")) if is_paid else 0.0

        # Check if new capacity is less than current registrations
        if int(capacity) < len(event.registrations):
            flash(f"Cannot reduce capacity to {capacity}. Event already has {len(event.registrations)} registrations.", "danger")
            return render_template("organizer/edit_event.html", event=event, society=society)

        event_date_obj = datetime.strptime(event_date, "%Y-%m-%dT%H:%M")

        event.title = title
        event.description = description
        event.event_date = event_date_obj
        event.location = location
        event.capacity = int(capacity)
        event.is_paid = is_paid
        event.cost = cost
        
        db.session.commit()
        flash(f'Event "{title}" updated successfully', "success")
        return redirect(url_for("organizer.organizer_events"))

    return render_template("organizer/edit_event.html", event=event, society=society)


@organizer_bp.route("/organizer/delete-event/<int:event_id>", methods=["POST"], endpoint="organizer_delete_event")
@organizer_required
def organizer_delete_event(event_id):
    """Delete an event (organizer only for their own events)"""
    event = Event.query.get_or_404(event_id)
    
    # Check if event belongs to current organizer
    if event.created_by != current_user.id:
        flash("Access denied. You can only delete your own events.", "danger")
        return redirect(url_for("organizer.organizer_events"))
    
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{event.title}" deleted successfully', "success")
    return redirect(url_for("organizer.organizer_events"))


@organizer_bp.route("/organizer/events", endpoint="organizer_events")
@organizer_required
def organizer_events():
    """List organizer's events"""
    my_events = Event.query.filter_by(created_by=current_user.id).order_by(
        Event.event_date.desc()
    ).all()
    return render_template("organizer/events.html", events=my_events)
