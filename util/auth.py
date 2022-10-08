import os
from datetime import datetime, timedelta
from typing import Union

from db.database import engine
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from schema import schemas
from service import service
from sqlalchemy.orm import Session

from util import deps, cookie

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = cookie.OAuth2PasswordBearerWithCookie(tokenUrl="/login")

SECERT_KEY = os.getenv("SECERT_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    farmer = service.get_farmer(db, username)
    if not farmer:
        return False
    if not verify_password(password, farmer.password):
        return False
    return farmer


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECERT_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    db: Session = Depends(deps.get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            access_token, SECERT_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        access_token_data = schemas.FarmerBase(username=username)
    except JWTError:
        raise credentials_exception
    farmer = service.get_farmer(db, username=access_token_data.username)
    if farmer is None:
        raise credentials_exception
    return farmer


async def get_current_active_user(
    farmer: schemas.FarmerExport = Depends(get_current_user),
):
    if not farmer:
        raise HTTPException(status_code=400, detail="not the user")
    if farmer.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return farmer
