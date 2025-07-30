from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.data.db import get_session
from app.models import Token
import app.service.user
import app.service.auth

router = APIRouter(prefix="/auth")

@router.post("/", response_model=Token)
async def login_for_access_token(
    form_data: app.service.auth.oauth2_form_dep,
    session: Session = Depends(get_session)
) -> Token:
    user = await app.service.user.get_user_from_login(form_data, session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Verify password
    if not app.service.auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    return Token(access_token=app.service.auth.create_access_token(user), token_type="bearer")