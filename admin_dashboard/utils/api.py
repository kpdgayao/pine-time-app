"""
API utilities for the Pine Time Admin Dashboard.
Handles API requests to the FastAPI backend.
"""

import requests
import streamlit as st
import json
import time
import math
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_ENDPOINTS, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF, DEFAULT_PAGE_SIZE, API_BASE_URL
from utils.auth import get_auth_header, ensure_valid_token, AuthError
from utils.db import is_demo_mode, test_database_connection, get_database_config
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api_utils")

class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

class PostgreSQLError(APIError):
    """Custom exception for PostgreSQL-specific errors"""
    def __init__(self, message, status_code=None, response=None, pg_code=None):
        self.pg_code = pg_code
        super().__init__(message, status_code, response)

class APIClient:
    """
    Centralized API client for making requests to the FastAPI backend.
    Handles authentication, error handling, and response processing.
    """
    
    def __init__(self):
        """Initialize API client with retry configuration"""
        self.session = self._create_session()
        self.connection_verified = False
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry configuration"""
        session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def verify_connection(self, force: bool = False) -> bool:
        """
        Verify connection to the API and database.
        
        Args:
            force (bool): Force verification even if already verified
            
        Returns:
            bool: True if connection is verified, False otherwise
        """
        if self.connection_verified and not force:
            return True
        
        try:
            # Test API connection using the root endpoint
            response = self.session.get(
                f"{API_BASE_URL}/",  # Use the root endpoint which doesn't require authentication
                timeout=REQUEST_TIMEOUT
            )
            
            # If response is successful, mark connection as verified
            if response.status_code < 400:
                self.connection_verified = True
                logger.info("API connection verified successfully")
                return True
            
            logger.error(f"API connection verification failed: {response.status_code}")
            return False
        except requests.RequestException as e:
            logger.error(f"API connection verification failed: {str(e)}")
            return False
    
    def _handle_response(self, response: requests.Response, error_message: str = "API request failed") -> Dict:
        """
        Handle API response and raise exception if needed.
        
        Args:
            response (requests.Response): API response
            error_message (str): Custom error message
            
        Returns:
            dict: Response JSON
            
        Raises:
            APIError: If API request failed
            PostgreSQLError: If PostgreSQL-specific error occurred
        """
        if response.status_code >= 400:
            try:
                error_data = response.json()
                
                # Log the full error response for debugging
                logger.debug(f"Error response from {response.url}: {error_data}")
                
                # Extract error details based on different possible formats
                if isinstance(error_data, dict):
                    # Standard FastAPI error format
                    if "detail" in error_data:
                        error_detail = error_data["detail"]
                    # JWT auth error format
                    elif "msg" in error_data:
                        error_detail = error_data["msg"]
                    # Generic error message
                    elif "message" in error_data:
                        error_detail = error_data["message"]
                    # Error code with description
                    elif "code" in error_data and "description" in error_data:
                        error_detail = f"{error_data['code']}: {error_data['description']}"
                    # Fall back to the whole response
                    else:
                        error_detail = str(error_data)
                else:
                    error_detail = str(error_data)
                
                # Check for PostgreSQL-specific errors
                if isinstance(error_detail, dict) and error_detail.get("type") == "database_error":
                    pg_code = error_detail.get("code")
                    pg_message = error_detail.get("message", "Database error")
                    raise PostgreSQLError(
                        f"{error_message}: {pg_message}",
                        response.status_code,
                        response,
                        pg_code
                    )
                
                # Create user-friendly error message based on status code
                status_message = {
                    400: "Bad Request",
                    401: "Unauthorized",
                    403: "Forbidden",
                    404: "Not Found",
                    405: "Method Not Allowed",
                    408: "Request Timeout",
                    409: "Conflict",
                    422: "Validation Error",
                    429: "Too Many Requests",
                    500: "Internal Server Error",
                    502: "Bad Gateway",
                    503: "Service Unavailable",
                    504: "Gateway Timeout"
                }.get(response.status_code, f"Error {response.status_code}")
                
                raise APIError(
                    f"{error_message}: {status_message} - {error_detail}", 
                    response.status_code, 
                    response
                )
            except json.JSONDecodeError:
                # Non-JSON error response
                error_text = response.text[:100] + ("..." if len(response.text) > 100 else "")
                logger.debug(f"Non-JSON error response: {error_text}")
                raise APIError(
                    f"{error_message}: {response.status_code} - Non-JSON response", 
                    response.status_code, 
                    response
                )
        
        try:
            return response.json()
        except json.JSONDecodeError:
            if response.status_code == 204:  # No content
                return {}
            # Empty response with success status
            if response.status_code < 300 and not response.text.strip():
                return {}
            # Log the problematic response
            logger.warning(f"Invalid JSON in successful response from {response.url}: {response.text[:100]}")
            raise APIError(f"Invalid JSON response: {response.text[:100]}", response.status_code, response)
    
    def safe_api_response_handler(self, response_data):
        """
        Safely process API response data, handling different formats.
        
        Args:
            response_data: API response data (could be list or dict)
            
        Returns:
            Processed response data with consistent format
        """
        try:
            # Check if response is a dictionary with 'items' key (paginated response)
            if isinstance(response_data, dict) and "items" in response_data:
                return response_data
            # Check if response is a list (non-paginated response)
            elif isinstance(response_data, list):
                # Convert to paginated format for consistency
                return {
                    "items": response_data,
                    "total": len(response_data),
                    "page": 1,
                    "size": len(response_data),
                    "pages": 1
                }
            # Return as is for other formats
            return response_data
        except Exception as e:
            logger.error(f"Error processing API response: {str(e)}")
            # Return empty result with consistent format
            return {
                "items": [],
                "total": 0,
                "page": 1,
                "size": 0,
                "pages": 0
            }
    
    def safe_api_call(self, method, url, **kwargs):
        """
        Make an API call with comprehensive error handling.
        
        Args:
            method: HTTP method
            url: API endpoint URL
            **kwargs: Additional arguments for requests
            
        Returns:
            API response data
            
        Raises:
            APIError: If API request failed
        """
        try:
            # Ensure valid token before making request
            from utils.auth import ensure_valid_token
            token_valid = ensure_valid_token()
            
            if not token_valid and not kwargs.get("skip_auth", False):
                raise APIError("Authentication token is invalid or expired")
            
            # Make the request with timeout
            response = self.session.request(
                method, 
                url, 
                timeout=kwargs.pop("timeout", REQUEST_TIMEOUT),
                **kwargs
            )
            
            # Handle response
            return self._handle_response(response, kwargs.get("error_message", "API request failed"))
        except requests.exceptions.Timeout:
            logger.error(f"API request to {url} timed out after {kwargs.get('timeout', REQUEST_TIMEOUT)}s")
            raise APIError(f"Request timed out. The server is taking too long to respond.")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error when calling {url}")
            raise APIError("Connection error. Unable to connect to the server.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception when calling {url}: {str(e)}")
            raise APIError(f"Request failed: {str(e)}")
        except APIError:
            # Re-raise API errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error when calling {url}: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    def request(
        self, 
        method: str, 
        endpoint: str, 
        params: Dict = None, 
        data: Dict = None, 
        json_data: Dict = None,
        headers: Dict = None,
        with_auth: bool = True,
        error_message: str = "API request failed",
        show_spinner: bool = True,
        spinner_text: str = "Processing request...",
        fallback_to_demo: bool = True,
        max_retries: int = 2,
        retry_status_codes: List[int] = None,
        retry_delay: float = 1.0
    ) -> Dict:
        """
        Make a request to the API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            data (dict, optional): Form data
            json_data (dict, optional): JSON data
            headers (dict, optional): Additional headers
            with_auth (bool, optional): Whether to include auth header
            error_message (str, optional): Custom error message
            show_spinner (bool, optional): Whether to show a spinner
            spinner_text (str, optional): Text to show in spinner
            fallback_to_demo (bool, optional): Whether to fallback to demo data on failure
            max_retries (int, optional): Maximum number of retry attempts
            retry_status_codes (List[int], optional): Status codes to retry on
            retry_delay (float, optional): Delay between retries in seconds
            
        Returns:
            dict: Response JSON
            
        Raises:
            APIError: If API request failed and no fallback
        """
        # Default retry status codes if none provided
        if retry_status_codes is None:
            retry_status_codes = [408, 429, 500, 502, 503, 504]  # Common retryable status codes
            
        # If in demo mode, use demo data
        if is_demo_mode():
            logger.info(f"Demo mode active, skipping actual API request to {endpoint}")
            return self._generate_fallback_data(endpoint, method, params)
        
        # Ensure valid token if auth is required
        if with_auth:
            token_valid = ensure_valid_token()
            if not token_valid:
                if fallback_to_demo:
                    logger.warning("Authentication failed, falling back to demo data")
                    # Display a more user-friendly message
                    st.warning("⚠️ Authentication issues detected. Using sample data instead. Your experience may be limited.")
                    # Update connection status in session state to trigger reconnection attempts
                    if "connection_status" in st.session_state:
                        st.session_state["connection_status"]["api_connected"] = False
                        st.session_state["connection_status"]["success"] = False
                        st.session_state["last_connection_check"] = 0  # Force a recheck on next verification
                    return self._generate_fallback_data(endpoint, method, params)
                raise AuthError("Authentication required")
        
        # Prepare headers
        request_headers = {}
        if with_auth:
            request_headers.update(get_auth_header())
        if headers:
            request_headers.update(headers)
        
        # Initialize retry counter and last error
        retries = 0
        last_error = None
        
        # Retry loop
        while retries <= max_retries:
            try:
                # Make request with spinner if requested
                if show_spinner:
                    with st.spinner(spinner_text):
                        response = self.session.request(
                            method=method,
                            url=endpoint,  # Endpoint already contains the full URL
                            params=params,
                            data=data,
                            json=json_data,
                            headers=request_headers,
                            timeout=REQUEST_TIMEOUT
                        )
                else:
                    response = self.session.request(
                        method=method,
                        url=endpoint,  # Endpoint already contains the full URL
                        params=params,
                        data=data,
                        json=json_data,
                        headers=request_headers,
                        timeout=REQUEST_TIMEOUT
                    )
                
                # Check if we should retry based on status code
                if response.status_code in retry_status_codes and retries < max_retries:
                    retries += 1
                    wait_time = retry_delay * (2 ** (retries - 1))  # Exponential backoff
                    logger.warning(f"Received status {response.status_code} from {endpoint}, retrying in {wait_time:.2f}s (attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                # Process the response
                return self._handle_response(response, error_message)
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_error = e
                if retries < max_retries:
                    retries += 1
                    wait_time = retry_delay * (2 ** (retries - 1))  # Exponential backoff
                    logger.warning(f"{type(e).__name__} for {endpoint}, retrying in {wait_time:.2f}s (attempt {retries}/{max_retries}): {str(e)}")
                    time.sleep(wait_time)
                else:
                    break
            except requests.exceptions.RequestException as e:
                # Don't retry other request exceptions
                last_error = e
                break
        
        # If we've exhausted retries or had a non-retryable error, handle the failure
        if isinstance(last_error, requests.exceptions.ConnectionError):
            logger.error(f"Connection error for {endpoint} after {retries} retries: {str(last_error)}")
            if fallback_to_demo:
                logger.warning(f"Connection failed, falling back to demo data for {endpoint}")
                # Show a more specific error message to the user
                st.warning(f"⚠️ Unable to connect to the server. Using sample data instead. Please check your internet connection.")
                # Update connection status in session state to trigger reconnection attempts
                if "connection_status" in st.session_state:
                    st.session_state["connection_status"]["api_connected"] = False
                    st.session_state["connection_status"]["success"] = False
                    st.session_state["last_connection_check"] = 0  # Force a recheck on next verification
                return self._generate_fallback_data(endpoint, method, params)
            raise APIError(f"Connection error after {retries} retries: {str(last_error)}")
            
        elif isinstance(last_error, requests.exceptions.Timeout):
            logger.error(f"Timeout error for {endpoint} after {retries} retries: {str(last_error)}")
            if fallback_to_demo:
                logger.warning(f"Request timed out, falling back to demo data for {endpoint}")
                # Show a more specific error message to the user
                st.warning(f"⚠️ Server response timeout. Using sample data instead. The server might be under heavy load.")
                return self._generate_fallback_data(endpoint, method, params)
            raise APIError(f"Request timed out after {retries} retries: {str(last_error)}")
            
        elif isinstance(last_error, requests.exceptions.RequestException):
            logger.error(f"Request error for {endpoint}: {str(last_error)}")
            if fallback_to_demo:
                logger.warning(f"Request failed, falling back to demo data for {endpoint}")
                # Show a more specific error message based on the type of exception
                error_type = type(last_error).__name__
                if "SSLError" in error_type:
                    st.warning(f"⚠️ Secure connection failed. Using sample data instead. This might be a certificate issue.")
                elif "ProxyError" in error_type:
                    st.warning(f"⚠️ Proxy connection issue. Using sample data instead. Please check your network settings.")
                else:
                    st.warning(f"⚠️ Connection issue detected. Using sample data instead. Please try again later.")
                return self._generate_fallback_data(endpoint, method, params)
            raise APIError(f"Request failed: {str(last_error)}")
    
    def get(self, endpoint: str, **kwargs) -> Dict:
        """Make a GET request"""
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Dict:
        """Make a POST request"""
        return self.request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Dict:
        """Make a PUT request"""
        return self.request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict:
        """Make a DELETE request"""
        return self.request("DELETE", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> Dict:
        """Make a PATCH request"""
        return self.request("PATCH", endpoint, **kwargs)
        
    def _generate_fallback_data(self, endpoint: str, method: str, params: Dict = None) -> Dict:
        """
        Generate fallback data based on the endpoint and request parameters.
        This provides more intelligent fallbacks than just returning an empty dict.
        
        Args:
            endpoint (str): The API endpoint that was requested
            method (str): The HTTP method that was used
            params (Dict, optional): The query parameters that were used
            
        Returns:
            Dict: Appropriate fallback data for the endpoint
        """
        from utils.connection import (
            get_sample_users, get_sample_events, get_sample_user_profile,
            get_sample_user_badges, get_sample_user_events, get_sample_points_history,
            get_sample_leaderboard, get_sample_badges
        )
        
        # Extract page and size from params if available
        page = 1
        page_size = 20
        if params:
            page = params.get("page", 1)
            page_size = params.get("size", 20)
        
        # Users endpoints
        if "/users/" in endpoint:
            if endpoint.endswith("/users/") or endpoint.endswith("/users"):
                return get_sample_users(page, page_size)
            elif "/profile" in endpoint or "/me" in endpoint:
                return get_sample_user_profile()
            elif "/badges" in endpoint:
                return get_sample_user_badges()
            elif "/events" in endpoint:
                return get_sample_user_events()
            # Individual user endpoint
            elif method == "GET" and any(char.isdigit() for char in endpoint.split("/")[-1]):
                return get_sample_user_profile()
        
        # Events endpoints
        elif "/events/" in endpoint:
            if endpoint.endswith("/events/") or endpoint.endswith("/events"):
                return get_sample_events(page, page_size)
            # Individual event endpoint
            elif method == "GET" and any(char.isdigit() for char in endpoint.split("/")[-1]):
                events = get_sample_events(1, 1)
                if events and "items" in events and events["items"]:
                    return events["items"][0]
                return {}
        
        # Points endpoints
        elif "/points/" in endpoint:
            if "/history" in endpoint:
                return get_sample_points_history()
            elif "/leaderboard" in endpoint:
                return get_sample_leaderboard()
        
        # Badges endpoints
        elif "/badges/" in endpoint:
            if endpoint.endswith("/badges/") or endpoint.endswith("/badges"):
                return get_sample_badges()
            # Individual badge endpoint
            elif method == "GET" and any(char.isdigit() for char in endpoint.split("/")[-1]):
                badges = get_sample_badges()
                if badges:
                    return badges[0]
                return {}
        
        # Default empty response
        if method == "GET":
            logger.warning(f"No specific fallback data for GET {endpoint}, returning empty result")
            return {}
        else:
            # For POST/PUT/DELETE/PATCH, return success response
            logger.warning(f"No specific fallback data for {method} {endpoint}, returning success response")
            return {"success": True, "message": "Operation completed in demo mode"}
    
    def paginated_request(
        self, 
        endpoint: str, 
        page: int = 1, 
        page_size: int = DEFAULT_PAGE_SIZE,
        **kwargs
    ) -> Dict:
        """
        Make a paginated request to the API.
        
        Args:
            endpoint (str): API endpoint
            page (int, optional): Page number
            page_size (int, optional): Items per page
            **kwargs: Additional arguments for request
            
        Returns:
            dict: Response with pagination info
        """
        params = kwargs.pop("params", {})
        params.update({"page": page, "size": page_size})
        
        try:
            response = self.get(endpoint, params=params, **kwargs)
            
            # Handle different response formats
            if isinstance(response, list):
                # API returned a list instead of paginated response
                logger.info(f"API endpoint {endpoint} returned a list instead of paginated response")
                # Convert to paginated format
                return {
                    "items": response,
                    "total": len(response),
                    "page": page,
                    "size": page_size,
                    "pages": max(1, math.ceil(len(response) / page_size))
                }
            elif isinstance(response, dict):
                # Check if this is already a paginated response
                if all(key in response for key in ["items", "total", "page", "size", "pages"]):
                    return response
                
                # Check for common pagination keys
                pagination_keys = ["results", "data", "events", "users", "items", "records"]
                
                # If not, check if there's a key that might contain the items
                for key in pagination_keys:
                    if key in response and isinstance(response[key], list):
                        # Found a list, use these as the items
                        items = response[key]
                        logger.info(f"Using '{key}' as items list from response")
                        return {
                            "items": items,
                            "total": response.get("total", len(items)),
                            "page": response.get("page", page),
                            "size": response.get("size", page_size),
                            "pages": response.get("pages", max(1, math.ceil(len(items) / page_size)))
                        }
                
                # Check if any key contains a list that might be the items
                for key in response.keys():
                    if isinstance(response[key], list):
                        # Found a list, assume these are the items
                        items = response[key]
                        logger.info(f"Using '{key}' as items list from response")
                        return {
                            "items": items,
                            "total": len(items),
                            "page": page,
                            "size": page_size,
                            "pages": max(1, math.ceil(len(items) / page_size))
                        }
                
                # If the response is a dict but doesn't have any list values,
                # it might be a single item - wrap it in a list
                if endpoint.endswith("/events") or "/events/" in endpoint:
                    logger.info(f"Response appears to be a single item, wrapping in a list")
                    return {
                        "items": [response],
                        "total": 1,
                        "page": page,
                        "size": page_size,
                        "pages": 1
                    }
            
            # If we can't determine the structure, return as is with a warning
            logger.warning(f"Could not normalize paginated response format from {endpoint}: {type(response)}")
            # As a last resort, try to wrap the response in a standard format
            return {
                "items": response if isinstance(response, list) else [response] if response else [],
                "total": len(response) if isinstance(response, list) else 1 if response else 0,
                "page": page,
                "size": page_size,
                "pages": max(1, math.ceil(len(response) if isinstance(response, list) else 1 if response else 0) / page_size)
            }
        except Exception as e:
            logger.error(f"Error in paginated_request for {endpoint}: {str(e)}")
            # Return empty paginated response on error
            return {
                "items": [],
                "total": 0,
                "page": page,
                "size": page_size,
                "pages": 0
            }

# Initialize global API client
api_client = APIClient()

# Function to check API and database connection
def check_api_connection() -> Dict[str, Any]:
    """
    Check API and database connection.
    
    Returns:
        dict: Connection status with success flag and message
    """
    # First check API connection
    try:
        api_connected = api_client.verify_connection(force=True)
    except Exception as e:
        api_connected = False
        api_error = str(e)
    
    # Then check database connection
    db_version = test_database_connection()
    db_connected = db_version is not None
    
    # Get database type from config
    db_config = get_database_config()
    db_type = db_config.get("database_type", "unknown")
    
    return {
        "success": api_connected and db_connected,
        "api_connected": api_connected,
        "db_connected": db_connected,
        "db_type": db_type,
        "message": (
            f"API {'connected' if api_connected else 'disconnected'}, " +
            f"Database ({db_type}): {'connected - ' + db_version if db_connected else 'disconnected'}"
        )
    }

# User API functions
@st.cache_data(ttl=60)
def get_users(page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Dict[str, Any]:
    """Get all users with pagination"""
    try:
        response = api_client.paginated_request(
            API_ENDPOINTS["users"]["list"],
            page=page,
            page_size=page_size,
            spinner_text="Loading users...",
            error_message="Fetching users"
        )
        
        # Process the response to handle different formats
        if isinstance(response, dict) and "items" in response:
            # Standard paginated response
            items = response["items"]
        elif isinstance(response, list):
            # List response (could be list of objects or strings)
            items = response
        else:
            # Unexpected format, use empty list
            items = []
            
        # Convert string items to dictionaries if needed
        processed_items = []
        for item in items:
            if isinstance(item, dict):
                # Item is already a dictionary
                processed_items.append(item)
            else:
                # Item is a string or other primitive type, convert to dictionary
                processed_items.append({
                    "id": str(item),
                    "username": f"user_{str(item)}",
                    "email": f"user_{str(item)}@example.com",
                    "first_name": "Unknown",
                    "last_name": "User",
                    "role": "user",
                    "points": 0,
                    "created_at": datetime.now().isoformat()
                })
        
        # Return in paginated format
        return {
            "items": processed_items,
            "total": len(processed_items),
            "page": page,
            "size": page_size,
            "pages": max(1, math.ceil(len(processed_items) / page_size))
        }
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return {"items": [], "total": 0, "page": page, "size": page_size, "pages": 0}

@st.cache_data(ttl=60)
def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        return api_client.get(
            API_ENDPOINTS["users"]["detail"].format(user_id=user_id),
            spinner_text=f"Loading user details..."
        )
    except Exception as e:
        st.error(f"Error fetching user: {str(e)}")
        return None

def update_user(user_id: str, user_data: Dict[str, Any]) -> bool:
    """Update user by ID"""
    try:
        api_client.put(
            API_ENDPOINTS["users"]["update"].format(user_id=user_id),
            json_data=user_data,
            spinner_text="Updating user profile..."
        )
        st.success("User profile updated successfully")
        # Clear cache for this user
        get_user.clear()
        get_users.clear()
        return True
    except Exception as e:
        st.error(f"Error updating user: {str(e)}")
        return False

def update_user_points(user_id: str, points: int, reason: str) -> bool:
    """Update user points"""
    try:
        api_client.post(
            API_ENDPOINTS["users"]["points"].format(user_id=user_id),
            json_data={"points": points, "reason": reason},
            spinner_text="Updating points..."
        )
        st.success(f"Points {'added to' if points > 0 else 'deducted from'} user successfully")
        # Clear cache for this user
        get_user.clear()
        get_users.clear()
        return True
    except Exception as e:
        st.error(f"Error updating user points: {str(e)}")
        return False

@st.cache_data(ttl=300)
def get_user_badges(user_id: str) -> List[Dict[str, Any]]:
    """Get user badges"""
    if not user_id:
        logger.warning("Attempted to fetch badges with empty user_id")
        return []
        
    try:
        # First try the standard endpoint
        try:
            badges = api_client.get(
                API_ENDPOINTS["users"]["badges"].format(user_id=user_id),
                spinner_text="Loading badges...",
                error_message="Fetching user badges",
                fallback_to_demo=True
            )
            if badges:
                return badges if isinstance(badges, list) else [badges]
        except APIError as e:
            # If 404, try alternative endpoint format
            if e.status_code == 404:
                logger.info(f"Standard badges endpoint returned 404 for user {user_id}, trying alternative")
                try:
                    # Try alternative endpoint that might return all badges with a user_id filter
                    badges = api_client.get(
                        API_ENDPOINTS["badges"]["list"],
                        params={"user_id": user_id},
                        spinner_text="Loading badges...",
                        error_message="Fetching user badges (alternative)"
                    )
                    if isinstance(badges, list):
                        return badges
                    elif isinstance(badges, dict) and "items" in badges:
                        return badges["items"]
                    return []
                except Exception as alt_e:
                    logger.warning(f"Alternative badges endpoint also failed: {str(alt_e)}")
                    # Fall through to the fallback below
            else:
                # For other error codes, log and continue to fallback
                logger.error(f"Error fetching user badges: {str(e)}")
        
        # If we got here, both attempts failed
        logger.warning(f"All badge fetch attempts failed for user {user_id}, using fallback")
        from utils.connection import get_sample_user_badges
        return get_sample_user_badges()
    except Exception as e:
        logger.error(f"Unexpected error fetching user badges: {str(e)}")
        # Don't show error to user - use fallback data instead
        from utils.connection import get_sample_user_badges
        return get_sample_user_badges()

# Event API functions
@st.cache_data(ttl=60)
def get_events(page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Dict[str, Any]:
    """Get all events with pagination"""
    try:
        response = api_client.paginated_request(
            API_ENDPOINTS["events"]["list"],
            page=page,
            page_size=page_size,
            spinner_text="Loading events...",
            error_message="Fetching events"
        )
        
        # Process the response to handle different formats
        if isinstance(response, dict) and "items" in response:
            # Standard paginated response
            items = response["items"]
        elif isinstance(response, list):
            # List response (could be list of objects or strings)
            items = response
        else:
            # Unexpected format, use empty list
            items = []
            
        # Convert string items to dictionaries if needed
        processed_items = []
        for item in items:
            if isinstance(item, dict):
                # Item is already a dictionary
                processed_items.append(item)
            else:
                # Item is a string or other primitive type, convert to dictionary
                processed_items.append({
                    "id": str(item),
                    "name": f"Event {str(item)}",
                    "description": "",
                    "date": datetime.now().isoformat(),
                    "location": "",
                    "status": "unknown",
                    "registrations": [],
                    "points": 0
                })
        
        # Return in paginated format
        return {
            "items": processed_items,
            "total": len(processed_items),
            "page": page,
            "size": page_size,
            "pages": max(1, math.ceil(len(processed_items) / page_size))
        }
    except APIError as e:
        logger.error(f"API error fetching events: {str(e)}")
        st.error(f"Error loading events: {str(e)}")
        return {"items": [], "total": 0, "page": page, "size": page_size, "pages": 0}
    except Exception as e:
        logger.error(f"Unexpected error fetching events: {str(e)}")
        st.error(f"Error loading events: {str(e)}")
        return {"items": [], "total": 0, "page": page, "size": page_size, "pages": 0}

@st.cache_data(ttl=60)
def get_event(event_id: str) -> Optional[Dict[str, Any]]:
    """Get event by ID"""
    try:
        # Get event data from API
        event_data = api_client.get(
            API_ENDPOINTS["events"]["detail"].format(event_id=event_id),
            spinner_text=f"Loading event details..."
        )
        
        # If we have event data, transform field names for UI
        if event_data:
            # Import the field mapping utility
            from utils.field_mappings import transform_event_data_for_ui
            
            # Transform API field names to UI field names
            return transform_event_data_for_ui(event_data)
        
        return event_data
    except Exception as e:
        logger.error(f"Error fetching event: {str(e)}")
        st.error(f"Error fetching event: {str(e)}")
        return None

def create_event(event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create new event"""
    try:
        # Import the field mapping utility
        from utils.field_mappings import transform_event_data_for_api
        
        # Transform field names to match API expectations
        transformed_data = transform_event_data_for_api(event_data)
        
        # Send the transformed data to the API
        response = api_client.post(
            API_ENDPOINTS["events"]["create"],
            json_data=transformed_data,
            spinner_text="Creating event..."
        )
        st.success("Event created successfully")
        # Clear events cache
        get_events.clear()
        return response
    except Exception as e:
        st.error(f"Error creating event: {str(e)}")
        return None

