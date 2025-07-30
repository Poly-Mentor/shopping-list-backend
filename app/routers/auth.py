from fastapi import APIRouter, HTTPException, status

from app.models import Token
from app.service.auth import oauth2_form_dep, create_access_token
from app.service.user import get_user_from_login_dep

router = APIRouter(prefix="/auth")

@router.post("/")
async def login_for_access_token(
    form_data: oauth2_form_dep,
    user: get_user_from_login_dep
) -> Token:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user), token_type="bearer")