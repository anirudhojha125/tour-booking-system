"""
Tour Recommendation & Booking System - Flask Application
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from routes.tours import tours_bp
from routes.bookings import bookings_bp
from routes.reviews import reviews_bp
from routes.wishlist import wishlist_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(tours_bp, url_prefix='/api/tours')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Serve frontend
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        return app.send_static_file(path)
    
    # Create tables and initialize demo data
    with app.app_context():
        db.create_all()
        
        # Initialize demo data if no users exist
        from models import User
        if User.query.count() == 0:
            try:
                from init_demo_data import create_demo_data
                create_demo_data()
                print("Demo data initialized successfully!")
            except Exception as e:
                print(f"Failed to initialize demo data: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
