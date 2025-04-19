from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies
from app.core.security import get_password_hash, verify_password

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user_in_data = user_in.dict()
    user_in_data.pop("password")
    user = models.User(**user_in_data)
    user.hashed_password = get_password_hash(user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- NEW USER MANAGEMENT ENDPOINTS ---
from fastapi import status
import logging
from typing import List, Any

@router.patch("/{user_id}/status", response_model=schemas.User)
def update_user_status(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    is_active: bool = Body(..., embed=True),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Activate or deactivate a user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for status update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change status of self.")
    user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} status updated to {is_active} by admin {current_user.id}")
    return user

@router.patch("/{user_id}/role", response_model=schemas.User)
def update_user_role(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    user_type: str = Body(...),
    is_superuser: bool = Body(...),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Change user type or superuser status.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for role update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change role of self.")
    if user_type not in ["regular", "business", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid user_type.")
    user.user_type = user_type
    user.is_superuser = is_superuser
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} role updated to {user_type}, superuser={is_superuser} by admin {current_user.id}")
    return user

@router.post("/bulk_update", response_model=List[schemas.User])
def bulk_update_users(
    *,
    db: Session = Depends(dependencies.get_db),
    user_ids: List[int] = Body(...),
    action: str = Body(...),
    value: Any = Body(None),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Bulk update users (activate, deactivate, delete, promote, demote).
    """
    allowed_actions = ["activate", "deactivate", "delete", "promote", "demote"]
    if action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Invalid bulk action.")
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found for bulk update.")
    updated_users = []
    for user in users:
        if user.id == current_user.id:
            continue  # skip self
        if action == "activate":
            user.is_active = True
        elif action == "deactivate":
            user.is_active = False
        elif action == "delete":
            db.delete(user)
            continue
        elif action == "promote":
            user.user_type = "admin"
            user.is_superuser = True
        elif action == "demote":
            user.user_type = "regular"
            user.is_superuser = False
        db.add(user)
        updated_users.append(user)
    db.commit()
    for user in updated_users:
        db.refresh(user)
    logging.info(f"Bulk action '{action}' performed on users {user_ids} by admin {current_user.id}")
    return updated_users


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(dependencies.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = current_user
    if password is not None:
        user.hashed_password = get_password_hash(password)
    if full_name is not None:
        user.full_name = full_name
    if email is not None:
        user.email = email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- NEW USER MANAGEMENT ENDPOINTS ---
from fastapi import status
import logging
from typing import List, Any

@router.patch("/{user_id}/status", response_model=schemas.User)
def update_user_status(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    is_active: bool = Body(..., embed=True),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Activate or deactivate a user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for status update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change status of self.")
    user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} status updated to {is_active} by admin {current_user.id}")
    return user

@router.patch("/{user_id}/role", response_model=schemas.User)
def update_user_role(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    user_type: str = Body(...),
    is_superuser: bool = Body(...),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Change user type or superuser status.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for role update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change role of self.")
    if user_type not in ["regular", "business", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid user_type.")
    user.user_type = user_type
    user.is_superuser = is_superuser
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} role updated to {user_type}, superuser={is_superuser} by admin {current_user.id}")
    return user

@router.post("/bulk_update", response_model=List[schemas.User])
def bulk_update_users(
    *,
    db: Session = Depends(dependencies.get_db),
    user_ids: List[int] = Body(...),
    action: str = Body(...),
    value: Any = Body(None),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Bulk update users (activate, deactivate, delete, promote, demote).
    """
    allowed_actions = ["activate", "deactivate", "delete", "promote", "demote"]
    if action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Invalid bulk action.")
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found for bulk update.")
    updated_users = []
    for user in users:
        if user.id == current_user.id:
            continue  # skip self
        if action == "activate":
            user.is_active = True
        elif action == "deactivate":
            user.is_active = False
        elif action == "delete":
            db.delete(user)
            continue
        elif action == "promote":
            user.user_type = "admin"
            user.is_superuser = True
        elif action == "demote":
            user.user_type = "regular"
            user.is_superuser = False
        db.add(user)
        updated_users.append(user)
    db.commit()
    for user in updated_users:
        db.refresh(user)
    logging.info(f"Bulk action '{action}' performed on users {user_ids} by admin {current_user.id}")
    return updated_users


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user == current_user:
        return user

# --- NEW USER MANAGEMENT ENDPOINTS ---
from fastapi import status
import logging
from typing import List, Any

@router.patch("/{user_id}/status", response_model=schemas.User)
def update_user_status(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    is_active: bool = Body(..., embed=True),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Activate or deactivate a user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for status update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change status of self.")
    user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} status updated to {is_active} by admin {current_user.id}")
    return user

@router.patch("/{user_id}/role", response_model=schemas.User)
def update_user_role(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    user_type: str = Body(...),
    is_superuser: bool = Body(...),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Change user type or superuser status.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for role update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change role of self.")
    if user_type not in ["regular", "business", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid user_type.")
    user.user_type = user_type
    user.is_superuser = is_superuser
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} role updated to {user_type}, superuser={is_superuser} by admin {current_user.id}")
    return user

@router.post("/bulk_update", response_model=List[schemas.User])
def bulk_update_users(
    *,
    db: Session = Depends(dependencies.get_db),
    user_ids: List[int] = Body(...),
    action: str = Body(...),
    value: Any = Body(None),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Bulk update users (activate, deactivate, delete, promote, demote).
    """
    allowed_actions = ["activate", "deactivate", "delete", "promote", "demote"]
    if action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Invalid bulk action.")
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found for bulk update.")
    updated_users = []
    for user in users:
        if user.id == current_user.id:
            continue  # skip self
        if action == "activate":
            user.is_active = True
        elif action == "deactivate":
            user.is_active = False
        elif action == "delete":
            db.delete(user)
            continue
        elif action == "promote":
            user.user_type = "admin"
            user.is_superuser = True
        elif action == "demote":
            user.user_type = "regular"
            user.is_superuser = False
        db.add(user)
        updated_users.append(user)
    db.commit()
    for user in updated_users:
        db.refresh(user)
    logging.info(f"Bulk action '{action}' performed on users {user_ids} by admin {current_user.id}")
    return updated_users
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user

# --- NEW USER MANAGEMENT ENDPOINTS ---
from fastapi import status
import logging
from typing import List, Any

@router.patch("/{user_id}/status", response_model=schemas.User)
def update_user_status(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    is_active: bool = Body(..., embed=True),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Activate or deactivate a user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for status update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change status of self.")
    user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} status updated to {is_active} by admin {current_user.id}")
    return user

@router.patch("/{user_id}/role", response_model=schemas.User)
def update_user_role(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    user_type: str = Body(...),
    is_superuser: bool = Body(...),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Change user type or superuser status.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for role update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change role of self.")
    if user_type not in ["regular", "business", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid user_type.")
    user.user_type = user_type
    user.is_superuser = is_superuser
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} role updated to {user_type}, superuser={is_superuser} by admin {current_user.id}")
    return user

@router.post("/bulk_update", response_model=List[schemas.User])
def bulk_update_users(
    *,
    db: Session = Depends(dependencies.get_db),
    user_ids: List[int] = Body(...),
    action: str = Body(...),
    value: Any = Body(None),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Bulk update users (activate, deactivate, delete, promote, demote).
    """
    allowed_actions = ["activate", "deactivate", "delete", "promote", "demote"]
    if action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Invalid bulk action.")
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found for bulk update.")
    updated_users = []
    for user in users:
        if user.id == current_user.id:
            continue  # skip self
        if action == "activate":
            user.is_active = True
        elif action == "deactivate":
            user.is_active = False
        elif action == "delete":
            db.delete(user)
            continue
        elif action == "promote":
            user.user_type = "admin"
            user.is_superuser = True
        elif action == "demote":
            user.user_type = "regular"
            user.is_superuser = False
        db.add(user)
        updated_users.append(user)
    db.commit()
    for user in updated_users:
        db.refresh(user)
    logging.info(f"Bulk action '{action}' performed on users {user_ids} by admin {current_user.id}")
    return updated_users


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user_data = jsonable_encoder(user)
    update_data = user_in.dict(exclude_unset=True)
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- NEW USER MANAGEMENT ENDPOINTS ---
from fastapi import status
import logging
from typing import List, Any

@router.patch("/{user_id}/status", response_model=schemas.User)
def update_user_status(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    is_active: bool = Body(..., embed=True),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Activate or deactivate a user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for status update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change status of self.")
    user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} status updated to {is_active} by admin {current_user.id}")
    return user

@router.patch("/{user_id}/role", response_model=schemas.User)
def update_user_role(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    user_type: str = Body(...),
    is_superuser: bool = Body(...),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Change user type or superuser status.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"User with id {user_id} not found for role update.")
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change role of self.")
    if user_type not in ["regular", "business", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid user_type.")
    user.user_type = user_type
    user.is_superuser = is_superuser
    db.add(user)
    db.commit()
    db.refresh(user)
    logging.info(f"User {user_id} role updated to {user_type}, superuser={is_superuser} by admin {current_user.id}")
    return user

@router.post("/bulk_update", response_model=List[schemas.User])
def bulk_update_users(
    *,
    db: Session = Depends(dependencies.get_db),
    user_ids: List[int] = Body(...),
    action: str = Body(...),
    value: Any = Body(None),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Bulk update users (activate, deactivate, delete, promote, demote).
    """
    allowed_actions = ["activate", "deactivate", "delete", "promote", "demote"]
    if action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Invalid bulk action.")
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found for bulk update.")
    updated_users = []
    for user in users:
        if user.id == current_user.id:
            continue  # skip self
        if action == "activate":
            user.is_active = True
        elif action == "deactivate":
            user.is_active = False
        elif action == "delete":
            db.delete(user)
            continue
        elif action == "promote":
            user.user_type = "admin"
            user.is_superuser = True
        elif action == "demote":
            user.user_type = "regular"
            user.is_superuser = False
        db.add(user)
        updated_users.append(user)
    db.commit()
    for user in updated_users:
        db.refresh(user)
    logging.info(f"Bulk action '{action}' performed on users {user_ids} by admin {current_user.id}")
    return updated_users


@router.post("/register", response_model=schemas.User)
def register_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Register new user without requiring superuser privileges.
    """
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user_in_data = user_in.dict()
    user_in_data.pop("password")
    # Set default role to regular user
    user_in_data["is_superuser"] = False
    user_in_data["is_active"] = True
    user = models.User(**user_in_data)
    user.hashed_password = get_password_hash(user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user