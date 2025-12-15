from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from models import User, Event


public_bp = Blueprint("public", __name__)


@public_bp.route("/", endpoint="index")
def index():
    """Public homepage with event listing"""
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
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return render_template("register.html")

        # Create new student user
        user = User(name=name, email=email, role="student")
        user.set_password(password)
        # db session commit is handled in main app context
        from models import db

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
