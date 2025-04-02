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
            response = requests.post(
                API_ENDPOINTS["auth"]["token"],
                data={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                st.session_state["token"] = token_data["access_token"]
                st.session_state["refresh_token"] = token_data.get("refresh_token")
                st.session_state["token_expiry"] = time.time() + token_data.get("expires_in", 3600)
                st.session_state["is_authenticated"] = True
                st.session_state["login_time"] = time.time()
                
                # Get user info from token
                user_info = verify_token(token_data["access_token"])
                if user_info:
                    st.session_state["user_info"] = user_info
                    logger.info(f"User {user_info.get('username')} logged in successfully")
                    return True
                else:
                    logout()
                    st.error("Failed to get user information")
                    return False
            elif response.status_code == 401:
                st.error("Invalid username or password")
                return False
            else:
                try:
                    error_detail = response.json().get("detail", f"Error code: {response.status_code}")
                    st.error(f"Login failed: {error_detail}")
                except json.JSONDecodeError:
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

def refresh_token():
    """
    Refresh JWT token using refresh token.
    
    Returns:
        bool: True if token refresh successful, False otherwise
    """
    # In demo mode, just reset the expiry
    if is_demo_mode():
        st.session_state["token_expiry"] = time.time() + 3600
        return True
    
    refresh_token = st.session_state.get("refresh_token")
    if not refresh_token:
        logger.warning("No refresh token available")
        return False
    
    try:
        logger.info("Attempting to refresh token")
        response = requests.post(
            API_ENDPOINTS["auth"]["refresh"],
            json={"refresh_token": refresh_token}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state["token"] = token_data["access_token"]
            st.session_state["token_expiry"] = time.time() + token_data.get("expires_in", 3600)
            # Update refresh token if provided
            if "refresh_token" in token_data:
                st.session_state["refresh_token"] = token_data["refresh_token"]
            logger.info("Token refreshed successfully")
            return True
        
        logger.warning(f"Token refresh failed: {response.status_code}")
        return False
    except Exception as e:
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
        response = requests.get(
            API_ENDPOINTS["auth"]["verify"],
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        
        logger.warning(f"Token verification failed: {response.status_code}")
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
    if not st.session_state.get("is_authenticated"):
        logger.warning("User not authenticated")
        return False
    
    if is_token_expired():
        logger.info("Token expired or about to expire, attempting refresh")
        if not refresh_token():
            logger.warning("Token refresh failed, logging out")
            logout()
            return False
    
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