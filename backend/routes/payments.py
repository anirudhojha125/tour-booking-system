"""
Payment Processing Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Payment, Booking, User
import uuid as uuid_module
from datetime import datetime
from routes.auth import role_required

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    methods = [
        {'id': 'card', 'name': 'Credit/Debit Card', 'icon': 'credit-card'},
        {'id': 'upi', 'name': 'UPI Payment', 'icon': 'smartphone'},
        {'id': 'net_banking', 'name': 'Net Banking', 'icon': 'building-columns'}
    ]
    return jsonify({'payment_methods': methods}), 200

@payments_bp.route('', methods=['POST'])
@role_required(['traveler'])
def process_payment():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('booking_id'):
        return jsonify({'error': 'booking_id is required'}), 400
    if not data.get('payment_method'):
        return jsonify({'error': 'payment_method is required'}), 400
    
    # Validate payment method
    valid_methods = ['card', 'upi', 'net_banking']
    if data['payment_method'] not in valid_methods:
        return jsonify({'error': 'Invalid payment method'}), 400
    
    # Find the booking
    booking = Booking.query.filter_by(uuid=data['booking_id']).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Verify the booking belongs to current user
    if booking.traveler_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if payment already exists
    if booking.payment:
        if booking.payment.payment_status == 'success':
            return jsonify({'error': 'Payment already completed for this booking'}), 400
        # Update existing pending payment
        payment = booking.payment
    else:
        # Create new payment
        payment = Payment(
            booking_id=booking.id,
            amount=booking.total_amount,
            payment_method=data['payment_method'],
            payment_status='pending'
        )
        db.session.add(payment)
    
    # Simulate payment processing
    # In production, integrate with actual payment gateway
    payment.payment_status = 'success'
    payment.transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid_module.uuid4())[:8].upper()}"
    payment.paid_at = datetime.utcnow()
    
    # Update booking status to confirmed
    booking.booking_status = 'confirmed'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Payment processed successfully',
        'payment': payment.to_dict(),
        'booking': booking.to_dict()
    }), 200

@payments_bp.route('/simulate-fail', methods=['POST'])
@role_required(['traveler'])
def simulate_payment_failure():
    """For testing purposes - simulate a failed payment"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('booking_id'):
        return jsonify({'error': 'booking_id is required'}), 400
    
    booking = Booking.query.filter_by(uuid=data['booking_id']).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    if booking.traveler_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if booking.payment:
        payment = booking.payment
    else:
        payment = Payment(
            booking_id=booking.id,
            amount=booking.total_amount,
            payment_method=data.get('payment_method', 'card'),
            payment_status='pending'
        )
        db.session.add(payment)
    
    payment.payment_status = 'failed'
    db.session.commit()
    
    return jsonify({
        'message': 'Payment failed',
        'payment': payment.to_dict()
    }), 200

@payments_bp.route('', methods=['GET'])
@jwt_required()
def get_my_payments():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'traveler':
        payments = Payment.query.join(Booking).filter(Booking.traveler_id == current_user_id).all()
    elif user.role == 'agent':
        payments = Payment.query.join(Booking).join(Booking.tour).filter(Booking.tour.has(agent_id=current_user_id)).all()
    else:  # admin
        payments = Payment.query.all()
    
    return jsonify({
        'payments': [payment.to_dict() for payment in payments],
        'count': len(payments)
    }), 200

@payments_bp.route('/<payment_uuid>', methods=['GET'])
@jwt_required()
def get_payment(payment_uuid):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    payment = Payment.query.filter_by(uuid=payment_uuid).first()
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Check authorization
    if user.role == 'traveler' and payment.booking.traveler_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    if user.role == 'agent' and payment.booking.tour.agent_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'payment': payment.to_dict()}), 200

@payments_bp.route('/stats', methods=['GET'])
@role_required(['admin'])
def get_payment_stats():
    from sqlalchemy import func
    
    stats = {
        'total_payments': Payment.query.count(),
        'total_amount': db.session.query(func.sum(Payment.amount)).filter(Payment.payment_status == 'success').scalar() or 0,
        'successful': Payment.query.filter_by(payment_status='success').count(),
        'pending': Payment.query.filter_by(payment_status='pending').count(),
        'failed': Payment.query.filter_by(payment_status='failed').count(),
        'refunded': Payment.query.filter_by(payment_status='refunded').count()
    }
    
    # Payment method breakdown
    method_stats = db.session.query(
        Payment.payment_method,
        func.count(Payment.id).label('count'),
        func.sum(Payment.amount).label('total')
    ).filter(Payment.payment_status == 'success').group_by(Payment.payment_method).all()
    
    stats['by_method'] = [
        {'method': m[0], 'count': m[1], 'total': float(m[2] or 0)} for m in method_stats
    ]
    
    return jsonify({'stats': stats}), 200