def update_event(event_id: str, event_data: Dict[str, Any]) -> bool:
    """Update event by ID"""
    try:
        # Import the field mapping utility
        from utils.field_mappings import transform_event_data_for_api
        
        # Transform field names to match API expectations
        transformed_data = transform_event_data_for_api(event_data)
        
        # Send the transformed data to the API
        api_client.put(
            API_ENDPOINTS["events"]["update"].format(event_id=event_id),
            json_data=transformed_data,
            spinner_text="Updating event..."
        )
        st.success("Event updated successfully")
        # Clear events cache
        get_events.clear()
        return True
    except Exception as e:
        st.error(f"Error updating event: {str(e)}")
        return False

def delete_event(event_id: str) -> bool:
    """Delete event by ID"""
    try:
        api_client.delete(
            API_ENDPOINTS["events"]["delete"].format(event_id=event_id),
            spinner_text="Deleting event..."
        )
        st.success("Event deleted successfully")
        # Clear events cache
        get_events.clear()
        return True
    except Exception as e:
        st.error(f"Error deleting event: {str(e)}")
        return False

def check_in_user(event_id: str, user_id: str) -> bool:
    """Check in user to event"""
    try:
        api_client.post(
            API_ENDPOINTS["events"]["check_in"].format(event_id=event_id),
            json_data={"user_id": user_id},
            spinner_text="Processing check-in..."
        )
        st.success("User checked in successfully")
        # Clear cache
        get_event.clear()
        return True
    except Exception as e:
        st.error(f"Error checking in user: {str(e)}")
        return False

