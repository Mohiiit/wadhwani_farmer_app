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


# function to verify the passwords
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# function to get the password hash
def get_password_hash(password):
    return pwd_context.hash(password)


# function to authenticate the user
def authenticate_user(db: Session, username: str, password: str):

    # getting the farmer with username provided
    farmer = service.get_farmer(db, username)

    # returning false when it does not exist in the database
    if not farmer:
        return False

    # returning false if the password does not match with password stored in database.
    if not verify_password(password, farmer.password):
        return False

    # returning farmer data when password matches
    return farmer


# creating a new access token
def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
):

    # storing the copy of the provided data
    to_encode = data.copy()

    # updating the expire time of the token
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    # updating the expire time in the data
    to_encode.update({"exp": expire})

    # encoding the token with new expire time with the secret key using algorithm
    encoded_jwt = jwt.encode(to_encode, SECERT_KEY, algorithm=ALGORITHM)

    # returning the token
    return encoded_jwt


# function to get the current user logged in
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
        # decoding the token provided with secret key using alogrithm
        payload = jwt.decode(
            access_token, SECERT_KEY, algorithms=[ALGORITHM]
        )

        # getting the username from the decoded token
        username: str = payload.get("sub")

        # raising exception when no username is found
        if username is None:
            raise credentials_exception

        # storing the username found
        found_username = schemas.FarmerBase(username=username)
    except JWTError:
        raise credentials_exception

    # checking whether the "found-username" exist in the database or not
    farmer = service.get_farmer(db, username=found_username.username)

    # raising the exception when there is no farmer with "found-username"
    if farmer is None:
        raise credentials_exception

    # returning farmer data if found the "found-username"
    return farmer


# helper function which will call the above function.
async def get_current_active_user(
    farmer: schemas.FarmerExport = Depends(get_current_user),
):
    if not farmer:
        raise HTTPException(status_code=400, detail="not the user")
    return farmer
