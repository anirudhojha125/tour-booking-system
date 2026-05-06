#!/usr/bin/env python3
"""
Tour Recommendation & Booking System - Launcher Script
Run this script to start the Flask application
"""
import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from app import create_app

if __name__ == '__main__':
    print("=" * 60)
    print("Tour Recommendation & Booking System")
    print("=" * 60)
    print("\nStarting server...")
    print("Access the application at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
