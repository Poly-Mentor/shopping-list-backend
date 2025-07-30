import jwt
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from app.models import User, UserCreate

# Load environment variables
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

def get_secret_key():
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("SECRET_KEY environment variable not set")
    return secret_key

def get_algorithm():
    algorithm = os.getenv('ALGORITHM')
    if not algorithm:
        raise ValueError("ALGORITHM environment variable not set")
    return algorithm

def get_token_expires_minutes():
    token_expiration = os.getenv("TOKEN_EXPIRES_MINUTES")
    if not token_expiration:
        return 15
    return int(token_expiration)

SECRET_KEY = get_secret_key()
ALGORITHM = get_algorithm()
TOKEN_EXPIRES_MINUTES = get_token_expires_minutes()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

oauth2_scheme_dep = Annotated[str, Depends(oauth2_scheme)]
oauth2_form_dep = Annotated[OAuth2PasswordRequestForm, Depends()]

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_string_password(password: str) -> str:
    return pwd_context.hash(password)

def get_password_hash(user: UserCreate):
    return hash_string_password(user.password)

hash_password_dep = Annotated[str, Depends(get_password_hash)]

def create_access_token(user: User):
    data: dict = {"sub": user.name}
    expires_delta = timedelta(minutes=TOKEN_EXPIRES_MINUTES)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return username
