from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Changed to store hashed password
    user_type = db.Column(db.String(20), nullable=False, default='customer')
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    available = db.Column(db.Boolean, default=True)
    phone_number = db.Column(db.String(20), nullable=False)
    images = db.Column(db.String(200), nullable=True, default='placeholder')  # Allow null, default to 'placeholder'

    @property
    def image(self):
        if not self.images or self.images == 'placeholder':
            return 'vehicle-placeholder.svg'
        return self.images.split(',')[0].strip()

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)