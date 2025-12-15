"""Backend package for DBS Event Management System.

Exposes the Flask application instance and database initialization helper.
"""

from .main import app, init_db  # noqa: F401
