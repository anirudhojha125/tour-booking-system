"""
Review & Rating Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Review, Booking, Tour, User
from routes.auth import role_required

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('', methods=['GET'])
def get_reviews():
    tour_uuid = request.args.get('tour_id')
    
    query = Review.query
    
    if tour_uuid:
        tour = Tour.query.filter_by(uuid=tour_uuid).first()
        if tour:
            query = query.filter_by(tour_id=tour.id)
    
    reviews = query.order_by(Review.created_at.desc()).all()
    
    return jsonify({
        'reviews': [review.to_dict() for review in reviews],
        'count': len(reviews)
    }), 200

@reviews_bp.route('', methods=['POST'])
@role_required(['traveler'])
def create_review():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('booking_id'):
        return jsonify({'error': 'booking_id is required'}), 400
    if not data.get('rating') or not (1 <= data['rating'] <= 5):
        return jsonify({'error': 'rating must be between 1 and 5'}), 400
    
    # Find the booking
    booking = Booking.query.filter_by(uuid=data['booking_id']).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Verify the booking belongs to current user
    if booking.traveler_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if booking is completed
    if booking.booking_status != 'completed':
        return jsonify({'error': 'Can only review completed bookings'}), 400
    
    # Check if review already exists
    if booking.review:
        return jsonify({'error': 'Review already exists for this booking'}), 409
    
    # Create review
    review = Review(
        booking_id=booking.id,
        tour_id=booking.tour_id,
        user_id=current_user_id,
        rating=data['rating'],
        comment=data.get('comment', '')
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'message': 'Review submitted successfully',
        'review': review.to_dict()
    }), 201

@reviews_bp.route('/<review_uuid>', methods=['GET'])
def get_review(review_uuid):
    review = Review.query.filter_by(uuid=review_uuid).first()
    
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    return jsonify({'review': review.to_dict()}), 200

@reviews_bp.route('/<review_uuid>', methods=['PUT'])
@jwt_required()
def update_review(review_uuid):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    review = Review.query.filter_by(uuid=review_uuid).first()
    
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    # Only reviewer or admin can update
    if review.user_id != current_user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'rating' in data:
        if not (1 <= data['rating'] <= 5):
            return jsonify({'error': 'rating must be between 1 and 5'}), 400
        review.rating = data['rating']
    
    if 'comment' in data:
        review.comment = data['comment']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Review updated successfully',
        'review': review.to_dict()
    }), 200

@reviews_bp.route('/<review_uuid>', methods=['DELETE'])
@jwt_required()
def delete_review(review_uuid):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    review = Review.query.filter_by(uuid=review_uuid).first()
    
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    # Only reviewer or admin can delete
    if review.user_id != current_user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'message': 'Review deleted successfully'}), 200

@reviews_bp.route('/my-reviews', methods=['GET'])
@role_required(['traveler'])
def get_my_reviews():
    current_user_id = get_jwt_identity()
    
    reviews = Review.query.filter_by(user_id=current_user_id).order_by(Review.created_at.desc()).all()
    
    return jsonify({
        'reviews': [review.to_dict() for review in reviews],
        'count': len(reviews)
    }), 200

@reviews_bp.route('/pending', methods=['GET'])
@role_required(['traveler'])
def get_pending_reviews():
    """Get list of completed bookings that can be reviewed"""
    current_user_id = get_jwt_identity()
    
    # Find completed bookings without reviews
    bookings = Booking.query.filter_by(
        traveler_id=current_user_id,
        booking_status='completed'
    ).filter(
        ~Booking.id.in_(
            db.session.query(Review.booking_id).filter(Review.user_id == current_user_id)
        )
    ).all()
    
    return jsonify({
        'pending_reviews': [booking.to_dict() for booking in bookings],
        'count': len(bookings)
    }), 200

@reviews_bp.route('/stats', methods=['GET'])
def get_review_stats():
    from sqlalchemy import func
    
    stats = db.session.query(
        func.avg(Review.rating).label('average_rating'),
        func.count(Review.id).label('total_reviews')
    ).first()
    
    # Rating distribution
    distribution = db.session.query(
        Review.rating,
        func.count(Review.id).label('count')
    ).group_by(Review.rating).all()
    
    return jsonify({
        'average_rating': round(float(stats[0] or 0), 1),
        'total_reviews': stats[1] or 0,
        'rating_distribution': {str(d[0]): d[1] for d in distribution}
    }), 200