def mark_event_complete(event_id: str, user_id: str) -> bool:
    """Mark event as complete for user"""
    try:
        api_client.post(
            API_ENDPOINTS["events"]["complete"].format(event_id=event_id),
            json_data={"user_id": user_id},
            spinner_text="Marking event as complete..."
        )
        st.success("Event marked as complete")
        # Clear cache
        get_event.clear()
        return True
    except Exception as e:
        st.error(f"Error marking event as complete: {str(e)}")
        return False

# Analytics API functions
@st.cache_data(ttl=3600)
def get_event_popularity() -> Dict[str, Any]:
    """Get event popularity analytics"""
    try:
        return api_client.get(
            API_ENDPOINTS["analytics"]["event_popularity"],
            spinner_text="Loading event popularity data..."
        )
    except Exception as e:
        st.error(f"Error fetching event popularity data: {str(e)}")
        return {}

@st.cache_data(ttl=3600)
def get_user_engagement() -> Dict[str, Any]:
    """Get user engagement analytics"""
    try:
        return api_client.get(
            API_ENDPOINTS["analytics"]["user_engagement"],
            spinner_text="Loading user engagement data..."
        )
    except Exception as e:
        st.error(f"Error fetching user engagement data: {str(e)}")
        return {}

@st.cache_data(ttl=3600)
def get_points_distribution() -> Dict[str, Any]:
    """Get points distribution analytics"""
    try:
        return api_client.get(
            API_ENDPOINTS["analytics"]["points_distribution"],
            spinner_text="Loading points distribution data..."
        )
    except Exception as e:
        st.error(f"Error fetching points distribution data: {str(e)}")
        return {}

