# Tour Recommendation & Booking System

A comprehensive full-stack web application for tour discovery, booking, and management connecting **Travelers**, **Tour Agents**, and **Administrators**.

![TourBook](https://img.shields.io/badge/TourBook-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-3.0+-orange)

## Features

### For Travelers
- Browse and search tours with advanced filters
- View detailed tour information and reviews
- Add tours to wishlist (unique constraint per user-tour)
- Book tours with real-time slot availability
- Secure payment processing (Card, UPI, Net Banking)
- Submit verified reviews after completed bookings
- Manage bookings and cancel if needed

### For Tour Agents
- Create and manage tour listings
- Track real-time slot availability
- View and manage bookings for their tours
- Update tour details and availability
- Mark bookings as confirmed/completed

### For Administrators
- Platform overview dashboard with statistics
- Manage all users, tours, and bookings
- Payment monitoring and reporting
- Content moderation capabilities
- Create admin users

## Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM for database operations
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing
- **SQLite** - Database (can be upgraded to PostgreSQL)
- **Werkzeug** - Password hashing

### Frontend
- **HTML5** semantic markup
- **CSS3** with CSS Variables for theming
- **JavaScript (ES6+)** - Vanilla JS for interactivity
- **Font Awesome** - Icons
- **Responsive Design** - Mobile-first approach

## Project Structure

```
tour-booking-system/
├── backend/
│   ├── app.py              # Flask application entry point
│   ├── config.py           # Configuration settings
│   ├── models.py           # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication routes
│   │   ├── tours.py        # Tour management routes
│   │   ├── bookings.py     # Booking routes
│   │   ├── payments.py     # Payment processing routes
│   │   ├── reviews.py      # Review and rating routes
│   │   ├── wishlist.py     # Wishlist routes
│   │   └── admin.py        # Admin dashboard routes
│   └── tour_booking.db     # SQLite database (created on first run)
├── frontend/
│   ├── css/
│   │   └── styles.css      # Main stylesheet with beautiful design
│   ├── js/
│   │   └── main.js         # JavaScript utilities
│   ├── index.html          # Home page
│   ├── tours.html          # Tour listing page
│   ├── tour-details.html   # Individual tour page
│   ├── login.html          # User login
│   ├── register.html       # User registration
│   ├── wishlist.html       # User wishlist
│   ├── bookings.html       # User bookings
│   ├── payment.html        # Payment page
│   ├── agent-dashboard.html # Agent management dashboard
│   └── admin-dashboard.html # Admin management dashboard
├── requirements.txt        # Python dependencies
├── run.py                  # Launcher script
└── README.md               # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone/Navigate to the Project
```bash
cd python-workspace/tour-booking-system
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
# Option 1: Using the launcher script
python run.py

# Option 2: Direct from backend directory
cd backend
python app.py
```

### Step 5: Access the Application
Open your browser and navigate to:
- **Application URL**: http://localhost:5000
- **API Base URL**: http://localhost:5000/api

## Demo Accounts

For testing purposes, you can use these pre-configured accounts:

| Role | Email | Password |
|------|-------|----------|
| Traveler | traveler@demo.com | traveler123 |
| Agent | agent@demo.com | agent123 |
| Admin | admin@demo.com | admin123 |

Or create your own account by registering.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

### Tours
- `GET /api/tours` - List all tours (with filters)
- `GET /api/tours/<id>` - Get tour details
- `POST /api/tours` - Create new tour (Agent only)
- `PUT /api/tours/<id>` - Update tour
- `DELETE /api/tours/<id>` - Delete tour (soft delete)
- `GET /api/tours/my-tours` - Get agent's tours
- `GET /api/tours/types` - Get tour types
- `GET /api/tours/locations` - Get unique locations

### Bookings
- `GET /api/bookings` - Get user's bookings
- `POST /api/bookings` - Create booking
- `GET /api/bookings/<id>` - Get booking details
- `POST /api/bookings/<id>/cancel` - Cancel booking
- `POST /api/bookings/<id>/confirm` - Confirm booking (Agent/Admin)
- `POST /api/bookings/<id>/complete` - Complete booking (Agent/Admin)
- `GET /api/bookings/stats` - Get booking statistics

### Payments
- `GET /api/payments/methods` - Get payment methods
- `POST /api/payments` - Process payment
- `GET /api/payments` - Get payment history
- `GET /api/payments/<id>` - Get payment details
- `GET /api/payments/stats` - Get payment statistics (Admin)

### Reviews
- `GET /api/reviews` - Get reviews
- `POST /api/reviews` - Create review
- `GET /api/reviews/<id>` - Get review details
- `PUT /api/reviews/<id>` - Update review
- `DELETE /api/reviews/<id>` - Delete review
- `GET /api/reviews/my-reviews` - Get user's reviews
- `GET /api/reviews/pending` - Get pending reviews
- `GET /api/reviews/stats` - Get review statistics

### Wishlist
- `GET /api/wishlist` - Get wishlist
- `POST /api/wishlist` - Add to wishlist
- `DELETE /api/wishlist/<tour_id>` - Remove from wishlist
- `GET /api/wishlist/check/<tour_id>` - Check if in wishlist
- `POST /api/wishlist/clear` - Clear wishlist

### Admin
- `GET /api/admin/dashboard` - Get dashboard statistics
- `GET /api/admin/users` - Get all users
- `PUT /api/admin/users/<id>/status` - Update user status
- `PUT /api/admin/users/<id>/role` - Update user role
- `GET /api/admin/tours` - Get all tours
- `GET /api/admin/bookings` - Get all bookings
- `GET /api/admin/reviews` - Get all reviews
- `POST /api/admin/create-admin` - Create admin user

## Design Features

### Color Scheme
- **Primary**: Vibrant Orange-Red (#FF6B35) - Call-to-action buttons
- **Secondary**: Deep Teal (#004E89) - Headers and accents
- **Accent**: Golden Yellow (#FFC857) - Ratings and highlights
- **Dark**: Navy Blue (#1A1A2E) - Text and backgrounds
- **Success**: Green (#28A745)
- **Error**: Red (#DC3545)

### UI/UX Highlights
- Modern gradient backgrounds
- Smooth animations and transitions
- Responsive design for all screen sizes
- Floating cards with shadows
- Interactive star ratings
- Toast notifications
- Loading spinners
- Modal dialogs
- Form validation

## Security Features

- JWT-based authentication with role-based access control
- Password hashing with Werkzeug
- SQL injection protection via SQLAlchemy ORM
- XSS protection through proper escaping
- CORS configuration
- Input validation on all endpoints

## Future Enhancements

- Email notifications
- SMS alerts
- Advanced search with AI recommendations
- Multi-language support
- Mobile app (React Native/Flutter)
- Payment gateway integration (Stripe/Razorpay)
- Real-time chat between travelers and agents
- Advanced analytics and reporting
- Tour images upload functionality

## License

This project is created for educational purposes.

## Support

For issues or questions, please contact the development team.

---

**Happy Traveling with TourBook! ✈️🌍**
