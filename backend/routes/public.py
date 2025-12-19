from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from models import db, User, Event


public_bp = Blueprint("public", __name__)


@public_bp.route("/setup", methods=["GET", "POST"], endpoint="setup")
def setup():
    """Initial setup page for creating first admin when database is empty"""
    # Check if any users already exist
    if User.query.first():
        flash("Setup already completed. Please login.", "info")
        return redirect(url_for("public.login"))
    
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash("All fields are required", "danger")
            return render_template("setup.html")
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("setup.html")
        
        if len(password) < 6:
            flash("Password must be at least 6 characters", "danger")
            return render_template("setup.html")
        
        # Create first admin
        admin = User(name=name, email=email, role="superadmin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        
        flash("Admin account created successfully! Please login.", "success")
        return redirect(url_for("public.login"))
    
    return render_template("setup.html")


@public_bp.route("/", endpoint="index")
def index():
    """Public homepage with role-based redirection"""
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.role == "superadmin":
            return redirect(url_for("admin.admin_dashboard"))
        elif current_user.role == "organizer":
            return redirect(url_for("organizer.organizer_dashboard"))
        elif current_user.role == "student":
            return redirect(url_for("student.student_dashboard"))
        else:
            # Fallback to public dashboard if role is unknown
            return redirect(url_for("public.dashboard"))
    
    # Show public homepage for non-authenticated users
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template("index.html", events=events)


@public_bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    """Login page for all users"""
    if current_user.is_authenticated:
        return redirect(url_for("public.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("public.dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")


@public_bp.route("/register", methods=["GET", "POST"], endpoint="register")
def register():
    """Registration page for new students"""
    if current_user.is_authenticated:
        return redirect(url_for("public.dashboard"))

    if request.method == "POST":
        student_number = request.form.get("student_number")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not student_number or student_number.strip() == "":
            flash("Student ID is required", "danger")
            return render_template("register.html")

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return render_template("register.html")

        if User.query.filter_by(student_number=student_number).first():
            flash("Student ID already registered", "danger")
            return render_template("register.html")

        # Create new student user
        user = User(student_number=student_number, name=name, email=email, role="student")
        user.set_password(password)
        # db session commit is handled in main app context
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("public.login"))

    return render_template("register.html")


@public_bp.route("/logout", endpoint="logout")
@login_required
def logout():
    """Logout current user"""
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("public.index"))


@public_bp.route("/dashboard", endpoint="dashboard")
@login_required
def dashboard():
    """Route users to their role-specific dashboard"""
    if current_user.role == "superadmin":
        return redirect(url_for("admin.admin_dashboard"))
    elif current_user.role == "organizer":
        return redirect(url_for("organizer.organizer_dashboard"))
    else:
        return redirect(url_for("student.student_dashboard"))
