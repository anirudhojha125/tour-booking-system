"""
Tour Management Routes - CRUD operations for tours
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Tour, User
from datetime import datetime
from routes.auth import role_required

tours_bp = Blueprint('tours', __name__)

@tours_bp.route('', methods=['GET'])
def get_tours():
    # Query parameters
    location = request.args.get('location')
    tour_type = request.args.get('type')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    available_only = request.args.get('available_only', type=bool, default=False)
    search = request.args.get('search')
    
    query = Tour.query.filter_by(is_active=True)
    
    # Apply filters
    if location:
        query = query.filter(Tour.location.ilike(f'%{location}%'))
    if tour_type:
        query = query.filter_by(tour_type=tour_type)
    if min_price is not None:
        query = query.filter(Tour.price_per_person >= min_price)
    if max_price is not None:
        query = query.filter(Tour.price_per_person <= max_price)
    if available_only:
        query = query.filter(Tour.available_slots > 0)
    if search:
        query = query.filter(
            db.or_(
                Tour.title.ilike(f'%{search}%'),
                Tour.description.ilike(f'%{search}%'),
                Tour.location.ilike(f'%{search}%')
            )
        )
    
    tours = query.order_by(Tour.created_at.desc()).all()
    
    return jsonify({
        'tours': [tour.to_dict() for tour in tours],
        'count': len(tours)
    }), 200

@tours_bp.route('/<tour_uuid>', methods=['GET'])
def get_tour(tour_uuid):
    tour = Tour.query.filter_by(uuid=tour_uuid).first()
    
    if not tour:
        return jsonify({'error': 'Tour not found'}), 404
    
    # Get reviews for this tour
    reviews_data = [review.to_dict() for review in tour.reviews]
    
    tour_data = tour.to_dict()
    tour_data['reviews'] = reviews_data
    tour_data['reviews_count'] = len(reviews_data)
    
    return jsonify({'tour': tour_data}), 200

@tours_bp.route('', methods=['POST'])
@role_required(['agent'])
def create_tour():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'location', 'duration_days', 'price_per_person', 'total_slots', 'tour_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Parse tour date
    try:
        tour_date = datetime.fromisoformat(data['tour_date'])
    except ValueError:
        return jsonify({'error': 'Invalid tour_date format. Use ISO format (YYYY-MM-DDTHH:MM)'}), 400
    
    tour = Tour(
        agent_id=current_user_id,
        title=data['title'],
        description=data.get('description'),
        location=data['location'],
        duration_days=data['duration_days'],
        price_per_person=data['price_per_person'],
        total_slots=data['total_slots'],
        available_slots=data['total_slots'],  # Initially all slots available
        tour_date=tour_date,
        tour_type=data.get('tour_type', 'adventure'),
        image_url=data.get('image_url')
    )
    
    db.session.add(tour)
    db.session.commit()
    
    return jsonify({
        'message': 'Tour created successfully',
        'tour': tour.to_dict()
    }), 201

@tours_bp.route('/<tour_uuid>', methods=['PUT'])
@jwt_required()
def update_tour(tour_uuid):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    tour = Tour.query.filter_by(uuid=tour_uuid).first()
    
    if not tour:
        return jsonify({'error': 'Tour not found'}), 404
    
    # Only agent who created the tour or admin can update
    if tour.agent_id != current_user_id and claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized to update this tour'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'title' in data:
        tour.title = data['title']
    if 'description' in data:
        tour.description = data['description']
    if 'location' in data:
        tour.location = data['location']
    if 'duration_days' in data:
        tour.duration_days = data['duration_days']
    if 'price_per_person' in data:
        tour.price_per_person = data['price_per_person']
    if 'tour_type' in data:
        tour.tour_type = data['tour_type']
    if 'image_url' in data:
        tour.image_url = data['image_url']
    if 'is_active' in data and claims.get('role') == 'admin':
        tour.is_active = data['is_active']
    
    # Handle slot updates carefully
    if 'total_slots' in data:
        new_total = data['total_slots']
        if new_total < tour.total_slots - tour.available_slots:
            return jsonify({'error': 'Cannot reduce total slots below booked slots'}), 400
        # Adjust available slots proportionally
        booked = tour.total_slots - tour.available_slots
        tour.total_slots = new_total
        tour.available_slots = new_total - booked
    
    if 'tour_date' in data:
        try:
            tour.tour_date = datetime.fromisoformat(data['tour_date'])
        except ValueError:
            return jsonify({'error': 'Invalid tour_date format'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Tour updated successfully',
        'tour': tour.to_dict()
    }), 200

@tours_bp.route('/<tour_uuid>', methods=['DELETE'])
@jwt_required()
def delete_tour(tour_uuid):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    tour = Tour.query.filter_by(uuid=tour_uuid).first()
    
    if not tour:
        return jsonify({'error': 'Tour not found'}), 404
    
    # Only agent who created the tour or admin can delete
    if tour.agent_id != current_user_id and claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized to delete this tour'}), 403
    
    # Soft delete - mark as inactive
    tour.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Tour deleted successfully'}), 200

@tours_bp.route('/my-tours', methods=['GET'])
@role_required(['agent'])
def get_my_tours():
    current_user_id = get_jwt_identity()
    
    tours = Tour.query.filter_by(agent_id=current_user_id).order_by(Tour.created_at.desc()).all()
    
    return jsonify({
        'tours': [tour.to_dict() for tour in tours],
        'count': len(tours)
    }), 200

@tours_bp.route('/types', methods=['GET'])
def get_tour_types():
    types = ['adventure', 'cultural', 'nature', 'city', 'beach', 'wildlife']
    return jsonify({'tour_types': types}), 200

@tours_bp.route('/locations', methods=['GET'])
def get_locations():
    # Get unique locations
    locations = db.session.query(Tour.location).filter_by(is_active=True).distinct().all()
    return jsonify({'locations': [loc[0] for loc in locations]}), 200
