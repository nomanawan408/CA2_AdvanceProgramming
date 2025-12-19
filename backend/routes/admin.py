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


@admin_bp.route("/admin/add-student", methods=["GET", "POST"], endpoint="admin_add_student")
@admin_required
def admin_add_student():
    """Add new student"""
    if request.method == "POST":
        student_number = request.form.get("student_number")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return render_template("admin/add_student.html")

        if User.query.filter_by(student_number=student_number).first():
            flash("Student ID already exists", "danger")
            return render_template("admin/add_student.html")

        student = User(student_number=student_number, name=name, email=email, role="student")
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash(f"Student {name} added successfully", "success")
        return redirect(url_for("admin.admin_students"))

    return render_template("admin/add_student.html")


@admin_bp.route("/admin/edit-student/<int:student_id>", methods=["GET", "POST"], endpoint="admin_edit_student")
@admin_required
def admin_edit_student(student_id):
    """Edit existing student"""
    student = User.query.get_or_404(student_id)
    
    if student.role != "student":
        flash("User is not a student", "danger")
        return redirect(url_for("admin.admin_students"))

    if request.method == "POST":
        student_number = request.form.get("student_number")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if email exists for another user
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != student_id:
            flash("Email already exists", "danger")
            return render_template("admin/edit_student.html", student=student)

        # Check if student number exists for another user
        existing_student = User.query.filter_by(student_number=student_number).first()
        if existing_student and existing_student.id != student_id:
            flash("Student ID already exists", "danger")
            return render_template("admin/edit_student.html", student=student)

        student.student_number = student_number
        student.name = name
        student.email = email
        
        if password and password.strip():
            student.set_password(password)
        
        db.session.commit()
        flash(f"Student {name} updated successfully", "success")
        return redirect(url_for("admin.admin_students"))

    return render_template("admin/edit_student.html", student=student)


@admin_bp.route("/admin/delete-student/<int:student_id>", methods=["POST"], endpoint="admin_delete_student")
@admin_required
def admin_delete_student(student_id):
    """Delete a student"""
    student = User.query.get_or_404(student_id)
    
    if student.role != "student":
        flash("User is not a student", "danger")
        return redirect(url_for("admin.admin_students"))
    
    db.session.delete(student)
    db.session.commit()
    flash(f"Student {student.name} deleted successfully", "success")
    return redirect(url_for("admin.admin_students"))


