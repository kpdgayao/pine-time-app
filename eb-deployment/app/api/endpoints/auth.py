from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import secrets
import string
import time
import logging

from app import models
from app.api import dependencies
from app.core.security import get_password_hash
from app.utils.email_utils import send_reset_email

router = APIRouter()

# In-memory store for reset tokens (for demo/testing; use DB or cache in production)
RESET_TOKENS = {}
RESET_TOKEN_EXPIRY_SECONDS = 3600  # 1 hour

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
def forgot_password(
    *,
    db: Session = Depends(dependencies.get_db),
    request: ForgotPasswordRequest,
) -> Any:
    """
    Initiate password reset process. Generates a reset token and sends it via email if possible.
    For demo/testing, the token is returned in the response if email fails.
    """
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist.")
    # Generate a secure random token
    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    RESET_TOKENS[token] = {
        "user_id": user.id,
        "expires": time.time() + RESET_TOKEN_EXPIRY_SECONDS
    }
    # Try to send the token via email
    email_sent = send_reset_email(user.email, token)
    if email_sent:
        logging.info(f"Password reset token sent to {user.email}")
        return {"message": "Password reset instructions have been sent to your email."}
    else:
        logging.warning(f"Email not sent to {user.email}, returning token in response for demo/testing.")
        return {"reset_token": token, "message": "Password reset token generated (email not sent, demo mode)."}

@router.post("/reset-password")
def reset_password(
    *,
    db: Session = Depends(dependencies.get_db),
    request: ResetPasswordRequest,
) -> Any:
    """
    Reset user password using a valid reset token.
    """
    token_data = RESET_TOKENS.get(request.token)
    if not token_data or token_data["expires"] < time.time():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    user = db.query(models.User).filter(models.User.id == token_data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.hashed_password = get_password_hash(request.new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    # Invalidate token after use
    del RESET_TOKENS[request.token]
    return {"message": "Password has been reset successfully."}
