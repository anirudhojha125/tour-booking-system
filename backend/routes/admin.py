"""
Admin Routes - System administration and oversight
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Tour, Booking, Payment, Review
from routes.auth import role_required
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@role_required(['admin'])
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    
    # User statistics
    user_stats = {
        'total_users': User.query.count(),
        'travelers': User.query.filter_by(role='traveler').count(),
        'agents': User.query.filter_by(role='agent').count(),
        'admins': User.query.filter_by(role='admin').count(),
        'active_users': User.query.filter_by(is_active=True).count()
    }
    
    # Tour statistics
    tour_stats = {
        'total_tours': Tour.query.count(),
        'active_tours': Tour.query.filter_by(is_active=True).count(),
        'by_type': {}
    }
    
    # Tour types breakdown
    tour_types = db.session.query(Tour.tour_type, func.count(Tour.id)).filter_by(is_active=True).group_by(Tour.tour_type).all()
    tour_stats['by_type'] = {t[0]: t[1] for t in tour_types}
    
    # Booking statistics
    booking_stats = {
        'total': Booking.query.count(),
        'pending': Booking.query.filter_by(booking_status='pending').count(),
        'confirmed': Booking.query.filter_by(booking_status='confirmed').count(),
        'completed': Booking.query.filter_by(booking_status='completed').count(),
        'cancelled': Booking.query.filter_by(booking_status='cancelled').count(),
        'total_revenue': db.session.query(func.sum(Booking.total_amount)).filter(
            Booking.booking_status.in_(['confirmed', 'completed'])
        ).scalar() or 0
    }
    
    # Payment statistics
    payment_stats = {
        'total_payments': Payment.query.count(),
        'successful': Payment.query.filter_by(payment_status='success').count(),
        'total_collected': db.session.query(func.sum(Payment.amount)).filter_by(payment_status='success').scalar() or 0,
        'by_method': {}
    }
    
    # Payment methods breakdown
    payment_methods = db.session.query(Payment.payment_method, func.count(Payment.id), func.sum(Payment.amount)).filter_by(
        payment_status='success'
    ).group_by(Payment.payment_method).all()
    payment_stats['by_method'] = {
        p[0]: {'count': p[1], 'total': float(p[2] or 0)} for p in payment_methods
    }
    
    # Review statistics
    review_stats = {
        'total_reviews': Review.query.count(),
        'average_rating': round(float(db.session.query(func.avg(Review.rating)).scalar() or 0), 1)
    }
    
    return jsonify({
        'users': user_stats,
        'tours': tour_stats,
        'bookings': booking_stats,
        'payments': payment_stats,
        'reviews': review_stats
    }), 200

@admin_bp.route('/users', methods=['GET'])
@role_required(['admin'])
def get_all_users():
    """Get all users with filtering"""
    role = request.args.get('role')
    is_active = request.args.get('is_active')
    search = request.args.get('search')
    
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == 'true')
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    users = query.order_by(User.created_at.desc()).all()
    
    return jsonify({
        'users': [user.to_dict() for user in users],
        'count': len(users)
    }), 200

@admin_bp.route('/users/<user_uuid>/status', methods=['PUT'])
@role_required(['admin'])
def update_user_status(user_uuid):
    """Activate or deactivate a user account"""
    user = User.query.filter_by(uuid=user_uuid).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'is_active' in data:
        user.is_active = data['is_active']
        db.session.commit()
        
        return jsonify({
            'message': f"User {'activated' if user.is_active else 'deactivated'} successfully",
            'user': user.to_dict()
        }), 200
    
    return jsonify({'error': 'is_active field is required'}), 400

@admin_bp.route('/users/<user_uuid>/role', methods=['PUT'])
@role_required(['admin'])
def update_user_role(user_uuid):
    """Change user role"""
    user = User.query.filter_by(uuid=user_uuid).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'role' not in data:
        return jsonify({'error': 'role field is required'}), 400
    
    if data['role'] not in ['traveler', 'agent', 'admin']:
        return jsonify({'error': 'Invalid role. Must be traveler, agent, or admin'}), 400
    
    user.role = data['role']
    db.session.commit()
    
    return jsonify({
        'message': 'User role updated successfully',
        'user': user.to_dict()
    }), 200

@admin_bp.route('/tours', methods=['GET'])
@role_required(['admin'])
def get_all_tours():
    """Get all tours including inactive ones"""
    query = Tour.query
    
    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == 'true')
    
    tours = query.order_by(Tour.created_at.desc()).all()
    
    return jsonify({
        'tours': [tour.to_dict() for tour in tours],
        'count': len(tours)
    }), 200

@admin_bp.route('/bookings', methods=['GET'])
@role_required(['admin'])
def get_all_bookings():
    """Get all bookings with filtering"""
    status = request.args.get('status')
    
    query = Booking.query
    
    if status:
        query = query.filter_by(booking_status=status)
    
    bookings = query.order_by(Booking.booking_date.desc()).all()
    
    return jsonify({
        'bookings': [booking.to_dict() for booking in bookings],
        'count': len(bookings)
    }), 200

@admin_bp.route('/reviews', methods=['GET'])
@role_required(['admin'])
def get_all_reviews():
    """Get all reviews for moderation"""
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    
    return jsonify({
        'reviews': [review.to_dict() for review in reviews],
        'count': len(reviews)
    }), 200

@admin_bp.route('/create-admin', methods=['POST'])
@role_required(['admin'])
def create_admin():
    """Create a new admin user"""
    data = request.get_json()
    
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if email exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create admin user
    user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        role='admin'
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Admin user created successfully',
        'user': user.to_dict()
    }), 201
