# Pine Time Experience Baguio

A web application for Pine Time Experience Baguio, a community that hosts trivia nights, murder mysteries, and game nights in Baguio City. The app connects locals with local businesses and artisans.

## Features

- **User Authentication**: Registration, login/logout with JWT token management
- **Event Management**: Create, discover, and register for events
- **Multi-level Badge System**: Bronze, silver, and gold badges across different categories
- **Points & Rewards**: Track points, view leaderboards, and earn rewards
- **Streak Tracking**: Rewards for consistent weekly attendance
- **Admin Dashboard**: Comprehensive tools for managing users, events, and analytics
- **User Interface**: Mobile-friendly design with intuitive navigation
- **Demo Mode**: Test the application without backend connection

## Project Structure

```
pine-time-app/
├── admin_dashboard/       # Streamlit frontend applications
│   ├── pages/             # Dashboard page components
│   ├── utils/             # Utility modules (auth, API, DB)
│   ├── app.py             # Admin dashboard entry point
│   └── user_app.py        # User interface entry point
├── app/                   # FastAPI backend
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── db/                # Database setup
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── main.py            # Backend entry point
├── .env.example           # Example environment variables
└── requirements.txt       # Backend dependencies
```

## Tech Stack

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: Streamlit
- **Authentication**: JWT-based auth system
- **Styling**: Custom CSS with Pine Time green theme (#2E7D32)

## Setup Instructions

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pine-time-app.git
   cd pine-time-app
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

6. Run the FastAPI backend:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the admin_dashboard directory:
   ```bash
   cd admin_dashboard
   ```

2. Install frontend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the admin dashboard:
   ```bash
   streamlit run app.py
   ```

4. Run the user interface:
   ```bash
   streamlit run user_app.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./pine_time.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/pine_time

# JWT Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_BASE_URL=http://localhost:8000
```

## Demo Mode

The application includes a demo mode for testing without a backend connection:

1. For the user interface, check the "Use demo login" box on the login page
2. For the admin dashboard, use the demo credentials:
   - Username: admin
   - Password: admin

## Error Handling and Resilience

The application implements robust error handling and resilience patterns:

- API error handling with custom exception classes
- Fallback mechanisms with sample data generation
- Graceful degradation when services are impaired
- Comprehensive user feedback for error conditions

## Database Integration

The application supports both SQLite and PostgreSQL:

- SQLite for development and testing
- PostgreSQL for production environments
- Connection pooling with configurable parameters
- ORM implementation with SQLAlchemy

## Authentication System

The authentication system includes:

- JWT token management (acquisition, storage, refresh)
- Role-based access control (admin vs. regular users)
- Session timeout management
- Secure token handling with proper validation

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

MIT