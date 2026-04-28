# Mathura Tourism - Django Project

A complete full-stack Django web application for exploring, discovering, and booking tourism services in Mathura. Features include a custom-built AI chatbot, intelligent navigation system, real-time place discovery, and comprehensive local service booking capabilities.

## 🌟 Features

- **Tourist Places Directory**: Browse temples, ghats, museums, and parks in Mathura
- **Custom AI Chatbot**: Intelligent conversational assistant for instant tourism assistance
- **Advanced Navigation**: Interactive maps and route planning for seamless travel
- **Local Services**: Hotels, restaurants, transport, and cafes with booking system
- **User Accounts**: Authentication, favorites, profile management, and booking history
- **Reviews & Ratings**: Rate and review places with community feedback
- **Real-time Information**: Location-based services and nearby place discovery
- **Responsive Design**: Bootstrap 5 - works seamlessly on desktop, tablet, and mobile
- **REST APIs**: Full-featured DRF API for frontend consumption
- **Voice Input**: Web Speech API integration for chatbot voice commands

## 📋 Project Structure

```
mathura_tourism/
├── manage.py                           # Django management command
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
├── db.sqlite3                          # SQLite database
│
├── mathura_tourism/                    # Project settings
│   ├── __init__.py
│   ├── settings.py                     # Django configuration
│   ├── urls.py                         # Main URL routing
│   ├── wsgi.py                         # WSGI application
│   └── asgi.py                         # ASGI application
│
└── tourism/                            # Main Django app
    ├── __init__.py
    ├── admin.py                        # Django admin configuration
    ├── apps.py                         # App configuration
    ├── models.py                       # Database models
    ├── serializers.py                  # DRF serializers
    ├── views.py                        # Page views & chatbot
    ├── views_api.py                    # API views (DRF)
    ├── urls.py                         # Page URLs
    ├── urls_api.py                     # API URLs
    ├── signals.py                      # Django signals
    ├── management/
    │   └── commands/
    │       └── load_sample_data.py     # Management command for sample data
    │
    ├── migrations/                     # Database migrations
    │
    ├── templates/                      # HTML templates
    │   ├── base.html                   # Base template with navbar
    │   ├── dashboard.html              # Dashboard/home page
    │   ├── explore.html                # Places listing & filtering
    │   ├── place_detail.html           # Individual place details
    │   ├── navigation.html             # Map & navigation page
    │   ├── chatbot.html                # AI chatbot interface
    │   ├── services.html               # Services booking page
    │   ├── favourites.html             # User's favorite places
    │   ├── profile.html                # User profile page
    │   ├── login.html                  # Login page
    │   └── register.html               # Registration page
    │
    └── static/
        ├── css/
        │   └── style.css               # Main stylesheet
        └── js/
            ├── main.js                 # Core JavaScript utilities
            ├── map.js                  # Interactive map manager
            └── chatbot.js              # AI chatbot interface manager
```

## 🗄️ Database Models

### Core Models
- **TouristPlace**: Temples, ghats, museums, parks with location, rating, images
- **Review**: User reviews for places with rating and comments
- **LocalService**: Hotels, restaurants, transport, cafes with contact info
- **Booking**: Service bookings with status tracking
- **Notification**: User notifications system
- **FavouritePlace**: User's favorite places list
- **UserProfile**: Extended user information (phone, preferences)

## 🔌 API Endpoints

All APIs use Django REST Framework with pagination (20 items per page).

### Authentication
- `POST /api/register/` - User registration
- `POST /api/users/login/` - User login

### Tourist Places
- `GET /api/places/` - List all places (with pagination)
- `GET /api/places/?category=temple` - Filter by category
- `GET /api/places/{id}/` - Place detail
- `GET /api/places/nearby/?lat=27.5&lng=77.6&radius=5` - Nearby places

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review (authenticated)
- `GET /api/reviews/by_place/?place_id=1` - Reviews for specific place
- `PUT /api/reviews/{id}/` - Update review (owner only)

### Local Services
- `GET /api/services/` - List services
- `GET /api/services/?type=hotel` - Filter by service type
- `GET /api/services/nearby/?lat=27.5&lng=77.6&radius=5` - Nearby services
- `POST /api/bookings/` - Create booking (authenticated)

### User Features
- `GET /api/bookings/` - User's bookings (authenticated)
- `GET /api/notifications/` - User's notifications (authenticated)
- `POST /api/notifications/{id}/mark_as_read/` - Mark notification read
- `GET /api/favourites/` - User's favorites (authenticated)
- `POST /api/favourites/add_favourite/` - Add to favorites
- `POST /api/favourites/remove_favourite/` - Remove from favorites

### Chatbot
- `POST /chatbot/api/` - Send message to AI chatbot

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- Git (optional)

