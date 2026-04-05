from flask_sqlalchemy import SQLAlchemy

import os
import json

db = SQLAlchemy()

def init_db(app):
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicle_rental.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

        from models import User, Vehicle

        has_owner = User.query.filter_by(user_type='owner').first()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', user_type='admin', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
        if not has_owner:
            owner = User(username='owner', user_type='owner')
            owner.set_password('owner123')
            db.session.add(owner)
        if not User.query.filter_by(username='customer').first():
            customer = User(username='customer', user_type='customer')
            customer.set_password('customer123')
            db.session.add(customer)

        db.session.commit()

        owner = User.query.filter_by(user_type='owner').first()
        if owner:
            vehicle_data = None
            json_path = os.path.join(os.path.dirname(__file__), 'j.json')
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        vehicle_data = json.load(f)
                except Exception:
                    vehicle_data = None

            if not vehicle_data:
                vehicle_data = [
                    {
                        'make': 'Toyota',
                        'model': 'Camry',
                        'year': 2020,
                        'price_per_day': 50,
                        'phone_number': '1234567890',
                        'images': 'vehicle-placeholder.svg',
                    },
                    {
                        'make': 'Honda',
                        'model': 'Civic',
                        'year': 2021,
                        'price_per_day': 45,
                        'phone_number': '0987654321',
                        'images': 'vehicle-placeholder.svg',
                    },
                    {
                        'make': 'Ford',
                        'model': 'Mustang',
                        'year': 2019,
                        'price_per_day': 80,
                        'phone_number': '5551234567',
                        'images': 'vehicle-placeholder.svg',
                    },
                    {
                        'make': 'Nissan',
                        'model': 'Altima',
                        'year': 2022,
                        'price_per_day': 60,
                        'phone_number': '4449876543',
                        'images': 'vehicle-placeholder.svg',
                    },
                ]

            if isinstance(vehicle_data, dict):
                vehicle_data = [vehicle_data]

            existing_count = Vehicle.query.count()
            if existing_count < len(vehicle_data):
                for item in vehicle_data[existing_count:]:
                    sample_vehicle = Vehicle(
                        make=item.get('make', 'Toyota'),
                        model=item.get('model', 'Camry'),
                        year=int(item.get('year', 2020)),
                        price_per_day=float(item.get('price_per_day', 50)),
                        owner_id=owner.id,
                        available=bool(item.get('available', True)),
                        phone_number=item.get('phone_number', '1234567890'),
                        images=item.get('images', 'vehicle-placeholder.svg'),
                    )
                    db.session.add(sample_vehicle)
                db.session.commit()
