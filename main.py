from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, status

import csv
import codecs
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt

from sqlalchemy.orm import Session

from model import models

from schema import schemas
import os
from service import service
from db.database import engine
from util import deps, translate
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
async def upload(file: UploadFile = File(...), db: Session = Depends(deps.get_db)):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    data = {"files": "files added"}
    for rows in csvReader:
        db_farmer = schemas.FarmerBase(
            farmer_name=rows["farmer_name"],
            state_name=rows["state_name"],
            district_name=rows["district_name"],
            village_name=rows["village_name"],
            username=rows["phone_number"],
        )
        service.create_farmer(db, db_farmer)

    file.file.close()
    return data


@app.get("/farmers/", response_model=list[schemas.Farmer])
async def read_farmers(db: Session = Depends(deps.get_db)):
    farmers = service.get_farmers_all(db)
    return farmers


@app.get("/farmers/{lang}", response_model=list[schemas.FarmerBase])
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
        district_name = await translate.translate_text(i.district_name, lang)
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

test_user = {
    "username": "mohit",
    "password": "something",
}


@app.post("/login")
async def user_login(
    loginitem: schemas.FarmerLogIn, db: Session = Depends(deps.get_db)
):
    data = jsonable_encoder(loginitem)
    farmer = service.get_farmer(db, loginitem.username)
    if not farmer:
        raise HTTPException(
            status_code=404,
            detail="Farmer with this phone number doesn't exist, please signup",
        )

    if farmer.password == loginitem.password:
        encoded_jwt = jwt.encode(data, SECERT_KEY, algorithm=ALGORITHM)
        return {"token": encoded_jwt}
    else:
        raise HTTPException(
            status_code=404,
            detail="Wrong password, please try again",
        )


@app.post("/signup", response_model=schemas.Farmer)
async def user_signup(
    signupitem: schemas.FarmerSignUp, db: Session = Depends(deps.get_db)
):
    farmer = service.get_farmer(db, signupitem.username)
    if farmer:
        raise HTTPException(
            status_code=400,
            detail="Farmer with this phone number already exists",
        )

    farmer = service.create_farmer(db, signupitem)
    return farmer
