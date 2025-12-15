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


@organizer_bp.route("/organizer/events", endpoint="organizer_events")
@organizer_required
def organizer_events():
    """List organizer's events"""
    my_events = Event.query.filter_by(created_by=current_user.id).order_by(
        Event.event_date.desc()
    ).all()
    return render_template("organizer/events.html", events=my_events)
