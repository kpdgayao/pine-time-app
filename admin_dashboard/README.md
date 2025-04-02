# Pine Time Admin Dashboard

A comprehensive admin dashboard for the Pine Time Experience platform built with Streamlit.

## Features

1. **Authentication**: Secure login with JWT token handling and role-based access control
2. **Dashboard Overview**: Key metrics and summary information
3. **Event Management**: Create, read, update, and delete events, manage check-ins and completions
4. **User Management**: Edit user profiles, adjust points, and view badge progress
5. **Analytics**: Visualize event popularity, user engagement, and points distribution

## Project Structure

```python
admin_dashboard/
├── app.py              # Main Streamlit app with navigation
├── config.py           # Configuration settings
├── requirements.txt    # Dependencies
├── utils/
│   ├── auth.py         # JWT handling and session management
│   └── api.py          # API connection functions
└── pages/              # Different dashboard sections
    ├── dashboard.py    # Main dashboard overview
    ├── events.py       # Event management
    ├── users.py        # User management
    └── analytics.py    # Analytics visualizations
```

## Setup and Installation

1. Make sure you have Python 3.8+ installed

2. Install the required dependencies:

   ```bash
   cd admin_dashboard
   pip install -r requirements.txt
   ```

3. Configure the API endpoint in `config.py` to point to your FastAPI backend:

   ```python
   API_BASE_URL = "http://localhost:8000"  # Change this to your FastAPI backend URL
   ```

## Running the Dashboard

Start the Streamlit application:

```bash
cd admin_dashboard
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Authentication

The dashboard uses JWT tokens for authentication with the FastAPI backend. Only users with admin role can access the dashboard. The authentication flow includes:

- JWT token acquisition and storage
- Automatic token refresh before expiry
- Secure token verification
- Role-based access control (admin only)
- Session timeout management

## API Integration

The dashboard connects to the Pine Time FastAPI backend through a robust API client that handles:

### API Connection Layer

- Centralized API client with consistent error handling
- JWT token management (storage, refresh, expiry)
- Request retries with exponential backoff
- Loading state indicators during API calls
- Response processing and validation

### Data Integration Points

The dashboard integrates with the following API endpoints:

- **Authentication**: `/auth/token`, `/auth/refresh`, `/auth/verify`
- **User Management**: `/users/*` endpoints for profile management and points adjustment
- **Event Management**: `/events/*` endpoints for CRUD operations and check-ins
- **Points & Badges**: `/points/*`, `/badges/*`, `/leaderboard` for rewards tracking
- **Analytics**: Various endpoints for data visualization

### Error Handling & UX

- Loading indicators during API calls
- Proper error messaging for failed requests
- Success confirmations for operations
- Fallback to sample data when API is unavailable
- Responsive UI during data loading

## Pagination and Caching

The dashboard implements:

- Streamlit's caching to minimize API calls
- Proper pagination for lists of events and users
- Cache invalidation when data is modified

## Customization

You can customize the dashboard appearance by modifying the theme settings in `config.py` and the CSS in `app.py`.

## Troubleshooting

If you encounter connection issues:

1. Verify the FastAPI backend is running
2. Check the `API_BASE_URL` in `config.py`
3. Ensure your network allows connections to the API
4. Check the console logs for detailed error messages
