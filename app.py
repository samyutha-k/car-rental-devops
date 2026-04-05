from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, init_db
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from flask import Response
from models import User, Vehicle, Reservation
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import logging
import uuid
import secrets

# ✅ ADDED (Prometheus fix)
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db(app)

# =========================
# HELPER FUNCTIONS
# =========================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_vehicle_available(vehicle_id, start_date, end_date):
    if start_date >= end_date:
        return False
    reservations = Reservation.query.filter_by(vehicle_id=vehicle_id).all()
    for res in reservations:
        if not (end_date < res.start_date or start_date > res.end_date):
            return False
    return True

# =========================
# ROUTES
# =========================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def index_alias():
    return redirect(url_for('index'))

@app.route('/index.html')
def index_html():
    return redirect(url_for('index'))

@app.route('/catalog.html')
def catalog_html():
    return redirect(url_for('catalog'))

@app.route('/profile.html')
def profile_html():
    return redirect(url_for('profile'))

@app.route('/owner_dashboard.html')
def owner_dashboard_html():
    return redirect(url_for('owner_dashboard'))

@app.route('/owner_homepage.html')
def owner_homepage_html():
    return redirect(url_for('owner_homepage'))

@app.route('/admin.html')
def admin_html():
    return redirect(url_for('admin'))

@app.route('/login.html')
def login_html():
    return redirect(url_for('login'))

@app.route('/signup.html')
def signup_html():
    return redirect(url_for('signup'))

@app.route('/reservation.html')
def reservation_html():
    return redirect(url_for('index'))

