"""
Payment registration endpoint for Pine Time App (PostgreSQL, no ORM).
Follows PEP 8, robust error handling, and project conventions.
"""

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, condecimal
from typing import Optional
import logging
import psycopg2
from app.utils import db

router = APIRouter()

class PaymentRegistrationRequest(BaseModel):
    registration_id: int
    user_id: int
    event_id: int
    amount_paid: condecimal(max_digits=10, decimal_places=2)
    payment_channel: str

@router.post("/payments/register", status_code=201)
def register_payment(payment: PaymentRegistrationRequest, request: Request):
    """
    Registers a payment for an event registration.
    """
    if db.is_demo_mode():
        # Demo mode fallback: pretend success
        return {"payment_id": 1, "payment_date": "demo-mode"}

    conn = None
    try:
        params = db.get_postgres_connection_params()
        conn = psycopg2.connect(**params)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO payment (
                    registration_id, user_id, event_id, amount_paid, payment_channel
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id, payment_date
            """, (
                payment.registration_id,
                payment.user_id,
                payment.event_id,
                payment.amount_paid,
                payment.payment_channel
            ))
            row = cur.fetchone()
            conn.commit()
        return {"payment_id": row[0], "payment_date": row[1]}
    except psycopg2.IntegrityError as e:
        logging.error(f"Payment registration integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid registration, user, or event ID, or duplicate payment."
        )
    except Exception as e:
        logging.error(f"Payment registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register payment. Please try again later."
        )
    finally:
        if conn:
            conn.close()


@router.get("/payments/by_registration/{registration_id}")
def get_payment_by_registration(registration_id: int):
    """
    Retrieve payment details for a given registration ID.
    """
    if db.is_demo_mode():
        # Demo mode fallback: pretend no payment
        return None

    conn = None
    try:
        params = db.get_postgres_connection_params()
        conn = psycopg2.connect(**params)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, registration_id, user_id, event_id, amount_paid, payment_channel, payment_date
                FROM payment
                WHERE registration_id = %s
            """, (registration_id,))
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Payment not found for this registration.")
        return {
            "payment_id": row[0],
            "registration_id": row[1],
            "user_id": row[2],
            "event_id": row[3],
            "amount_paid": float(row[4]),
            "payment_channel": row[5],
            "payment_date": row[6]
        }
    except HTTPException:
        # Re-raise FastAPI HTTPExceptions so they propagate correctly (e.g., 404 for not found)
        raise
    except Exception as e:
        # Log the full traceback for robust debugging
        logging.exception(f"Failed to fetch payment for registration {registration_id}")
        # Only unexpected errors should return 500
        raise HTTPException(status_code=500, detail="Failed to fetch payment details.")
    finally:
        if conn:
            conn.close()
