"""
Tests for authentication API endpoints.
"""

import pytest
import logging
from typing import Dict, Any

from admin_dashboard.config import API_ENDPOINTS
from admin_dashboard.utils.api import APIError

# Configure logging
logger = logging.getLogger("test_auth_api")

def test_login_success(api_client, test_user_credentials):
    """Test successful login."""
    # Arrange
    login_data = {
        "username": test_user_credentials["username"],
        "password": test_user_credentials["password"]
    }
    
    # Act
    try:
        response = api_client.post(
            API_ENDPOINTS["auth"]["token"],
            json_data=login_data,
            with_auth=False
        )
        
        # Assert
        assert response is not None
        assert "access_token" in response
        assert "token_type" in response
        assert response["token_type"] == "bearer"
    except APIError as e:
        pytest.fail(f"Login failed with error: {str(e)}")

def test_login_invalid_credentials(api_client):
    """Test login with invalid credentials."""
    # Arrange
    login_data = {
        "username": "invalid_user",
        "password": "invalid_password"
    }
    
    # Act & Assert
    with pytest.raises(APIError) as excinfo:
        api_client.post(
            API_ENDPOINTS["auth"]["token"],
            json_data=login_data,
            with_auth=False
        )
    
    # Check status code
    assert excinfo.value.status_code in [401, 403]

def test_token_refresh(api_client, auth_headers):
    """Test token refresh."""
    # Extract token from headers
    token = auth_headers["Authorization"].split(" ")[1]
    
    # Arrange
    refresh_data = {
        "access_token": token
    }
    
    # Act
    try:
        response = api_client.post(
            API_ENDPOINTS["auth"]["refresh"],
            json_data=refresh_data,
            with_auth=False
        )
        
        # Assert
        assert response is not None
        assert "access_token" in response
        assert "token_type" in response
        assert response["token_type"] == "bearer"
    except APIError as e:
        pytest.fail(f"Token refresh failed with error: {str(e)}")

def test_token_verification(api_client, auth_headers):
    """Test token verification."""
    # Act
    try:
        response = api_client.get(
            API_ENDPOINTS["auth"]["verify"],
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        assert "id" in response
        assert "email" in response
        assert "username" in response
    except APIError as e:
        pytest.fail(f"Token verification failed with error: {str(e)}")

def test_invalid_token_verification(api_client):
    """Test verification with invalid token."""
    # Arrange
    invalid_headers = {
        "Authorization": "Bearer invalid_token"
    }
    
    # Act & Assert
    with pytest.raises(APIError) as excinfo:
        api_client.get(
            API_ENDPOINTS["auth"]["verify"],
            headers=invalid_headers
        )
    
    # Check status code
    assert excinfo.value.status_code in [401, 403]