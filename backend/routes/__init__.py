"""Blueprint registrations for the DBS Event Management System backend."""

from .public import public_bp
from .admin import admin_bp
from .organizer import organizer_bp
from .student import student_bp
from .exports import exports_bp
from .registrations import registrations_bp

__all__ = [
    "public_bp",
    "admin_bp",
    "organizer_bp",
    "student_bp",
    "exports_bp",
    "registrations_bp",
]
