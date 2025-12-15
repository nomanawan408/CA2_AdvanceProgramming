from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Decorator to require superadmin role"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "superadmin":
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("public.index"))
        return f(*args, **kwargs)

    return decorated_function


def organizer_required(f):
    """Decorator to require organizer role"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in [
            "superadmin",
            "organizer",
        ]:
            flash("Access denied. Organizer privileges required.", "danger")
            return redirect(url_for("public.index"))
        return f(*args, **kwargs)

    return decorated_function


def student_required(f):
    """Decorator to require student role"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "student":
            flash("Access denied. Student account required.", "danger")
            return redirect(url_for("public.index"))
        return f(*args, **kwargs)

    return decorated_function