# =========================
# AUTH
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user_type = request.form.get('user_type', 'customer').strip()

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if user.user_type == user_type or user.is_admin:
                session['user_id'] = user.id
                session['user_type'] = user.user_type
                session['is_admin'] = user.is_admin
                flash('Login successful!', 'success')

                if user.is_admin:
                    return redirect(url_for('admin'))
                if user_type == 'customer':
                    return redirect(url_for('catalog'))
                elif user_type == 'owner':
                    return redirect(url_for('owner_homepage'))
            else:
                flash('Incorrect user type.', 'error')
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user_type = request.form.get('user_type', 'customer').strip()

        if len(username) < 3 or len(password) < 6:
            flash('Username must be at least 3 chars and password 6 chars.', 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        else:
            user = User(username=username, user_type=user_type)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

# =========================
# USER FEATURES
# =========================

@app.route('/catalog')
def catalog():
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    vehicles = Vehicle.query.filter_by(available=True).all()
    return render_template('catalog.html', vehicles=vehicles)

# =========================
# OWNER FEATURES
# =========================

@app.route('/owner_homepage')
def owner_homepage():
    if session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    vehicles = Vehicle.query.filter_by(owner_id=session['user_id']).all()
    return render_template('owner_homepage.html', vehicles=vehicles)

@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    if request.method == 'POST':
        make = request.form['make'].strip()
        model = request.form['model'].strip()
        year = int(request.form['year'])
        price_per_day = float(request.form['price_per_day'])
        phone_number = request.form['phone_number'].strip()
        images = 'placeholder'

        if 'images' in request.files:
            image_file = request.files['images']
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                images = filename

        vehicle = Vehicle(
            make=make,
            model=model,
            year=year,
            price_per_day=price_per_day,
            owner_id=session['user_id'],
            available=True,
            phone_number=phone_number,
            images=images,
        )
        db.session.add(vehicle)
        db.session.commit()
        flash('Vehicle added successfully.', 'success')
        return redirect(url_for('owner_homepage'))

    return render_template('add_vehicle.html')

@app.route('/owner_dashboard')
def owner_dashboard():
    if session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    vehicles = Vehicle.query.filter_by(owner_id=session['user_id']).all()
    vehicle_reservations = []

    for vehicle in vehicles:
        reservations = Reservation.query.filter_by(vehicle_id=vehicle.id).all()
        reservation_list = []
        for reservation in reservations:
            customer = User.query.get(reservation.user_id)
            reservation_list.append({
                'customer_username': customer.username if customer else 'Unknown',
                'start_date': reservation.start_date.strftime('%Y-%m-%d'),
                'end_date': reservation.end_date.strftime('%Y-%m-%d'),
                'total_cost': reservation.total_cost,
            })

        vehicle_reservations.append({
            'vehicle': vehicle,
            'reservations': reservation_list,
        })

    return render_template('owner_dashboard.html', vehicle_reservations=vehicle_reservations, edit_vehicle=None)

@app.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    if session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != session['user_id']:
        flash('You do not have permission to edit this vehicle.', 'error')
        return redirect(url_for('owner_dashboard'))

    if request.method == 'POST':
        vehicle.make = request.form['make'].strip()
        vehicle.model = request.form['model'].strip()
        vehicle.year = int(request.form['year'])
        vehicle.price_per_day = float(request.form['price_per_day'])
        vehicle.phone_number = request.form['phone_number'].strip()

        if 'images' in request.files:
            image_file = request.files['images']
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                vehicle.images = filename

        db.session.commit()
        flash('Vehicle updated successfully.', 'success')
        return redirect(url_for('owner_dashboard'))

    vehicles = Vehicle.query.filter_by(owner_id=session['user_id']).all()
    vehicle_reservations = []
    for item in vehicles:
        reservations = Reservation.query.filter_by(vehicle_id=item.id).all()
        reservation_list = []
        for reservation in reservations:
            customer = User.query.get(reservation.user_id)
            reservation_list.append({
                'customer_username': customer.username if customer else 'Unknown',
                'start_date': reservation.start_date.strftime('%Y-%m-%d'),
                'end_date': reservation.end_date.strftime('%Y-%m-%d'),
                'total_cost': reservation.total_cost,
            })
        vehicle_reservations.append({'vehicle': item, 'reservations': reservation_list})

    return render_template('owner_dashboard.html', vehicle_reservations=vehicle_reservations, edit_vehicle=vehicle)

@app.route('/remove_vehicle/<int:vehicle_id>', methods=['POST'])
def remove_vehicle(vehicle_id):
    if session.get('user_type') != 'owner':
        return redirect(url_for('login'))

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != session['user_id']:
        flash('You do not have permission to remove this vehicle.', 'error')
        return redirect(url_for('owner_dashboard'))

    db.session.delete(vehicle)
    db.session.commit()
    flash('Vehicle removed successfully.', 'success')
    return redirect(url_for('owner_dashboard'))

@app.route('/reserve/<int:vehicle_id>', methods=['GET', 'POST'])
def reserve(vehicle_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('Please login as a customer first.', 'error')
        return redirect(url_for('login'))

    vehicle = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        except ValueError:
            flash('Please enter valid dates.', 'error')
            return redirect(url_for('reserve', vehicle_id=vehicle_id))

        if start_date >= end_date:
            flash('End date must be after the start date.', 'error')
            return redirect(url_for('reserve', vehicle_id=vehicle_id))

        if not is_vehicle_available(vehicle_id, start_date, end_date):
            flash('Vehicle is not available for the selected dates.', 'error')
            return redirect(url_for('reserve', vehicle_id=vehicle_id))

        total_days = (end_date - start_date).days
        total_cost = total_days * vehicle.price_per_day

        reservation = Reservation(
            user_id=session['user_id'],
            vehicle_id=vehicle.id,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost,
        )
        db.session.add(reservation)
        db.session.commit()

        flash('Reservation confirmed!', 'success')
        return redirect(url_for('profile'))

    return render_template('reservation.html', vehicle=vehicle, today=datetime.utcnow().strftime('%Y-%m-%d'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    reservations = Reservation.query.filter_by(user_id=session['user_id']).all()
    reserved_vehicles = []
    today = datetime.utcnow().date()

    for reservation in reservations:
        vehicle = Vehicle.query.get(reservation.vehicle_id)
        if not vehicle:
            continue

        reserved_vehicles.append({
            'reservation_id': reservation.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'price_per_day': vehicle.price_per_day,
            'phone_number': vehicle.phone_number,
            'image': vehicle.image,
            'start_date': reservation.start_date.strftime('%Y-%m-%d'),
            'end_date': reservation.end_date.strftime('%Y-%m-%d'),
            'total_cost': reservation.total_cost,
            'is_upcoming': reservation.end_date >= today,
        })

    return render_template('profile.html', reserved_vehicles=reserved_vehicles)

@app.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != session['user_id']:
        flash('You do not have permission to cancel this reservation.', 'error')
        return redirect(url_for('profile'))

    db.session.delete(reservation)
    db.session.commit()
    flash('Reservation canceled successfully.', 'success')
    return redirect(url_for('profile'))

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    vehicles = Vehicle.query.all()
    reservations = Reservation.query.all()
    return render_template('admin.html', vehicles=vehicles, reservations=reservations)

# =========================
# PROMETHEUS METRICS (FIX)
# =========================

@app.route('/metrics')
def metrics():
     return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# =========================
# RUN
# =========================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)