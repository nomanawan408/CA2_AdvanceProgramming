from flask import Blueprint, flash, redirect, url_for
from flask_login import current_user, login_required

from export_routes import export_registrations_csv, export_registrations_pdf
from models import Event


exports_bp = Blueprint("exports", __name__)


@exports_bp.route("/event/<int:event_id>/export/csv", endpoint="export_csv")
@login_required
def export_csv(event_id):
    """Export registrations as CSV"""
    if current_user.role not in ["superadmin", "organizer"]:
        flash("Access denied", "danger")
        return redirect(url_for("public.index"))

    event = Event.query.get_or_404(event_id)

    # Check permissions
    if current_user.role == "organizer" and event.created_by != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for("organizer.organizer_dashboard"))

    return export_registrations_csv(event_id)


@exports_bp.route("/event/<int:event_id>/export/pdf", endpoint="export_pdf")
@login_required
def export_pdf(event_id):
    """Export registrations as PDF"""
    if current_user.role not in ["superadmin", "organizer"]:
        flash("Access denied", "danger")
        return redirect(url_for("public.index"))

    event = Event.query.get_or_404(event_id)

    # Check permissions
    if current_user.role == "organizer" and event.created_by != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for("organizer.organizer_dashboard"))

    return export_registrations_pdf(event_id)