@admin_bp.route("/admin/add-admin", methods=["GET", "POST"], endpoint="admin_add_admin")
@admin_required
def admin_add_admin():
    """Add new admin (superadmin only)"""
    # Only allow superadmin to create new admins
    if current_user.role != "superadmin":
        flash("Access denied. Only superadmin can create new admins.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return render_template("admin/add_admin.html")

        admin = User(name=name, email=email, role="superadmin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        flash(f"Admin {name} added successfully", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin/add_admin.html")


@admin_bp.route("/admin/organizers", endpoint="admin_organizers")
@admin_required
def admin_organizers():
    """List all organizers"""
    organizers = User.query.filter_by(role="organizer").all()
    return render_template("admin/organizers.html", organizers=organizers)


@admin_bp.route("/admin/edit-organizer/<int:organizer_id>", methods=["GET", "POST"], endpoint="admin_edit_organizer")
@admin_required
def admin_edit_organizer(organizer_id):
    """Edit existing organizer"""
    organizer = User.query.get_or_404(organizer_id)
    
    if organizer.role != "organizer":
        flash("User is not an organizer", "danger")
        return redirect(url_for("admin.admin_organizers"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if email exists for another user
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != organizer_id:
            flash("Email already exists", "danger")
            return render_template("admin/edit_organizer.html", organizer=organizer)

        organizer.name = name
        organizer.email = email
        
        if password and password.strip():
            organizer.set_password(password)
        
        db.session.commit()
        flash(f"Organizer {name} updated successfully", "success")
        return redirect(url_for("admin.admin_organizers"))

    return render_template("admin/edit_organizer.html", organizer=organizer)


@admin_bp.route("/admin/delete-organizer/<int:organizer_id>", methods=["POST"], endpoint="admin_delete_organizer")
@admin_required
def admin_delete_organizer(organizer_id):
    """Delete an organizer"""
    organizer = User.query.get_or_404(organizer_id)
    
    if organizer.role != "organizer":
        flash("User is not an organizer", "danger")
        return redirect(url_for("admin.admin_organizers"))
    
    # Check if organizer is head of any society
    societies = Society.query.filter_by(society_head_id=organizer_id).all()
    if societies:
        flash(f"Cannot delete organizer {organizer.name}. They are head of {len(societies)} society(ies).", "danger")
        return redirect(url_for("admin.admin_organizers"))
    
    db.session.delete(organizer)
    db.session.commit()
    flash(f"Organizer {organizer.name} deleted successfully", "success")
    return redirect(url_for("admin.admin_organizers"))


@admin_bp.route("/admin/students", endpoint="admin_students")
@admin_required
def admin_students():
    """List all students"""
    students = User.query.filter_by(role="student").all()
    return render_template("admin/students.html", students=students)


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


@admin_bp.route("/admin/edit-society/<int:society_id>", methods=["GET", "POST"], endpoint="admin_edit_society")
@admin_required
def admin_edit_society(society_id):
    """Edit existing society"""
    society = Society.query.get_or_404(society_id)
    organizers = User.query.filter_by(role="organizer").all()

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        society_head_id = request.form.get("society_head_id")

        # Check if society name exists for another society
        existing_society = Society.query.filter_by(name=name).first()
        if existing_society and existing_society.id != society_id:
            flash("Society name already exists", "danger")
            return render_template("admin/edit_society.html", society=society, organizers=organizers)

        society.name = name
        society.description = description
        society.society_head_id = int(society_head_id) if society_head_id else None
        
        db.session.commit()
        flash(f"Society {name} updated successfully", "success")
        return redirect(url_for("admin.admin_societies"))

    return render_template("admin/edit_society.html", society=society, organizers=organizers)


@admin_bp.route("/admin/delete-society/<int:society_id>", methods=["POST"], endpoint="admin_delete_society")
@admin_required
def admin_delete_society(society_id):
    """Delete a society"""
    society = Society.query.get_or_404(society_id)
    
    # Check if society has events
    events = Event.query.filter_by(society_id=society_id).all()
    if events:
        flash(f"Cannot delete society {society.name}. It has {len(events)} associated event(s).", "danger")
        return redirect(url_for("admin.admin_societies"))
    
    db.session.delete(society)
    db.session.commit()
    flash(f"Society {society.name} deleted successfully", "success")
    return redirect(url_for("admin.admin_societies"))


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


@admin_bp.route("/admin/edit-event/<int:event_id>", methods=["GET", "POST"], endpoint="admin_edit_event")
@admin_required
def admin_edit_event(event_id):
    """Edit existing event"""
    event = Event.query.get_or_404(event_id)
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

        # Check if new capacity is less than current registrations
        if int(capacity) < len(event.registrations):
            flash(f"Cannot reduce capacity to {capacity}. Event already has {len(event.registrations)} registrations.", "danger")
            return render_template("admin/edit_event.html", event=event, societies=societies)

        # Convert date string to datetime
        event_date_obj = datetime.strptime(event_date, "%Y-%m-%dT%H:%M")

        event.title = title
        event.description = description
        event.event_date = event_date_obj
        event.location = location
        event.capacity = int(capacity)
        event.is_paid = is_paid
        event.cost = cost
        event.society_id = int(society_id) if society_id else None
        
        db.session.commit()
        flash(f'Event "{title}" updated successfully', "success")
        return redirect(url_for("admin.admin_events"))

    return render_template("admin/edit_event.html", event=event, societies=societies)


@admin_bp.route("/admin/delete-event/<int:event_id>", methods=["POST"], endpoint="admin_delete_event")
@admin_required
def admin_delete_event(event_id):
    """Delete an event"""
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{event.title}" deleted successfully', "success")
    return redirect(url_for("admin.admin_events"))
