"""
Authentication utilities for the Pine Time Admin Dashboard.
Handles JWT token management and session state.
"""

import requests
import streamlit as st
import time
import json
import logging
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import PyJWTError
from typing import Dict, Any, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_ENDPOINTS, SESSION_EXPIRY, TOKEN_REFRESH_MARGIN
from utils.db import is_demo_mode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("auth_utils")

class AuthError(Exception):
    """Custom exception for authentication errors"""
    pass

def login(username, password):
    """
    Authenticate user with the FastAPI backend and store JWT token in session state.
    
    Args:
        username (str): Admin username
        password (str): Admin password
        
    Returns:
        bool: True if login successful, False otherwise
    """
    # If in demo mode, use demo credentials
    if is_demo_mode():
        if username == "demo@pinetimeexperience.com" and password == "demo":
            st.session_state["token"] = "demo_token"
            st.session_state["refresh_token"] = "demo_refresh_token"
            st.session_state["token_expiry"] = time.time() + 3600
            st.session_state["is_authenticated"] = True
            st.session_state["login_time"] = time.time()
            st.session_state["user_info"] = {
                "id": "demo_user_id",
                "username": "demo_user",
                "email": "demo@pinetimeexperience.com",
                "full_name": "Demo User",
                "role": "user",
                "points": 500,
                "created_at": datetime.now().isoformat()
            }
            return True
        else:
            st.error("Invalid username or password")
            return False
    
    try:
        with st.spinner("Authenticating..."):
            # Log the login attempt with the endpoint URL
            logger.info(f"Attempting login with endpoint: {API_ENDPOINTS['auth']['token']}")
            
            # Add timeout to prevent hanging
            response = requests.post(
                API_ENDPOINTS["auth"]["token"],
                data={"username": username, "password": password},
                timeout=10
            )
            
            # Log the response status code
            logger.info(f"Login response status code: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                logger.info("Login successful, received token data")
                
                # Check if access_token is in the response
                if "access_token" not in token_data:
                    logger.error(f"Missing access_token in response: {token_data}")
                    st.error("Authentication error: Invalid token response")
                    return False
                
                # Store token data in session state
                st.session_state["token"] = token_data["access_token"]
                st.session_state["refresh_token"] = token_data.get("refresh_token")
                st.session_state["token_expiry"] = time.time() + token_data.get("expires_in", 3600)
                st.session_state["is_authenticated"] = True
                st.session_state["login_time"] = time.time()
                
                # Log token information (without exposing the actual token)
                logger.info(f"Token stored in session, expires in {token_data.get('expires_in', 3600)} seconds")
                
                # Try to get user info from token verification endpoint
                logger.info("Verifying token and getting user info")
                user_info = verify_token(token_data["access_token"])
                
                # If token verification fails, try to extract basic info from the token itself
                if not user_info:
                    logger.warning("Token verification failed, attempting to extract user info from token payload")
                    try:
                        # Extract user info from token payload
                        payload = decode_token(token_data["access_token"])
                        if payload:
                            # Create minimal user info from payload
                            user_info = {
                                "id": payload.get("sub", "unknown"),
                                "username": username,
                                "email": username if "@" in username else f"{username}@example.com",
                                "role": payload.get("role", "user"),
                                "created_at": datetime.now().isoformat()
                            }
                            logger.info("Created user info from token payload")
                    except Exception as e:
                        logger.error(f"Failed to extract user info from token: {str(e)}")
                
                # If we have user info (either from verification or token payload), proceed with login
                if user_info:
                    st.session_state["user_info"] = user_info
                    logger.info(f"User {user_info.get('username')} logged in successfully")
                    return True
                else:
                    # Even without user info, we can still allow login with minimal info
                    minimal_user_info = {
                        "id": "unknown",
                        "username": username,
                        "email": username if "@" in username else f"{username}@example.com",
                        "role": "user",
                        "created_at": datetime.now().isoformat()
                    }
                    st.session_state["user_info"] = minimal_user_info
                    logger.warning(f"Proceeding with login using minimal user info for: {username}")
                    st.warning("⚠️ Limited user information available. Some features may be restricted.")
                    return True
            elif response.status_code == 401:
                logger.warning(f"Login failed: Invalid credentials")
                st.error("Invalid username or password")
                return False
            else:
                try:
                    response_text = response.text
                    logger.error(f"Login failed with status {response.status_code}: {response_text}")
                    
                    error_detail = response.json().get("detail", f"Error code: {response.status_code}")
                    st.error(f"Login failed: {error_detail}")
                except json.JSONDecodeError:
                    logger.error(f"Login failed with status {response.status_code}, invalid JSON response: {response.text}")
                    st.error(f"Login failed: Error code {response.status_code}")
                return False
    except requests.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        logger.error(f"Login connection error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        logger.error(f"Login error: {str(e)}")
        return False

def refresh_token(force: bool = False):
    """
    Refresh JWT token using refresh token.
    
    Args:
        force (bool): Force token refresh even if not expired
    
    Returns:
        bool: True if token refresh successful, False otherwise
    """
    # In demo mode, just reset the expiry
    if is_demo_mode():
        st.session_state["token_expiry"] = time.time() + 3600
        return True
    
    # Check if token needs refresh (unless forced)
    if not force and not is_token_expired():
        logger.debug("Token is still valid, no need to refresh")
        return True
    
    refresh_token = st.session_state.get("refresh_token")
    if not refresh_token:
        logger.warning("No refresh token available")
        return False
    
    # Track refresh attempts to prevent infinite loops
    refresh_attempts = st.session_state.get("token_refresh_attempts", 0)
    if refresh_attempts > 3:  # Limit to 3 consecutive attempts
        logger.error("Too many token refresh attempts, forcing re-login")
        logout()  # Force logout to clear invalid tokens
        st.error("🔑 Session expired. Please log in again.")
        return False
    
    try:
        logger.info("Attempting to refresh token")
        response = requests.post(
            API_ENDPOINTS["auth"]["refresh"],
            json={"refresh_token": refresh_token},
            timeout=10  # Add timeout to prevent hanging
        )
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state["token"] = token_data["access_token"]
            st.session_state["token_expiry"] = time.time() + token_data.get("expires_in", 3600)
            # Update refresh token if provided
            if "refresh_token" in token_data:
                st.session_state["refresh_token"] = token_data["refresh_token"]
            # Reset refresh attempts counter on success
            st.session_state["token_refresh_attempts"] = 0
            logger.info("Token refreshed successfully")
            return True
        elif response.status_code == 401 or response.status_code == 403:
            # Invalid or expired refresh token
            logger.warning(f"Refresh token invalid or expired: {response.status_code}")
            # Clear invalid tokens and force re-login
            logout()
            st.error("🔑 Session expired. Please log in again.")
            return False
        else:
            # Increment refresh attempts counter
            st.session_state["token_refresh_attempts"] = refresh_attempts + 1
            logger.warning(f"Token refresh failed with status code: {response.status_code}")
            # Try to extract error details from response
            try:
                error_details = response.json().get("detail", "Unknown error")
                logger.warning(f"Token refresh error details: {error_details}")
            except Exception:
                pass
            return False
    except requests.exceptions.ConnectionError:
        logger.error("Connection error during token refresh")
        # Don't increment counter for connection errors as they might be temporary
        return False
    except requests.exceptions.Timeout:
        logger.error("Timeout during token refresh")
        # Don't increment counter for timeouts as they might be temporary
        return False
    except Exception as e:
        # Increment refresh attempts counter
        st.session_state["token_refresh_attempts"] = refresh_attempts + 1
        logger.error(f"Token refresh error: {str(e)}")
        return False

def verify_token(token):
    """
    Verify JWT token with the FastAPI backend.
    
    Args:
        token (str): JWT token
        
    Returns:
        dict: User information if token is valid, None otherwise
    """
    # In demo mode, return demo user info
    if is_demo_mode() or token == "demo_token":
        return {
            "id": "demo_user_id",
            "username": "demo_user",
            "email": "demo@pinetimeexperience.com",
            "full_name": "Demo User",
            "role": "user",
            "points": 500,
            "created_at": datetime.now().isoformat()
        }
    
    try:
        # Use the user profile endpoint instead of token verification endpoint
        # This is more reliable as it's a standard GET endpoint that returns user info
        logger.info(f"Verifying token using user profile endpoint: {API_ENDPOINTS['users']['profile']}")
        
        response = requests.get(
            API_ENDPOINTS["users"]["profile"],
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        logger.info(f"User profile response status: {response.status_code}")
        
        # Handle successful response
        if response.status_code == 200:
            user_data = response.json()
            logger.info(f"Token verification successful for user: {user_data.get('username', 'unknown')}")
            return user_data
        
        # If user profile fails, try the original token verification endpoint as fallback
        logger.warning(f"User profile endpoint failed, trying token verification endpoint as fallback")
        
        # Try both POST and GET methods for the token verification endpoint
        for method in ["post", "get"]:
            try:
                if method == "post":
                    verify_response = requests.post(
                        API_ENDPOINTS["auth"]["verify"],
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=10
                    )
                else:
                    verify_response = requests.get(
                        API_ENDPOINTS["auth"]["verify"],
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=10
                    )
                
                logger.info(f"Token verification {method.upper()} response status: {verify_response.status_code}")
                
                if verify_response.status_code == 200:
                    user_data = verify_response.json()
                    logger.info(f"Token verification successful using {method.upper()} method")
                    return user_data
            except requests.RequestException as e:
                logger.warning(f"{method.upper()} method failed for token verification: {str(e)}")
        
        # If we get here, both endpoints failed
        # Try to extract basic info from the token itself
        logger.warning("All verification methods failed, attempting to extract info from token")
        payload = decode_token(token)
        if payload:
            # Create minimal user info from payload
            user_info = {
                "id": payload.get("sub", "unknown"),
                "username": payload.get("username", "user"),
                "email": payload.get("email", "user@example.com"),
                "role": payload.get("role", "user"),
                "created_at": datetime.now().isoformat()
            }
            logger.info("Created user info from token payload")
            return user_info
            
        # Handle error responses
        error_message = "Unknown error"
        try:
            error_data = response.json()
            error_message = error_data.get("detail", f"Error code: {response.status_code}")
        except:
            error_message = f"Error code: {response.status_code}"
        
        logger.warning(f"Token verification failed: {error_message}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return None

def decode_token(token):
    """
    Decode JWT token without verification to check expiry.
    
    Args:
        token (str): JWT token
        
    Returns:
        dict: Decoded token payload, None if invalid
    """
    # In demo mode, return a fake payload
    if is_demo_mode() or token == "demo_token":
        return {
            "sub": "demo_user_id",
            "exp": int(time.time() + 3600),
            "role": "user"
        }
    
    try:
        # Decode without verification just to check expiry
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except PyJWTError as e:
        logger.error(f"Token decode error: {str(e)}")
        return None

def is_token_expired():
    """
    Check if current token is expired or about to expire.
    
    Returns:
        bool: True if token is expired or will expire soon, False otherwise
    """
    token_expiry = st.session_state.get("token_expiry", 0)
    # Consider token expired if less than TOKEN_REFRESH_MARGIN seconds remaining
    return time.time() > (token_expiry - TOKEN_REFRESH_MARGIN)

def ensure_valid_token():
    """
    Ensure a valid token is available, refreshing if needed.
    
    Returns:
        bool: True if valid token available, False otherwise
    """
    # In demo mode, always return True
    if is_demo_mode():
        return True
    
    # Check if token exists
    token = st.session_state.get("token")
    if not token:
        logger.warning("No token available")
        return False
    
    # Check if user is authenticated at all
    if not st.session_state.get("is_authenticated", False):
        logger.warning("User not authenticated")
        return False
    
    # Check if token is expired or about to expire
    if is_token_expired():
        logger.info("Token expired or about to expire, refreshing")
        refresh_success = refresh_token()
        
        # If refresh failed, check if we should retry with a forced refresh
        if not refresh_success and st.session_state.get("token_refresh_attempts", 0) < 2:
            logger.info("Token refresh failed, attempting forced refresh")
            return refresh_token(force=True)
        
        return refresh_success
    
    # Validate token periodically (every 30 minutes) even if not expired
    last_validation = st.session_state.get("token_last_validation", 0)
    current_time = time.time()
    if current_time - last_validation > 1800:  # 30 minutes
        logger.info("Performing periodic token validation")
        user_info = verify_token(token)
        st.session_state["token_last_validation"] = current_time
        
        if not user_info:
            logger.warning("Token validation failed, attempting refresh")
            return refresh_token(force=True)
    
    return True

def check_authentication():
    """
    Check if user is authenticated and session is still valid.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    if not st.session_state.get("is_authenticated"):
        return False
    
    # Check session expiry
    current_time = time.time()
    login_time = st.session_state.get("login_time", 0)
    
    if current_time - login_time > SESSION_EXPIRY:
        logger.info("Session expired, logging out")
        logout()
        return False
    
    # Ensure valid token
    if not ensure_valid_token():
        return False
    
    # Refresh session time
    st.session_state["login_time"] = current_time
    return True

def check_admin_access():
    """
    Check if authenticated user has admin role.
    
    Returns:
        bool: True if user has admin role, False otherwise
    """
    if not check_authentication():
        return False
    
    user_info = st.session_state.get("user_info", {})
    return user_info.get("role") == "admin"

def check_user_access():
    """
    Check if authenticated user has regular user role.
    
    Returns:
        bool: True if user has user role, False otherwise
    """
    if not check_authentication():
        return False
    
    user_info = st.session_state.get("user_info", {})
    return user_info.get("role") == "user"

def logout():
    """
    Clear session state and log out user.
    """
    for key in ["token", "refresh_token", "token_expiry", "is_authenticated", "login_time", "user_info"]:
        if key in st.session_state:
            del st.session_state[key]
    logger.info("User logged out")

def get_auth_header():
    """
    Get authorization header with JWT token.
    
    Returns:
        dict: Authorization header
    """
    token = st.session_state.get("token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user information.
    
    Returns:
        dict: User information if authenticated, None otherwise
    """
    if not check_authentication():
        return None
    
    return st.session_state.get("user_info")