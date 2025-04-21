from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.api import dependencies
from app.db.session import get_db

router = APIRouter()

# Badge Type CRUD
@router.post("/types/", response_model=schemas.badge_type.BadgeTypeOut)
def create_badge_type(
    badge_type_in: schemas.badge_type.BadgeTypeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser)
):
    db_obj = models.BadgeType(**badge_type_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/types/{badge_type_id}", response_model=schemas.badge_type.BadgeTypeOut)
def update_badge_type(
    badge_type_id: int,
    badge_type_in: schemas.badge_type.BadgeTypeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser)
):
    db_obj = db.query(models.BadgeType).filter(models.BadgeType.id == badge_type_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Badge type not found")
    for field, value in badge_type_in.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/types/{badge_type_id}")
def delete_badge_type(
    badge_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser)
):
    db_obj = db.query(models.BadgeType).filter(models.BadgeType.id == badge_type_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Badge type not found")
    db.delete(db_obj)
    db.commit()
    return {"ok": True}

@router.get("/types/", response_model=List[schemas.badge_type.BadgeTypeOut])
def list_badge_types(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser)
):
    return db.query(models.BadgeType).all()

# Badge Assignment/Revocation
@router.post("/assign", response_model=schemas.badge.BadgeOut)
def assign_badge_to_user(
    badge_in: schemas.badge.BadgeAssign,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser)
):
    badge_type = db.query(models.BadgeType).filter(models.BadgeType.id == badge_in.badge_type_id).first()
    if not badge_type:
        raise HTTPException(status_code=404, detail="Badge type not found")
    badge = models.badge.Badge(
        user_id=badge_in.user_id,
        badge_type_id=badge_in.badge_type_id,
        badge_type=badge_type.badge_type,
        name=badge_type.name,
        description=badge_type.description,
        image_url=badge_type.image_url,
    )
    db.add(badge)
    db.commit()
    db.refresh(badge)
    badge = db.query(models.badge.Badge).filter(models.badge.Badge.id == badge.id).first()
    return badge

@router.post("/revoke", response_model=schemas.badge.BadgeOut)
def revoke_badge_from_user(
    badge_in: schemas.badge.BadgeRevoke,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser)
):
    badge = db.query(models.badge.Badge).filter(
        models.badge.Badge.id == badge_in.badge_id,
        models.badge.Badge.user_id == badge_in.user_id
    ).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found for user")
    db.delete(badge)
    db.commit()
    return badge

from sqlalchemy.orm import joinedload

@router.get("/user_badges/{badge_id}", response_model=schemas.badge.BadgeOut)
def get_user_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser)
):
    """
    Get a user's badge by badge ID (admin/superuser only).
    """
    badge = db.query(models.badge.Badge).options(joinedload(models.badge.Badge.badge_type_obj)).filter(models.badge.Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    badge_dict = badge.__dict__.copy()
    badge_type = badge.badge_type_obj
    if badge_type:
        badge_dict["badge_type_obj"] = schemas.badge_type.BadgeTypeOut.model_validate(badge_type)
    else:
        badge_dict["badge_type_obj"] = None
    return schemas.badge.BadgeOut.model_validate(badge_dict)

@router.delete("/user_badges/{badge_id}", response_model=schemas.badge.BadgeOut)
def delete_user_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser)
):
    """
    Delete a user's badge by badge ID (admin/superuser only).
    """
    badge = db.query(models.badge.Badge).options(joinedload(models.badge.Badge.badge_type_obj)).filter(models.badge.Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    # Convert badge_type_obj to BadgeTypeOut for Pydantic validation
    badge_dict = badge.__dict__.copy()
    badge_type = badge.badge_type_obj
    if badge_type:
        badge_dict["badge_type_obj"] = schemas.badge_type.BadgeTypeOut.model_validate(badge_type)
    else:
        badge_dict["badge_type_obj"] = None
    badge_data = schemas.badge.BadgeOut.model_validate(badge_dict)
    db.delete(badge)
    db.commit()
    return badge_data
