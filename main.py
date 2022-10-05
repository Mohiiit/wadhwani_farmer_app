from pydoc import Helper
from datetime import datetime, timedelta
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    File,
    UploadFile,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
import csv
import codecs
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from fastapi import Response

from sqlalchemy.orm import Session

from model import models

from schema import schemas
import os
from service import service
from db.database import engine
from util import deps, translate, auth
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = {
    "http://localhost",
    "http://localhost:3000",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload(
    file: UploadFile = File(...), db: Session = Depends(deps.get_db)
):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    data = {"files": "files added"}
    for rows in csvReader:
        db_farmer = schemas.FarmerExport(
            farmer_name=rows["farmer_name"],
            state_name=rows["state_name"],
            district_name=rows["district_name"],
            village_name=rows["village_name"],
            username=rows["phone_number"],
        )
        service.create_farmer_csv(db, db_farmer)

    file.file.close()
    return data


@app.get("/farmers/", response_model=list[schemas.FarmerExport])
async def read_farmers(db: Session = Depends(deps.get_db)):
    farmers = service.get_farmers_all(db)
    return farmers


@app.get("/farmers/{lang}", response_model=list[schemas.FarmerExport])
async def read_farmers_lang(
    skip: int = 0,
    limit: int = 4,
    lang: str = "hi",
    db: Session = Depends(deps.get_db),
):
    farmers = service.get_farmers(db, skip=skip, limit=limit)
    for i in farmers:
        farmer_name = await translate.translate_text(i.farmer_name, lang)
        state_name = await translate.translate_text(i.state_name, lang)
        district_name = await translate.translate_text(
            i.district_name, lang
        )
        village_name = await translate.translate_text(i.village_name, lang)

        i.farmer_name = farmer_name["translatedText"]
        i.state_name = state_name["translatedText"]
        i.district_name = district_name["translatedText"]
        i.village_name = village_name["translatedText"]

    return farmers


@app.get("/translate", response_model=str)
async def translate_text(
    lang: str = "hi",
    text: str = "test",
):
    translated_text = await translate.translate_text(text, lang)
    return translated_text["translatedText"]


SECERT_KEY = os.getenv("SECERT_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES")


@app.post("/login", response_model=schemas.Token)
async def user_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):
    farmer = auth.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(ACCESS_TOKEN_EXPIRES_MINUTES)
    )
    access_token = auth.create_access_token(
        data={"sub": farmer.username}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=f"Bearer {access_token}")
    access_token = {
        "access_token": access_token,
        "access_token_type": "bearer",
    }
    return access_token


@app.post("/signup", response_model=schemas.FarmerExport)
async def user_signup(
    signupitem: schemas.FarmerExport, db: Session = Depends(deps.get_db)
):
    farmer = service.get_farmer(db, signupitem.username)
    if farmer:
        raise HTTPException(
            status_code=400,
            detail="Farmer with this phone number already exists",
        )

    farmer = service.create_farmer(db, signupitem)
    return farmer


@app.get("/users/me/", response_model=schemas.FarmerExport)
async def read_users_me(
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):
    return farmer