### Step 1: Clone or Create Project
```bash
# Using the provided folder
cd c:\Users\vikshuG\mathra-project\mathura_tourism
```

### Step 2: Create Virtual Environment
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

### Step 4: Setup Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Or for Windows
copy .env.example .env

# Edit .env with your configuration settings
```

### Step 5: Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser

# Load sample data
python manage.py load_sample_data
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

**Test Accounts** (if you ran `load_sample_data`):
- Admin: username=`admin`, password=`admin123`
- User: username=`tourist`, password=`tourist123`

##  Main Pages

### Dashboard (`/`)
- Welcome message with user greeting
- Featured places carousel
- Category grid (Temples, Ghats, Museums, Parks)
- Search functionality
- "Find Nearby Places" button
- Upcoming events/festivals panel

### Explore (`/explore/`)
- All tourist places listing
- Category and text search filters
- Place cards with ratings and distance
- View details button

### Place Detail (`/place/<id>/`)
- Complete place information with images
- Interactive location map
- Rating and review count
- Customer reviews section
- Add to favorites button
- Get directions button

### Navigation (`/navigation/`)
- Interactive map display
- User location detection
- Destination search and autocomplete
- Route planning and directions
- Distance and time estimation
- Nearby places discovery

### AI Chatbot (`/chatbot/`)
- Clean and intuitive chat interface
- Conversation history management
- Text-based input
- Voice input support (Web Speech API)
- Quick suggestion chips for common queries
- Intelligent response generation

### Services (`/services/`)
- Tabs for different service types
- Hotel, Restaurant, Transport, Cafe listings
- Booking modal
- Contact information
- Ratings and descriptions

### Favorites (`/favourites/`)
- User's saved places
- Quick access to place details
- Remove from favorites option
- Navigation shortcuts

### Profile (`/profile/`)
- User account information
- Edit phone and preferences
- Booking history table
- Password change option
- Logout button

## 🎨 Frontend Stack

- **Framework**: Django 5.2
- **CSS**: Bootstrap 5.3 + Custom CSS
- **JavaScript**: Vanilla JS + Web APIs
- **Icons**: Bootstrap Icons
- **Maps**: Custom mapping and navigation system
- **Chat**: Custom AI chatbot engine
- **Database**: SQLite with Django ORM

## 🔐 Security Features

- CSRF protection on all forms
- SQL injection prevention (Django ORM)
- XSS protection (Django templates)
- CORS configuration
- Authentication required for sensitive operations
- Password hashing (Django default)

## 📊 Sample Data

The `load_sample_data` command creates:
- **5 Tourist Places**: Krishna Janmabhoomi, Dwarkadhish, Vishram Ghat, Museum, Kusum Sarovar
- **5 Services**: Guest house, Hotels, Restaurants, Transport, Cafe
- **2 Test Users**: admin (superuser) and tourist (regular user)

## 🛠️ Admin Panel

Access at: http://localhost:8000/admin/

Login with your superuser credentials.

**Manage**:
- Tourist Places
- Reviews
- Local Services
- Bookings
- Notifications
- Favorites
- User Profiles

## 🌐 Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn mathura_tourism.wsgi:application --bind 0.0.0.0:8000
```

### Production Settings
1. Set `DEBUG=False` in `.env`
2. Update `SECRET_KEY` with a secure random string
3. Update `ALLOWED_HOSTS` with your domain
4. Use PostgreSQL instead of SQLite
5. Enable HTTPS/SSL
6. Set up proper CORS origins
7. Use environment-based settings

## 📝 Environment Variables Reference

```
DEBUG                  - Development mode (True/False)
SECRET_KEY            - Django secret key
ALLOWED_HOSTS         - Comma-separated allowed hosts
DATABASE_ENGINE       - Database engine (default: SQLite)
DATABASE_NAME         - Database name/path
CORS_ALLOWED_ORIGINS  - CORS allowed domains
```

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'dotenv'`
**Solution**: Run `pip install python-dotenv`

### Issue: Maps not displaying correctly
**Solution**: Ensure JavaScript is enabled in your browser and the mapping module is loaded

### Issue: Chatbot not responding
**Solution**: Check that the chatbot service is running and database is initialized

### Issue: Images not uploading
**Solution**: Ensure `media/` folder exists and is writable

### Issue: Static files not loading
**Solution**: Run `python manage.py collectstatic`

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Python Documentation](https://docs.python.org/)

## 📄 License

This project is open source and available for educational and commercial use.

## 🤝 Contributing

Feel free to fork and submit pull requests for any improvements.

## 📞 Support

For issues or questions, check the troubleshooting section or create an issue in the repository.

---

**Happy Tourism Exploring! 🏛️✨**

Built with ❤️ for Mathura Tourism