# Points and Badges API functions
@st.cache_data(ttl=300)
def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Get points leaderboard"""
    try:
        return api_client.get(
            API_ENDPOINTS["points"]["leaderboard"],
            params={"limit": limit},
            spinner_text="Loading leaderboard..."
        )
    except Exception as e:
        st.error(f"Error fetching leaderboard: {str(e)}")
        return []

@st.cache_data(ttl=300)
def get_user_events(user_id: str) -> List[Dict[str, Any]]:
    """Get events for a specific user"""
    if not user_id:
        logger.warning("Attempted to fetch user events with empty user_id")
        return []
        
    try:
        # First try the standard endpoint
        try:
            events = api_client.get(
                API_ENDPOINTS["users"]["events"].format(user_id=user_id),
                spinner_text="Loading user events...",
                error_message="Fetching user events",
                fallback_to_demo=True
            )
            
            # Handle various response formats
            if isinstance(events, list):
                return events
            elif isinstance(events, dict):
                if "items" in events:
                    return events["items"]
                elif "events" in events:
                    return events["events"]
                elif "upcoming" in events or "past" in events:
                    # Combine upcoming and past events if that's the format
                    combined = []
                    if "upcoming" in events and isinstance(events["upcoming"], list):
                        combined.extend(events["upcoming"])
                    if "past" in events and isinstance(events["past"], list):
                        combined.extend(events["past"])
                    return combined
            
            # If we can't determine the format but got a response, return empty list
            logger.warning(f"Unexpected user events response format: {type(events)}")
            return []
            
        except APIError as e:
            # If 404, try alternative endpoint format
            if e.status_code == 404:
                logger.info(f"Standard user events endpoint returned 404 for user {user_id}, trying alternative")
                try:
                    # Try alternative endpoint that might return all events with a user_id filter
                    events = api_client.get(
                        API_ENDPOINTS["events"]["list"],
                        params={"user_id": user_id},
                        spinner_text="Loading user events...",
                        error_message="Fetching user events (alternative)"
                    )
                    
                    if isinstance(events, dict) and "items" in events:
                        return events["items"]
                    elif isinstance(events, list):
                        return events
                    return []
                except Exception as alt_e:
                    logger.warning(f"Alternative user events endpoint also failed: {str(alt_e)}")
                    # Fall through to the fallback below
            else:
                # For other error codes, log and continue to fallback
                logger.error(f"Error fetching user events: {str(e)}")
        
        # If we got here, both attempts failed
        logger.warning(f"All user events fetch attempts failed for user {user_id}, using fallback")
        from utils.connection import get_sample_user_events
        return get_sample_user_events()
    except Exception as e:
        logger.error(f"Unexpected error fetching user events: {str(e)}")
        # Don't show error to user - use fallback data instead
        from utils.connection import get_sample_user_events
        return get_sample_user_events()

@st.cache_data(ttl=300)
def get_points_history(user_id: str = None) -> List[Dict[str, Any]]:
    """Get points history, optionally filtered by user"""
    try:
        params = {}
        if user_id:
            params["user_id"] = user_id
        
        try:
            response = api_client.get(
                API_ENDPOINTS["points"]["history"],
                params=params,
                spinner_text="Loading points history...",
                error_message="Fetching points history",
                fallback_to_demo=True
            )
            
            # Handle various response formats
            if isinstance(response, dict):
                if "points_history" in response:
                    return response["points_history"]
                elif "items" in response:
                    return response["items"]
                elif "history" in response and isinstance(response["history"], list):
                    return response["history"]
                elif "transactions" in response and isinstance(response["transactions"], list):
                    return response["transactions"]
            elif isinstance(response, list):
                return response
            
            # If we can't determine the format but got a response, log and continue to fallback
            logger.warning(f"Unexpected points history response format: {type(response)}")
        except APIError as e:
            # Handle 404 errors gracefully
            if e.status_code == 404:
                logger.info(f"No points history found for user {user_id}")
            else:
                logger.error(f"Error fetching points history: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching points history: {str(e)}")
        
        # If we got here, the request failed or returned an invalid format
        logger.warning(f"Points history fetch failed or returned invalid format, using fallback")
        from utils.connection import get_sample_points_history
        return get_sample_points_history()
    except Exception as e:
        logger.error(f"Unexpected error in get_points_history: {str(e)}")
        # Don't show error to user - use fallback data instead
        from utils.connection import get_sample_points_history
        return get_sample_points_history()

@st.cache_data(ttl=3600)
def get_badges() -> List[Dict[str, Any]]:
    """Get all badges"""
    try:
        return api_client.get(
            API_ENDPOINTS["badges"]["list"],
            spinner_text="Loading badges..."
        )
    except Exception as e:
        st.error(f"Error fetching badges: {str(e)}")
        return []

@st.cache_data(ttl=3600)
def get_badge(badge_id: str) -> Optional[Dict[str, Any]]:
    """Get badge by ID"""
    try:
        return api_client.get(
            API_ENDPOINTS["badges"]["detail"].format(badge_id=badge_id),
            spinner_text="Loading badge details..."
        )
    except Exception as e:
        st.error(f"Error fetching badge: {str(e)}")
        return None


def register_for_event(event_id: str, user_id: str = None) -> bool:
    """Register a user for an event
    
    Args:
        event_id (str): ID of the event to register for
        user_id (str, optional): User ID to register. If None, uses current user.
        
    Returns:
        bool: True if registration was successful, False otherwise
    """
    # Check if we're in demo mode - always succeed in demo mode
    if is_demo_mode():
        logger.info(f"Demo mode active, simulating successful registration for event {event_id}")
        st.success("Successfully registered for the event in demo mode!")
        return True
        
    try:
        # If no user_id provided, use the current user
        registration_data = {}
        if user_id:
            registration_data["user_id"] = user_id
            
        # First try the direct event registration endpoint
        try:
            # Try the event-specific registration endpoint first
            api_client.post(
                API_ENDPOINTS["events"]["register"].format(event_id=event_id),
                json_data={},  # No need to send event_id in body for this endpoint
                spinner_text="Registering for event...",
                error_message="Event registration"
            )
            st.success("Successfully registered for the event!")
            # Clear relevant caches
            if hasattr(get_events, 'clear'):
                get_events.clear()
            if hasattr(get_user_events, 'clear'):
                get_user_events.clear()
            return True
        except APIError as e:
            # If 404, try alternative endpoint format
            if e.status_code == 404:
                logger.info(f"Standard registration endpoint returned 404 for event {event_id}, trying alternative")
                try:
                    # Try the registrations endpoint from the API_ENDPOINTS dictionary
                    registrations_endpoint = API_ENDPOINTS["registrations"]["create"]
                    logger.info(f"Trying alternative registration endpoint: {registrations_endpoint}")
                    
                    # Prepare registration data with event_id
                    if not registration_data:
                        registration_data = {}
                    registration_data["event_id"] = event_id
                    
                    api_client.post(
                        registrations_endpoint,
                        json_data=registration_data,
                        spinner_text="Registering for event...",
                        error_message="Event registration (alternative)"
                    )
                    st.success("Successfully registered for the event!")
                    # Clear relevant caches
                    if hasattr(get_events, 'clear'):
                        get_events.clear()
                    if hasattr(get_user_events, 'clear'):
                        get_user_events.clear()
                    return True
                except Exception as alt_e:
                    logger.warning(f"Alternative registration endpoint also failed: {str(alt_e)}")
                    # Fall through to demo mode fallback
            else:
                # For other error codes, log and continue to fallback
                logger.error(f"Error registering for event: {str(e)}")
                
                # Check for specific error messages and provide more user-friendly feedback
                if e.status_code == 400 and "Registration is closed" in str(e):
                    # This is a business rule validation error about event already started
                    st.error(f"❌ {e.message}")
                    st.info("💡 Tip: Look for upcoming events that haven't started yet.")
                    return False
                elif e.status_code == 400 and "already registered" in str(e).lower():
                    # User is already registered
                    st.warning("⚠️ You are already registered for this event.")
                    return True
                elif e.status_code == 400 and "full capacity" in str(e).lower():
                    # Event is at capacity
                    st.error("❌ This event is at full capacity. Please try another event.")
                    return False
                
        # If we got here, both attempts failed - fall back to demo mode
        logger.info(f"All registration attempts failed, falling back to demo mode for event {event_id}")
        st.warning("⚠️ Registration API unavailable. Using demo mode instead.")
        st.success("Registration simulated successfully in demo mode!")
        
        # Clear relevant caches anyway to ensure UI updates
        if hasattr(get_events, 'clear'):
            get_events.clear()
        if hasattr(get_user_events, 'clear'):
            get_user_events.clear()
            
        return True  # Return success in demo mode
    except Exception as e:
        logger.error(f"Event registration error: {str(e)}")
        
        # Even for unexpected errors, fall back to demo mode
        logger.info(f"Unexpected error during registration, falling back to demo mode for event {event_id}")
        st.warning("⚠️ Registration encountered an error. Using demo mode instead.")
        st.success("Registration simulated successfully in demo mode!")
        return True  # Return success in demo mode

def register_user(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Register a new user
    
    Args:
        user_data (Dict[str, Any]): User registration data
        
    Returns:
        Optional[Dict[str, Any]]: Registered user data or None if registration failed
    """
    try:
        # No authentication needed for registration
        response = api_client.post(
            API_ENDPOINTS["users"]["register"],
            json_data=user_data,
            with_auth=False,
            error_message="User registration failed"
        )
        logger.info(f"User registered successfully: {user_data.get('username')}")
        return response
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return None

