#!/usr/bin/env python3
"""
Demo Data Initialization Script
Creates demo users and tours for the Tour Booking System
"""
import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Tour, Booking, Payment, Review

def create_demo_data():
    """Create demo users and tours"""
    print("Creating demo data...")
    
    # Check if demo users already exist
    if User.query.filter_by(email='traveler@demo.com').first():
        print("Demo data already exists!")
        return
    
    # Create demo users
    demo_users = [
        {
            'email': 'traveler@demo.com',
            'password': 'traveler123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'traveler',
            'phone': '+1234567890'
        },
        {
            'email': 'agent@demo.com',
            'password': 'agent123',
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'role': 'agent',
            'phone': '+1234567891'
        },
        {
            'email': 'admin@demo.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'phone': '+1234567892'
        },
        {
            'email': 'jane.smith@email.com',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'traveler',
            'phone': '+1234567893'
        }
    ]
    
    created_users = {}
    for user_data in demo_users:
        user = User(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            phone=user_data.get('phone'),
            is_active=True
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        created_users[user_data['email']] = user
    
    db.session.commit()
    print(f"Created {len(demo_users)} demo users")
    
    # Create demo tours
    agent = created_users['agent@demo.com']
    demo_tours = [
        {
            'title': 'Bali Adventure Paradise',
            'description': 'Experience the magic of Bali with this comprehensive tour covering ancient temples, rice terraces, and pristine beaches. This 7-day adventure includes accommodation, meals, and guided tours to the island\'s most iconic locations.',
            'location': 'Bali, Indonesia',
            'duration_days': 7,
            'price_per_person': 899.99,
            'total_slots': 25,
            'tour_type': 'adventure',
            'tour_date': datetime.now() + timedelta(days=30),
            'image_url': 'https://images.unsplash.com/photo-1537953773345-b172dd3b5625?w=600&h=400&fit=crop'
        },
        {
            'title': 'Paris City of Lights',
            'description': 'Discover the romantic charm of Paris with visits to the Eiffel Tower, Louvre Museum, Notre-Dame, and charming cafes. Includes skip-the-line tickets, Seine river cruise, and expert local guides.',
            'location': 'Paris, France',
            'duration_days': 5,
            'price_per_person': 1299.99,
            'total_slots': 20,
            'tour_type': 'cultural',
            'tour_date': datetime.now() + timedelta(days=45),
            'image_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&h=400&fit=crop'
        },
        {
            'title': 'Santorini Sunset Experience',
            'description': 'Witness the world-famous Santorini sunsets, explore white-washed villages, and enjoy Mediterranean cuisine. This romantic getaway includes wine tasting, boat tours, and luxury accommodation.',
            'location': 'Santorini, Greece',
            'duration_days': 4,
            'price_per_person': 1599.99,
            'total_slots': 15,
            'tour_type': 'beach',
            'tour_date': datetime.now() + timedelta(days=60),
            'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=600&h=400&fit=crop'
        },
        {
            'title': 'Swiss Alps Adventure',
            'description': 'Conquer the majestic Swiss Alps with hiking trails, mountain railways, and Alpine villages. Includes accommodation in mountain lodges, guided hikes, and scenic train rides.',
            'location': 'Swiss Alps, Switzerland',
            'duration_days': 6,
            'price_per_person': 1899.99,
            'total_slots': 18,
            'tour_type': 'nature',
            'tour_date': datetime.now() + timedelta(days=90),
            'image_url': 'https://images.unsplash.com/photo-1551632811-561732d1e306?w=600&h=400&fit=crop'
        },
        {
            'title': 'Tokyo Cultural Immersion',
            'description': 'Immerse yourself in Japanese culture with temple visits, traditional tea ceremonies, and modern Tokyo experiences. Includes accommodation, guided tours, and cultural workshops.',
            'location': 'Tokyo, Japan',
            'duration_days': 8,
            'price_per_person': 2199.99,
            'total_slots': 22,
            'tour_type': 'cultural',
            'tour_date': datetime.now() + timedelta(days=120),
            'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e2990c0b?w=600&h=400&fit=crop'
        },
        {
            'title': 'Safari Adventure Kenya',
            'description': 'Experience the thrill of African safari with wildlife viewing in Masai Mara, cultural visits to Maasai villages, and luxury tented camps. Includes all meals, game drives, and expert guides.',
            'location': 'Masai Mara, Kenya',
            'duration_days': 5,
            'price_per_person': 2499.99,
            'total_slots': 12,
            'tour_type': 'wildlife',
            'tour_date': datetime.now() + timedelta(days=150),
            'image_url': 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=600&h=400&fit=crop'
        },
        {
            'title': 'New York City Explorer',
            'description': 'Explore the Big Apple with visits to Times Square, Central Park, Statue of Liberty, and Broadway shows. Includes accommodation, city tours, and attraction tickets.',
            'location': 'New York, USA',
            'duration_days': 4,
            'price_per_person': 999.99,
            'total_slots': 30,
            'tour_type': 'city',
            'tour_date': datetime.now() + timedelta(days=20),
            'image_url': 'https://images.unsplash.com/photo-1496442226666-8ec4a789c840?w=600&h=400&fit=crop'
        },
        {
            'title': 'Dubai Luxury Experience',
            'description': 'Experience the luxury and innovation of Dubai with visits to Burj Khalifa, desert safaris, and shopping festivals. Includes 5-star accommodation and exclusive experiences.',
            'location': 'Dubai, UAE',
            'duration_days': 6,
            'price_per_person': 1799.99,
            'total_slots': 25,
            'tour_type': 'city',
            'tour_date': datetime.now() + timedelta(days=75),
            'image_url': 'https://images.unsplash.com/photo-1512455605323-6a2b8c9a4e5e?w=600&h=400&fit=crop'
        }
    ]
    
    created_tours = []
    for tour_data in demo_tours:
        tour = Tour(
            agent_id=agent.id,
            title=tour_data['title'],
            description=tour_data['description'],
            location=tour_data['location'],
            duration_days=tour_data['duration_days'],
            price_per_person=tour_data['price_per_person'],
            total_slots=tour_data['total_slots'],
            available_slots=tour_data['total_slots'],
            tour_type=tour_data['tour_type'],
            tour_date=tour_data['tour_date'],
            image_url=tour_data['image_url'],
            is_active=True
        )
        db.session.add(tour)
        created_tours.append(tour)
    
    db.session.commit()
    print(f"Created {len(demo_tours)} demo tours")
    
    # Create some demo bookings and reviews
    traveler = created_users['traveler@demo.com']
    jane = created_users['jane.smith@email.com']
    
    # Create a completed booking with review
    booking1 = Booking(
        traveler_id=jane.id,
        tour_id=created_tours[0].id,  # Bali tour
        seats_booked=2,
        total_amount=created_tours[0].price_per_person * 2,
        booking_status='completed',
        booking_date=datetime.now() - timedelta(days=10)
    )
    db.session.add(booking1)
    db.session.commit()
    
    # Add payment for completed booking
    payment1 = Payment(
        booking_id=booking1.id,
        amount=booking1.total_amount,
        payment_method='card',
        payment_status='success',
        transaction_id='TXN' + datetime.now().strftime('%Y%m%d%H%M%S'),
        paid_at=datetime.now() - timedelta(days=10)
    )
    db.session.add(payment1)
    
    # Add review for completed booking
    review1 = Review(
        booking_id=booking1.id,
        tour_id=created_tours[0].id,
        user_id=jane.id,
        rating=5,
        comment='Amazing experience! The tour guide was knowledgeable and the accommodations were excellent. Bali is truly magical!',
        created_at=datetime.now() - timedelta(days=5)
    )
    db.session.add(review1)
    
    # Create a confirmed booking
    booking2 = Booking(
        traveler_id=traveler.id,
        tour_id=created_tours[1].id,  # Paris tour
        seats_booked=1,
        total_amount=created_tours[1].price_per_person,
        booking_status='confirmed',
        booking_date=datetime.now() - timedelta(days=2)
    )
    db.session.add(booking2)
    db.session.commit()
    
    # Add payment for confirmed booking
    payment2 = Payment(
        booking_id=booking2.id,
        amount=booking2.total_amount,
        payment_method='upi',
        payment_status='success',
        transaction_id='TXN' + datetime.now().strftime('%Y%m%d%H%M%S') + '01',
        paid_at=datetime.now() - timedelta(days=2)
    )
    db.session.add(payment2)
    
    # Create a pending booking
    booking3 = Booking(
        traveler_id=traveler.id,
        tour_id=created_tours[2].id,  # Santorini tour
        seats_booked=2,
        total_amount=created_tours[2].price_per_person * 2,
        booking_status='pending',
        booking_date=datetime.now() - timedelta(days=1)
    )
    db.session.add(booking3)
    
    # Update available slots
    created_tours[0].available_slots -= 2  # Bali tour
    created_tours[1].available_slots -= 1  # Paris tour
    created_tours[2].available_slots -= 2  # Santorini tour
    
    db.session.commit()
    
    print("Created demo bookings, payments, and reviews")
    print("Demo data initialization completed successfully!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    
    with app.app_context():
        create_demo_data()
        
        print("\n" + "="*60)
        print("DEMO ACCOUNTS CREATED:")
        print("="*60)
        print("Traveler: traveler@demo.com / traveler123")
        print("Agent:    agent@demo.com / agent123")
        print("Admin:    admin@demo.com / admin123")
        print("Jane:     jane.smith@email.com / password123")
        print("="*60)
        print(f"Tours created: {Tour.query.count()}")
        print(f"Users created: {User.query.count()}")
        print(f"Bookings created: {Booking.query.count()}")
        print("="*60)
