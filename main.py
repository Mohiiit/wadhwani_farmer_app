from datetime import timedelta
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    File,
    UploadFile,
    status,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
import csv
import codecs
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
ACCESS_TOKEN_EXPIRES_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/upload", response_model=schemas.Message)
async def upload_farmer_data_using_csv(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    
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
    data = {
        "status": "ok",
        "detail": "file uploaded"
    }
    return data


@app.get("/farmers", response_model=list[schemas.FarmerFinal])
async def fetch_all_farmer_data(
    db: Session = Depends(deps.get_db),
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):
    farmers = service.get_farmers_all(db)
    return farmers


@app.get("/farmers/{lang}", response_model=list[schemas.FarmerFinal])
async def fetch_farmer_data_in_given_language(
    lang: str = "hi",
    db: Session = Depends(deps.get_db),
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):

    farmers = service.get_farmers_all(db)
    for i in farmers:
        translated_data = await translate.join_farmer_data(i, lang)

        i.farmer_name = translated_data[0]
        i.state_name = translated_data[1]
        i.district_name = translated_data[2]
        i.village_name = translated_data[3]

    return farmers


@app.get("/translate", response_model=schemas.Message)
async def translate_the_given_text(
    lang: str = "hi",
    text: str = "test",
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):
    translated_text = await translate.translate_text(text, lang)
    translated_text = translated_text["translatedText"]
    data = {
        "status": "ok",
        "detail": f"You translated text is {translated_text}"
    }
    return data;


@app.post("/login", response_model=schemas.Token)
async def user_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):
    farmer = service.get_farmer(db, form_data.username)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your details doesn't exist, please signup first",
            headers={"WWW-Authenticate": "Bearer"},
        )
    farmer = auth.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong Password, If you are trying for first time, password is your phone-number.",
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


@app.get("/me", response_model=schemas.FarmerExport)
async def read_user_me(
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):
    return farmer


@app.patch("/update/{username}", response_model=schemas.FarmerExport)
async def update_data(
    username: str,
    new_farmer: schemas.FarmerUpdate,
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    if username != farmer.username:
        raise HTTPException(
            status_code=401,
            detail=f"You are allowed to make changes for {farmer.username} but you requested for {username}",
        )

    if farmer.disabled:
        raise HTTPException(status_code=401, detail="Inactive user")

    return service.update_data(db, new_farmer, farmer)


@app.get("/health")
async def check_health():
    return {"message": "Farmer App"}
