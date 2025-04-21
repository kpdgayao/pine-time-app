from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app import models, schemas
from app.api import dependencies

router = APIRouter()

@router.get("/points/transactions", response_model=List[schemas.PointsTransactionAdmin])
def get_all_points_transactions(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
    user_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all points transactions for admin, with optional filters.
    Includes user, event, and admin info for each transaction.
    """
    query = db.query(models.PointsTransaction)
    if user_id:
        query = query.filter(models.PointsTransaction.user_id == user_id)
    if type:
        query = query.filter(models.PointsTransaction.type == type)
    query = query.options(
        joinedload(models.PointsTransaction.user),
        joinedload(models.PointsTransaction.event),
        joinedload(models.PointsTransaction.admin)
    )
    transactions = query.order_by(models.PointsTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions
