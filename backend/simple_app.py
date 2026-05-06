"""
Simplified Tour Booking System - Flask Application (No JWT)
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

# Configuration
class Config:
    SECRET_KEY = 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tour_booking.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Simple models
class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    duration = db.Column(db.String(50))
    location = db.Column(db.String(100))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'))
    customer_name = db.Column(db.String(100))
    customer_email = db.Column(db.String(100))
    booking_date = db.Column(db.DateTime)

# Routes
@app.route('/')
def index():
    return jsonify({
        'message': 'Tour Booking System API',
        'version': '1.0.0',
        'endpoints': [
            '/api/tours',
            '/api/bookings'
        ]
    })

@app.route('/api/tours')
def get_tours():
    tours = Tour.query.all()
    return jsonify([{
        'id': tour.id,
        'name': tour.name,
        'description': tour.description,
        'price': tour.price,
        'duration': tour.duration,
        'location': tour.location
    } for tour in tours])

@app.route('/api/tours/<int:tour_id>')
def get_tour(tour_id):
    tour = Tour.query.get_or_404(tour_id)
    return jsonify({
        'id': tour.id,
        'name': tour.name,
        'description': tour.description,
        'price': tour.price,
        'duration': tour.duration,
        'location': tour.location
    })

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    return jsonify([{
        'id': booking.id,
        'tour_id': booking.tour_id,
        'customer_name': booking.customer_name,
        'customer_email': booking.customer_email,
        'booking_date': booking.booking_date.isoformat() if booking.booking_date else None
    } for booking in bookings])

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    # Simple booking creation (without request parsing for simplicity)
    return jsonify({'message': 'Booking endpoint working - implementation needed'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def create_app():
    with app.app_context():
        db.create_all()
        
        # Add sample tours if none exist
        if Tour.query.count() == 0:
            sample_tours = [
                Tour(name='Paris City Tour', description='Explore the beautiful city of Paris', price=99.99, duration='3 hours', location='Paris, France'),
                Tour(name='Rome Historical Tour', description='Discover ancient Rome', price=129.99, duration='4 hours', location='Rome, Italy'),
                Tour(name='London Experience', description='Experience the best of London', price=89.99, duration='3 hours', location='London, UK')
            ]
            for tour in sample_tours:
                db.session.add(tour)
            db.session.commit()
            print("Sample tours added successfully!")
    
    return app

if __name__ == '__main__':
    create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
