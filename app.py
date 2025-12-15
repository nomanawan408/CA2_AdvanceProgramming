"""
DBS Event Management System - Main Application
A simple Flask application for managing events at Dublin Business School
"""
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from models import db, User, Society, Event, Registration
from datetime import datetime
import os
from export_routes import export_registrations_csv, export_registrations_pdf

# Initialize Flask app 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dbs-event-system-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
 
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# Role-based access control decorators
def admin_required(f):
    """Decorator to require superadmin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'superadmin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def organizer_required(f):
    """Decorator to require organizer role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['superadmin', 'organizer']:
            flash('Access denied. Organizer privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator to require student role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied. Student account required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ============== PUBLIC ROUTES ==============

@app.route('/')
def index():
    """Public homepage with event listing"""
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('index.html', events=events)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for all users"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page for new students"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new student user
        user = User(name=name, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """Logout current user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Route users to their role-specific dashboard"""
    if current_user.role == 'superadmin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'organizer':
        return redirect(url_for('organizer_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))


# ============== ADMIN ROUTES ==============

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with system overview"""
    total_users = User.query.count()
    total_societies = Society.query.count()
    total_events = Event.query.count()
    total_registrations = Registration.query.count()
    
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_societies=total_societies,
                         total_events=total_events,
                         total_registrations=total_registrations,
                         recent_events=recent_events)


@app.route('/admin/organizers')
@admin_required
def admin_organizers():
    """List all organizers"""
    organizers = User.query.filter_by(role='organizer').all()
    return render_template('admin/organizers.html', organizers=organizers)


@app.route('/admin/add-organizer', methods=['GET', 'POST'])
@admin_required
def admin_add_organizer():
    """Add new organizer"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('admin/add_organizer.html')
        
        organizer = User(name=name, email=email, role='organizer')
        organizer.set_password(password)
        db.session.add(organizer)
        db.session.commit()
        
        flash(f'Organizer {name} added successfully', 'success')
        return redirect(url_for('admin_organizers'))
    
    return render_template('admin/add_organizer.html')


@app.route('/admin/societies')
@admin_required
def admin_societies():
    """List all societies"""
    societies = Society.query.all()
    return render_template('admin/societies.html', societies=societies)


@app.route('/admin/add-society', methods=['GET', 'POST'])
@admin_required
def admin_add_society():
    """Add new society"""
    organizers = User.query.filter_by(role='organizer').all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        society_head_id = request.form.get('society_head_id')
        
        if Society.query.filter_by(name=name).first():
            flash('Society name already exists', 'danger')
            return render_template('admin/add_society.html', organizers=organizers)
        
        society = Society(name=name, description=description, society_head_id=society_head_id)
        db.session.add(society)
        db.session.commit()
        
        flash(f'Society {name} added successfully', 'success')
        return redirect(url_for('admin_societies'))
    
    return render_template('admin/add_society.html', organizers=organizers)


@app.route('/admin/events')
@admin_required
def admin_events():
    """List all events"""
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('admin/events.html', events=events)


@app.route('/admin/add-event', methods=['GET', 'POST'])
@admin_required
def admin_add_event():
    """Add new standalone event (admin only)"""
    societies = Society.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        location = request.form.get('location')
        capacity = request.form.get('capacity')
        society_id = request.form.get('society_id')
        is_paid = request.form.get('is_paid') == 'on'
        cost = float(request.form.get('cost')) if is_paid else 0.0
        
        # Convert date string to datetime
        event_date_obj = datetime.strptime(event_date, '%Y-%m-%dT%H:%M')
        
        event = Event(
            title=title,
            description=description,
            event_date=event_date_obj,
            location=location,
            capacity=int(capacity),
            is_paid=is_paid,
            cost=cost,
            society_id=int(society_id) if society_id else None,
            created_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        
        flash(f'Event "{title}" created successfully', 'success')
        return redirect(url_for('admin_events'))
    
    return render_template('admin/add_event.html', societies=societies)


@app.route('/admin/delete-event/<int:event_id>')
@admin_required
def admin_delete_event(event_id):
    """Delete an event"""
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{event.title}" deleted successfully', 'success')
    return redirect(url_for('admin_events'))


# ============== ORGANIZER ROUTES ==============

@app.route('/organizer/dashboard')
@organizer_required
def organizer_dashboard():
    """Organizer dashboard"""
    # Get organizer's society
    society = Society.query.filter_by(society_head_id=current_user.id).first()
    
    # Get organizer's events
    my_events = Event.query.filter_by(created_by=current_user.id).order_by(Event.event_date.desc()).all()
    
    return render_template('organizer/dashboard.html', society=society, my_events=my_events)


@app.route('/organizer/add-event', methods=['GET', 'POST'])
@organizer_required
def organizer_add_event():
    """Add new event linked to organizer's society"""
    society = Society.query.filter_by(society_head_id=current_user.id).first()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        location = request.form.get('location')
        capacity = request.form.get('capacity')
        is_paid = request.form.get('is_paid') == 'on'
        cost = float(request.form.get('cost')) if is_paid else 0.0
        
        event_date_obj = datetime.strptime(event_date, '%Y-%m-%dT%H:%M')
        
        event = Event(
            title=title,
            description=description,
            event_date=event_date_obj,
            location=location,
            capacity=int(capacity),
            is_paid=is_paid,
            cost=cost,
            society_id=society.id if society else None,
            created_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        
        flash(f'Event "{title}" created successfully', 'success')
        return redirect(url_for('organizer_dashboard'))
    
    return render_template('organizer/add_event.html', society=society)


@app.route('/organizer/events')
@organizer_required
def organizer_events():
    """List organizer's events"""
    my_events = Event.query.filter_by(created_by=current_user.id).order_by(Event.event_date.desc()).all()
    return render_template('organizer/events.html', events=my_events)


# ============== STUDENT ROUTES ==============

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    """Student dashboard with their registrations"""
    my_registrations = Registration.query.filter_by(student_id=current_user.id).all()
    return render_template('student/dashboard.html', registrations=my_registrations)


@app.route('/event/<int:event_id>/register')
@app.route('/event/<int:event_id>/register', methods=['GET', 'POST'])
@login_required
def register_event(event_id):
    """Register for an event"""
    if current_user.role != 'student':
        flash('Only students can register for events', 'danger')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    
    # Check if already registered
    existing = Registration.query.filter_by(event_id=event_id, student_id=current_user.id).first()
    if existing:
        flash('You are already registered for this event', 'warning')
        return redirect(url_for('student_dashboard'))
    
    # Check capacity
    if event.is_full():
        flash('Sorry, this event is full', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        payment_method = request.form.get('payment_method')
        invoice_path = None
        
        # Handle file upload for online payment
        if payment_method == 'online' and 'invoice' in request.files:
            invoice_file = request.files['invoice']
            if invoice_file.filename != '':
                # Simple file save logic (intermediate level)
                upload_folder = os.path.join(app.root_path, 'static', 'invoices')
                os.makedirs(upload_folder, exist_ok=True)
                filename = f"{current_user.id}_{event_id}_{invoice_file.filename}"
                file_path = os.path.join(upload_folder, filename)
                invoice_file.save(file_path)
                invoice_path = os.path.join('static', 'invoices', filename)
        
        # Create registration
        registration = Registration(
            event_id=event_id, 
            student_id=current_user.id,
            phone_number=phone_number,
            payment_method=payment_method,
            invoice_path=invoice_path
        )
        db.session.add(registration)
        db.session.commit()
        
        flash(f'Successfully registered for "{event.title}"', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('register_event.html', event=event)


@app.route('/event/<int:event_id>/unregister')
@student_required
def unregister_event(event_id):
    """Unregister from an event"""
    registration = Registration.query.filter_by(event_id=event_id, student_id=current_user.id).first()
    
    if registration:
        db.session.delete(registration)
        db.session.commit()
        flash('Successfully unregistered from event', 'success')
    
    return redirect(url_for('student_dashboard'))


# ============== EXPORT ROUTES ==============

@app.route('/event/<int:event_id>/registrations')
@login_required
def view_registrations(event_id):
    """View registrations for an event (admin and organizers)"""
    if current_user.role not in ['superadmin', 'organizer']:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    
    # Check if organizer owns this event
    if current_user.role == 'organizer' and event.created_by != current_user.id:
        flash('You can only view registrations for your own events', 'danger')
        return redirect(url_for('organizer_dashboard'))
    
    registrations = Registration.query.filter_by(event_id=event_id).all()
    
    return render_template('registrations.html', event=event, registrations=registrations)


@app.route('/event/<int:event_id>/export/csv')
@login_required
def export_csv(event_id):
    """Export registrations as CSV"""
    if current_user.role not in ['superadmin', 'organizer']:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    
    # Check permissions
    if current_user.role == 'organizer' and event.created_by != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('organizer_dashboard'))
    
    return export_registrations_csv(event_id)


@app.route('/event/<int:event_id>/export/pdf')
@login_required
def export_pdf(event_id):
    """Export registrations as PDF"""
    if current_user.role not in ['superadmin', 'organizer']:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    event = Event.query.get_or_404(event_id)
    
    # Check permissions
    if current_user.role == 'organizer' and event.created_by != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('organizer_dashboard'))
    
    return export_registrations_pdf(event_id)


# ============== DATABASE INITIALIZATION ==============

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin exists
        if not User.query.filter_by(email='admin@dbs.ie').first():
            # Create superadmin
            admin = User(name='Super Admin', email='admin@dbs.ie', role='superadmin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample organizer
            organizer = User(name='John Organizer', email='organizer@dbs.ie', role='organizer')
            organizer.set_password('org123')
            db.session.add(organizer)
            
            # Create sample student
            student = User(name='Jane Student', email='student@dbs.ie', role='student')
            student.set_password('student123')
            db.session.add(student)
            
            db.session.commit()
            
            # Create sample society
            society = Society(
                name='Tech Society',
                description='Technology and Innovation Club',
                society_head_id=organizer.id
            )
            db.session.add(society)
            db.session.commit()
            
            # Create sample free event
            free_event = Event(
                title='Welcome Day 2025 (Free)',
                description='Welcome event for new students',
                event_date=datetime(2025, 1, 15, 10, 0),
                location='Main Hall',
                capacity=100,
                is_paid=False,
                cost=0.0,
                society_id=society.id,
                created_by=organizer.id
            )
            db.session.add(free_event)
            
            # Create sample paid event
            paid_event = Event(
                title='Cyber Security Workshop (Paid)',
                description='Advanced workshop on cyber security techniques.',
                event_date=datetime(2025, 2, 20, 14, 0),
                location='Lecture Theatre 1',
                capacity=30,
                is_paid=True,
                cost=25.00,
                society_id=society.id,
                created_by=organizer.id
            )
            db.session.add(paid_event)
            db.session.commit()
            
            print("Database initialized with sample data")
            print("Admin: admin@dbs.ie / admin123")
            print("Organizer: organizer@dbs.ie / org123")
            print("Student: student@dbs.ie / student123")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
