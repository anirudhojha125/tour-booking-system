"""
Booking Management Routes - Tour booking operations
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Booking, Tour, User
from routes.auth import role_required

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('', methods=['POST'])
@role_required(['traveler'])
def create_booking():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('tour_id'):
        return jsonify({'error': 'tour_id is required'}), 400
    if not data.get('seats') or data['seats'] < 1:
        return jsonify({'error': 'seats must be at least 1'}), 400
    
    # Find the tour
    tour = Tour.query.filter_by(uuid=data['tour_id']).first()
    if not tour:
        return jsonify({'error': 'Tour not found'}), 404
    
    if not tour.is_active:
        return jsonify({'error': 'Tour is not available'}), 400
    
    # Check availability
    seats_requested = data['seats']
    if tour.available_slots < seats_requested:
        return jsonify({
            'error': 'Not enough slots available',
            'available_slots': tour.available_slots
        }), 400
    
    # Calculate total amount
    total_amount = tour.price_per_person * seats_requested
    
    # Create booking
    booking = Booking(
        traveler_id=current_user_id,
        tour_id=tour.id,
        seats_booked=seats_requested,
        total_amount=total_amount,
        booking_status='pending'
    )
    
    # Update available slots
    tour.available_slots -= seats_requested
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({
        'message': 'Booking created successfully',
        'booking': booking.to_dict()
    }), 201

@bookings_bp.route('', methods=['GET'])
@jwt_required()
def get_my_bookings():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'traveler':
        bookings = Booking.query.filter_by(traveler_id=current_user_id).order_by(Booking.booking_date.desc()).all()
    elif user.role == 'agent':
        # Get bookings for tours created by this agent
        bookings = Booking.query.join(Tour).filter(Tour.agent_id == current_user_id).order_by(Booking.booking_date.desc()).all()
    else:  # admin
        bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    
    return jsonify({
        'bookings': [booking.to_dict() for booking in bookings],
        'count': len(bookings)
    }), 200

@bookings_bp.route('/<booking_uuid>', methods=['GET'])
@jwt_required()
def get_booking(booking_uuid):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    booking = Booking.query.filter_by(uuid=booking_uuid).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check authorization
    if user.role == 'traveler' and booking.traveler_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    if user.role == 'agent' and booking.tour.agent_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'booking': booking.to_dict()}), 200

@bookings_bp.route('/<booking_uuid>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_uuid):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    booking = Booking.query.filter_by(uuid=booking_uuid).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check authorization
    if user.role == 'traveler' and booking.traveler_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if booking can be cancelled
    if booking.booking_status in ['cancelled', 'completed']:
        return jsonify({'error': f'Cannot cancel booking with status: {booking.booking_status}'}), 400
    
    # Check if payment was made - if so, need to handle refund
    if booking.payment and booking.payment.payment_status == 'success':
        return jsonify({
            'error': 'Cannot cancel - payment already processed. Please contact support for refund.'
        }), 400
    
    # Restore available slots
    tour = booking.tour
    tour.available_slots += booking.seats_booked
    
    # Update booking status
    booking.booking_status = 'cancelled'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Booking cancelled successfully',
        'booking': booking.to_dict()
    }), 200

@bookings_bp.route('/<booking_uuid>/confirm', methods=['POST'])
@role_required(['agent', 'admin'])
def confirm_booking(booking_uuid):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    booking = Booking.query.filter_by(uuid=booking_uuid).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Agents can only confirm bookings for their own tours
    if user.role == 'agent' and booking.tour.agent_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if booking.booking_status != 'pending':
        return jsonify({'error': f'Cannot confirm booking with status: {booking.booking_status}'}), 400
    
    booking.booking_status = 'confirmed'
    db.session.commit()
    
    return jsonify({
        'message': 'Booking confirmed successfully',
        'booking': booking.to_dict()
    }), 200

@bookings_bp.route('/<booking_uuid>/complete', methods=['POST'])
@role_required(['agent', 'admin'])
def complete_booking(booking_uuid):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    booking = Booking.query.filter_by(uuid=booking_uuid).first()
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Agents can only complete bookings for their own tours
    if user.role == 'agent' and booking.tour.agent_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if booking.booking_status != 'confirmed':
        return jsonify({'error': f'Cannot complete booking with status: {booking.booking_status}'}), 400
    
    booking.booking_status = 'completed'
    db.session.commit()
    
    return jsonify({
        'message': 'Booking marked as completed',
        'booking': booking.to_dict()
    }), 200

@bookings_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_booking_stats():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'traveler':
        stats = {
            'total': Booking.query.filter_by(traveler_id=current_user_id).count(),
            'pending': Booking.query.filter_by(traveler_id=current_user_id, booking_status='pending').count(),
            'confirmed': Booking.query.filter_by(traveler_id=current_user_id, booking_status='confirmed').count(),
            'completed': Booking.query.filter_by(traveler_id=current_user_id, booking_status='completed').count(),
            'cancelled': Booking.query.filter_by(traveler_id=current_user_id, booking_status='cancelled').count()
        }
    elif user.role == 'agent':
        stats = {
            'total': Booking.query.join(Tour).filter(Tour.agent_id == current_user_id).count(),
            'pending': Booking.query.join(Tour).filter(Tour.agent_id == current_user_id, Booking.booking_status == 'pending').count(),
            'confirmed': Booking.query.join(Tour).filter(Tour.agent_id == current_user_id, Booking.booking_status == 'confirmed').count(),
            'completed': Booking.query.join(Tour).filter(Tour.agent_id == current_user_id, Booking.booking_status == 'completed').count(),
            'cancelled': Booking.query.join(Tour).filter(Tour.agent_id == current_user_id, Booking.booking_status == 'cancelled').count()
        }
    else:  # admin
        stats = {
            'total': Booking.query.count(),
            'pending': Booking.query.filter_by(booking_status='pending').count(),
            'confirmed': Booking.query.filter_by(booking_status='confirmed').count(),
            'completed': Booking.query.filter_by(booking_status='completed').count(),
            'cancelled': Booking.query.filter_by(booking_status='cancelled').count()
        }
    
    return jsonify({'stats': stats}), 200
