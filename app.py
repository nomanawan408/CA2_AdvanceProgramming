"""Entry point for DBS Event Management System.

Delegates to the real Flask application defined in backend.main.
Run this file with `python app.py` during development.
"""

from backend.main import app, init_db
  

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
