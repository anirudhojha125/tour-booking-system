"""
Tour Recommendation & Booking System - Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum('traveler', 'agent', 'admin', name='user_roles'), default='traveler')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='traveler', lazy=True, foreign_keys='Booking.traveler_id')
    agent_tours = db.relationship('Tour', backref='agent', lazy=True, foreign_keys='Tour.agent_id')
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Tour(db.Model):
    __tablename__ = 'tours'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(200), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    price_per_person = db.Column(db.Float, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    tour_date = db.Column(db.DateTime, nullable=False)
    tour_type = db.Column(db.Enum('adventure', 'cultural', 'nature', 'city', 'beach', 'wildlife', name='tour_types'))
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='tour', lazy=True)
    reviews = db.relationship('Review', backref='tour', lazy=True)
    wishlist_entries = db.relationship('Wishlist', backref='tour', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'agent_id': self.agent_id,
            'agent_name': f"{self.agent.first_name} {self.agent.last_name}" if self.agent else None,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'duration_days': self.duration_days,
            'price_per_person': self.price_per_person,
            'total_slots': self.total_slots,
            'available_slots': self.available_slots,
            'tour_date': self.tour_date.isoformat() if self.tour_date else None,
            'tour_type': self.tour_type,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'avg_rating': self.get_average_rating()
        }
    
    def get_average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 1)

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    traveler_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id'), nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    booking_status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', 'completed', name='booking_status'), default='pending')
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payment = db.relationship('Payment', backref='booking', lazy=True, uselist=False)
    review = db.relationship('Review', backref='booking', lazy=True, uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'traveler_id': self.traveler_id,
            'traveler_name': f"{self.traveler.first_name} {self.traveler.last_name}" if self.traveler else None,
            'tour_id': self.tour_id,
            'tour_title': self.tour.title if self.tour else None,
            'tour_location': self.tour.location if self.tour else None,
            'seats_booked': self.seats_booked,
            'total_amount': self.total_amount,
            'booking_status': self.booking_status,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'can_review': self.booking_status == 'completed' and not self.review
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.Enum('card', 'upi', 'net_banking', name='payment_methods'), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'success', 'failed', 'refunded', name='payment_status'), default='pending')
    transaction_id = db.Column(db.String(100), unique=True, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'booking_id': self.booking_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'booking_id': self.booking_id,
            'tour_id': self.tour_id,
            'tour_title': self.tour.title if self.tour else None,
            'user_id': self.user_id,
            'user_name': f"{self.user.first_name} {self.user.last_name}" if self.user else None,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey('tours.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicates
    __table_args__ = (db.UniqueConstraint('user_id', 'tour_id', name='unique_user_tour_wishlist'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tour_id': self.tour_id,
            'tour': self.tour.to_dict() if self.tour else None,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }
