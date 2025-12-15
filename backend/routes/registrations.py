from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from models import Event, Registration


registrations_bp = Blueprint("registrations", __name__)


@registrations_bp.route("/event/<int:event_id>/registrations", endpoint="view_registrations")
@login_required
def view_registrations(event_id):
    """View registrations for an event (admin and organizers)"""
    if current_user.role not in ["superadmin", "organizer"]:
        flash("Access denied", "danger")
        return redirect(url_for("public.index"))

    event = Event.query.get_or_404(event_id)

    # Check if organizer owns this event
    if current_user.role == "organizer" and event.created_by != current_user.id:
        flash("You can only view registrations for your own events", "danger")
        return redirect(url_for("organizer.organizer_dashboard"))

    registrations = Registration.query.filter_by(event_id=event_id).all()

    return render_template("registrations.html", event=event, registrations=registrations)
