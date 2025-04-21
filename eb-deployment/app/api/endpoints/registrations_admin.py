from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import dependencies

router = APIRouter()

def get_current_active_admin(current_user: models.User = Depends(dependencies.get_current_user)) -> models.User:
    if not (current_user.is_superuser or getattr(current_user, "user_type", None) == "admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.post("/{registration_id}/approve", response_model=schemas.Registration)
def approve_registration(
    *,
    db: Session = Depends(dependencies.get_db),
    registration_id: int,
    current_user: models.User = Depends(get_current_active_admin),
):
    reg = db.query(models.Registration).filter(models.Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    reg.status = "approved"
    db.commit()
    db.refresh(reg)
    return reg

@router.post("/{registration_id}/reject", response_model=schemas.Registration)
def reject_registration(
    *,
    db: Session = Depends(dependencies.get_db),
    registration_id: int,
    current_user: models.User = Depends(get_current_active_admin),
):
    reg = db.query(models.Registration).filter(models.Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    reg.status = "rejected"
    db.commit()
    db.refresh(reg)
    return reg

@router.get("/pending", response_model=List[schemas.Registration])
def get_pending_registrations(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(get_current_active_admin),
):
    regs = db.query(models.Registration).filter(models.Registration.status == "pending").all()
    # Attach user and event info for each registration
    for reg in regs:
        reg.user = db.query(models.User).filter(models.User.id == reg.user_id).first()
        reg.event = db.query(models.Event).filter(models.Event.id == reg.event_id).first()
    return regs
