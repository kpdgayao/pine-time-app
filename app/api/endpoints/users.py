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
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


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