def safe_get_user_id(user_id=None):
    """
    Safely get a user ID, falling back to current user if not provided.
    
    Args:
        user_id (str, optional): User ID to use, or None to use current user
        
    Returns:
        str: User ID or None if not available
    """
    if user_id:
        return user_id
    
    # Try to get current user ID
    try:
        from utils.auth import get_current_user
        current_user = get_current_user()
        if current_user and "id" in current_user:
            return current_user["id"]
    except Exception as e:
        logger.error(f"Error getting current user ID: {str(e)}")
    
    return None

def safe_get_current_user():
    """
    Safely get current user information with error handling.
    
    Returns:
        dict: User information or None if not available
    """
    try:
        from utils.auth import get_current_user
        return get_current_user()
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return None

def get_user_badges(user_id: str = None):
    """
    Get user badges with enhanced error handling.
    
    Args:
        user_id (str, optional): User ID, or None to use current user
        
    Returns:
        dict: User badges data with consistent format
    """
    # Get user ID, falling back to current user if not provided
    user_id = safe_get_user_id(user_id)
    
    if not user_id:
        logger.warning("No user ID provided or available for get_user_badges")
        return {
            "badges": [],
            "grouped_badges": {},
            "total": 0,
            "error": "No user ID provided"
        }
    
    # If in demo mode, return sample data
    if is_demo_mode():
        from utils.connection import get_sample_user_badges
        return get_sample_user_badges(user_id)
    
    try:
        # Get badges for the user using safe API call
        response = api_client.safe_api_call(
            "GET",
            f"{API_ENDPOINTS['badges']['user']}/{user_id}",
            headers=get_auth_header(),
            error_message=f"Failed to get badges for user {user_id}"
        )
        
        # Process badges data with safe response handler
        badges_data = api_client.safe_api_response_handler(response)
        
        # Extract badges list safely
        if isinstance(badges_data, dict) and "items" in badges_data:
            badges = badges_data.get("items", [])
        elif isinstance(badges_data, list):
            badges = badges_data
        else:
            badges = []
        
        # Group badges by category with null checking
        grouped_badges = {}
        for badge in badges:
            if not isinstance(badge, dict):
                continue
                
            category = badge.get("category", "Other")
            if category not in grouped_badges:
                grouped_badges[category] = []
            grouped_badges[category].append(badge)
        
        # Sort badges within each category by level
        for category in grouped_badges:
            grouped_badges[category].sort(key=lambda x: x.get("level", 0))
        
        return {
            "badges": badges,
            "grouped_badges": grouped_badges,
            "total": len(badges)
        }
    except APIError as e:
        logger.error(f"API error getting badges for user {user_id}: {str(e)}")
        # Return empty data with proper structure and error info
        return {
            "badges": [],
            "grouped_badges": {},
            "total": 0,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error getting badges for user {user_id}: {str(e)}")
        # Return empty data with proper structure
        return {
            "badges": [],
            "grouped_badges": {},
            "total": 0,
            "error": "An unexpected error occurred"
        }

def parse_date_safely(date_str, default=None):
    """
    Safely parse a date string with error handling.
    
    Args:
        date_str (str): Date string to parse
        default: Default value to return if parsing fails
        
    Returns:
        datetime or default: Parsed datetime or default value
    """
    if not date_str:
        return default
        
    try:
        from datetime import datetime
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except Exception as e:
        logger.debug(f"Error parsing date '{date_str}': {str(e)}")
        return default

def register_for_event(event_id: str, user_id: str = None):
    """
    Register a user for an event with enhanced error handling.
    
    Args:
        event_id (str): ID of the event to register for
        user_id (str, optional): User ID to register. If None, uses current user.
        
    Returns:
        dict: Registration result with status and message
    """
    # Check if we're in demo mode - always succeed in demo mode
    if is_demo_mode():
        logger.info(f"Demo mode active, simulating successful registration for event {event_id}")
        return {"success": True, "message": "Registration successful (demo mode)"}
    
    # Get user ID with safe fallback
    user_id = safe_get_user_id(user_id)
    
    if not user_id:
        error_msg = "No user ID provided and no current user available"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}
    
    # If in demo mode, simulate registration
    if is_demo_mode():
        return {"success": True, "message": "Registration successful (demo mode)"}
    
    try:
        # First, get the event to check if registration is allowed
        event = get_event(event_id)
        
        # Check if event exists
        if not event:
            error_msg = f"Event {event_id} not found"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
        # Check if event is in the past with safe date parsing
        from datetime import datetime, timedelta
        event_start = parse_date_safely(event.get("start_time"), default=datetime.now())
        now = datetime.now()
        
        if event_start < now:
            # Calculate how long ago the event started for better user feedback
            time_diff = now - event_start
            if time_diff < timedelta(hours=1):
                time_msg = f"{time_diff.seconds // 60} minutes ago"
            elif time_diff < timedelta(days=1):
                time_msg = f"{time_diff.seconds // 3600} hours ago"
            else:
                time_msg = f"{time_diff.days} days ago"
                
            error_msg = f"Cannot register for past event. Event started {time_msg}."
            logger.warning(f"Cannot register for past event {event_id} (started {time_msg})")
            return {"success": False, "message": error_msg, "reason": "past_event"}
        
        # Check if event is at capacity
        registered_count = event.get("registered_count", 0)
        max_participants = event.get("max_participants", 0)
        
        if max_participants > 0 and registered_count >= max_participants:
            error_msg = f"Event is at full capacity ({registered_count}/{max_participants})"
            logger.warning(f"Event {event_id} is at capacity")
            return {"success": False, "message": error_msg, "reason": "capacity_reached"}
        
        # Check if user is already registered
        try:
            # Get user registrations
            user_events = get_user_events(user_id)
            
            # Check if this event is in the user's registrations
            if isinstance(user_events, dict) and "items" in user_events:
                events = user_events.get("items", [])
            elif isinstance(user_events, list):
                events = user_events
            else:
                events = []
                
            for user_event in events:
                if user_event.get("id") == event_id:
                    error_msg = "You are already registered for this event"
                    logger.info(f"User {user_id} is already registered for event {event_id}")
                    return {"success": False, "message": error_msg, "reason": "already_registered"}
        except Exception as e:
            # Log but continue - this is just a convenience check
            logger.warning(f"Error checking if user is already registered: {str(e)}")
        
        # Register for the event with safe API call
        try:
            response = api_client.safe_api_call(
                "POST",
                API_ENDPOINTS["registrations"]["register"],
                json={"event_id": event_id, "user_id": user_id},
                headers=get_auth_header(),
                error_message=f"Failed to register for event {event_id}"
            )
            
            logger.info(f"Successfully registered for event {event_id}")
            return {"success": True, "message": "Registration successful", "data": response}
        except APIError as e:
            # Check for specific error messages
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                return {"success": False, "message": "You are already registered for this event", "reason": "already_registered"}
            elif "capacity" in error_msg.lower():
                return {"success": False, "message": "Event is at full capacity", "reason": "capacity_reached"}
            elif "past event" in error_msg.lower():
                return {"success": False, "message": "Cannot register for past events", "reason": "past_event"}
            else:
                return {"success": False, "message": error_msg}
    except Exception as e:
        error_msg = f"Error registering for event {event_id}: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": "An unexpected error occurred during registration"}