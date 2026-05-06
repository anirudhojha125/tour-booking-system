"""
Wishlist Routes - Save favorite tours
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Wishlist, Tour, User
from routes.auth import role_required

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('', methods=['GET'])
@role_required(['traveler'])
def get_wishlist():
    current_user_id = get_jwt_identity()
    
    wishlist_items = Wishlist.query.filter_by(user_id=current_user_id).all()
    
    return jsonify({
        'wishlist': [item.to_dict() for item in wishlist_items],
        'count': len(wishlist_items)
    }), 200

@wishlist_bp.route('', methods=['POST'])
@role_required(['traveler'])
def add_to_wishlist():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('tour_id'):
        return jsonify({'error': 'tour_id is required'}), 400
    
    # Find the tour
    tour = Tour.query.filter_by(uuid=data['tour_id']).first()
    if not tour:
        return jsonify({'error': 'Tour not found'}), 404
    
    # Check if already in wishlist (database constraint will catch this too)
    existing = Wishlist.query.filter_by(user_id=current_user_id, tour_id=tour.id).first()
    if existing:
        return jsonify({'error': 'Tour is already in your wishlist'}), 409
    
    # Add to wishlist
    wishlist_item = Wishlist(
        user_id=current_user_id,
        tour_id=tour.id
    )
    
    db.session.add(wishlist_item)
    db.session.commit()
    
    return jsonify({
        'message': 'Added to wishlist successfully',
        'wishlist_item': wishlist_item.to_dict()
    }), 201

@wishlist_bp.route('/<tour_uuid>', methods=['DELETE'])
@role_required(['traveler'])
def remove_from_wishlist(tour_uuid):
    current_user_id = get_jwt_identity()
    
    # Find the tour
    tour = Tour.query.filter_by(uuid=tour_uuid).first()
    if not tour:
        return jsonify({'error': 'Tour not found'}), 404
    
    # Find the wishlist item
    wishlist_item = Wishlist.query.filter_by(user_id=current_user_id, tour_id=tour.id).first()
    
    if not wishlist_item:
        return jsonify({'error': 'Tour not found in wishlist'}), 404
    
    db.session.delete(wishlist_item)
    db.session.commit()
    
    return jsonify({'message': 'Removed from wishlist successfully'}), 200

@wishlist_bp.route('/check/<tour_uuid>', methods=['GET'])
@role_required(['traveler'])
def check_wishlist(tour_uuid):
    """Check if a specific tour is in the user's wishlist"""
    current_user_id = get_jwt_identity()
    
    tour = Tour.query.filter_by(uuid=tour_uuid).first()
    if not tour:
        return jsonify({'error': 'Tour not found'}), 404
    
    exists = Wishlist.query.filter_by(user_id=current_user_id, tour_id=tour.id).first() is not None
    
    return jsonify({
        'in_wishlist': exists,
        'tour_id': tour_uuid
    }), 200

@wishlist_bp.route('/clear', methods=['POST'])
@role_required(['traveler'])
def clear_wishlist():
    current_user_id = get_jwt_identity()
    
    # Delete all wishlist items for the user
    Wishlist.query.filter_by(user_id=current_user_id).delete()
    db.session.commit()
    
    return jsonify({'message': 'Wishlist cleared successfully'}), 200
