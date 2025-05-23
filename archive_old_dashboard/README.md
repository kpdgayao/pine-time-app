# [ARCHIVED] Pine Time Admin Dashboard

**IMPORTANT: This is an archived version of the old Streamlit-based admin dashboard. It has been replaced by the React-based admin dashboard in the `pine-time-admin` directory.**

This code is kept for reference purposes only and should not be used for new development.

## Original Features

1. **Authentication**: JWT token handling and role-based access control
2. **Dashboard Overview**: Key metrics and summary information
3. **Event Management**: CRUD operations for events, check-ins management
4. **User Management**: Profile editing, points adjustment, badge progress tracking
5. **Analytics**: Event popularity, user engagement, and points distribution visualizations

## Project Structure

```python
archive_old_dashboard/   # Previously admin_dashboard/
├── app.py                # Main Streamlit app with navigation
├── config.py             # Configuration settings
├── utils/
│   ├── auth.py           # JWT handling and session management
│   ├── api.py            # API connection functions
│   ├── postgres_utils.py # PostgreSQL utilities
│   └── db.py             # Database connection utilities
└── pages/                # Different dashboard sections
    ├── dashboard.py      # Main dashboard overview
    ├── events.py         # Event management
    ├── users.py          # User management
    └── analytics.py      # Analytics visualizations
```

## Migration Notes

The Streamlit admin dashboard has been replaced with a React-based admin dashboard that provides:

1. Better UI/UX consistency with the user frontend (also React-based)
2. Improved performance and responsiveness
3. Centralized theming and styling
4. More robust error handling and state management
5. Better developer experience with TypeScript

For new development, please refer to the `pine-time-admin` directory.

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
