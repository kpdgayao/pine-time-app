from typing import Generator, Callable, Any, TypeVar, Dict, List, Union, Optional
from functools import wraps
import logging
import time

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app import models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        try:
            db.close()
        except Exception as e:
            # Handle SQLAlchemy IllegalStateChangeError during shutdown
            # This prevents the "Method 'close()' can't be called here" errors
            # that occur when the server is shutting down
            pass


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = db.query(models.User).filter(models.User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


# Type variable for generic function return type
T = TypeVar('T')


def safe_api_call(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for safely handling API calls with proper error handling.
    Wraps API endpoint functions to catch and handle exceptions gracefully.
    
    Args:
        func: The API endpoint function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            # Get the request object if available in kwargs
            request = kwargs.get('request', None)
            endpoint = func.__name__
            
            if request:
                client_info = f"{request.client.host}:{request.client.port}" if request.client else "Unknown"
                logging.info(f"API call to {endpoint} from {client_info}")
            
            # Add timing for performance monitoring
            start_time = time.time()
            result = await func(*args, **kwargs) if callable(getattr(func, '__await__', None)) else func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            if elapsed > 1.0:  # Log slow API calls
                logging.warning(f"Slow API call: {endpoint} took {elapsed:.2f}s")
            else:
                logging.debug(f"API call to {endpoint} completed in {elapsed:.2f}s")
                
            return result
            
        except HTTPException as e:
            # Re-raise HTTP exceptions as they're already properly formatted
            logging.warning(f"HTTP error in {func.__name__}: {e.status_code} - {e.detail}")
            raise
            
        except SQLAlchemyError as e:
            # Handle database errors
            logging.error(f"Database error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred. Please try again later."
            )
            
        except ValidationError as e:
            # Handle validation errors
            logging.error(f"Validation error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validation error: {str(e)}"
            )
            
        except Exception as e:
            # Catch all other exceptions
            logging.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later."
            )
            
    return wrapper


def safe_api_response_handler(response: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Safely process API responses, handling different formats consistently.
    
    Args:
        response: The API response to process
        
    Returns:
        Processed response in a consistent format
    """
    try:
        if response is None:
            return {"data": [], "message": "No data found"}
            
        # Handle paginated responses (dictionary with 'items' key)
        if isinstance(response, dict) and "items" in response:
            return response
            
        # Handle list responses
        if isinstance(response, list):
            return {"items": response, "total": len(response)}
            
        # Handle single item responses
        return response
        
    except Exception as e:
        logging.error(f"Error processing API response: {str(e)}", exc_info=True)
        return {"data": [], "error": "Error processing response", "message": str(e)}


def safe_get_current_user(db: Session, request: Request) -> Optional[models.User]:
    """
    Safely get the current user with error handling.
    
    Args:
        db: Database session
        request: FastAPI request object
        
    Returns:
        User object if found and authenticated, None otherwise
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header.replace("Bearer ", "")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            return None
            
        user = db.query(models.User).filter(models.User.id == user_id).first()
        return user if user and user.is_active else None
        
    except (jwt.JWTError, ValidationError, Exception) as e:
        logging.warning(f"Authentication error: {str(e)}")
        return None


def safe_get_user_id(current_user: Optional[models.User]) -> Optional[int]:
    """
    Safely get user ID with null checking.
    
    Args:
        current_user: User object
        
    Returns:
        User ID if available, None otherwise
    """
    try:
        return current_user.id if current_user else None
    except AttributeError as e:
        logging.warning(f"Error getting user ID: {str(e)}")
        return None


def safe_sqlalchemy_to_pydantic(model: Any, schema_class: Any) -> Any:
    """
    Safely convert a SQLAlchemy model instance to a Pydantic schema instance.
    
    Args:
        model: SQLAlchemy model instance
        schema_class: Pydantic schema class to convert to
        
    Returns:
        Pydantic schema instance
    """
    try:
        if model is None:
            logging.warning(f"Attempted to convert None model to {schema_class.__name__}")
            return None
            
        # Extract model attributes as dictionary
        model_dict = {}
        for column in model.__table__.columns:
            model_dict[column.name] = getattr(model, column.name)
            
        # Create and return Pydantic model instance
        return schema_class(**model_dict)
        
    except Exception as e:
        logging.error(f"Error converting SQLAlchemy model to Pydantic schema: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to convert model to {schema_class.__name__}: {str(e)}")