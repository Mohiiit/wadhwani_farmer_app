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

# this endpoint is for uploading the csv file to the database
@app.post("/upload", response_model=schemas.Message)
async def upload_farmer_data_using_csv(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):
    # reading the file
    csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    
    # iterating through every row
    for rows in csvReader:
        db_farmer = schemas.FarmerExport(
            farmer_name=rows["farmer_name"],
            state_name=rows["state_name"],
            district_name=rows["district_name"],
            village_name=rows["village_name"],
            username=rows["phone_number"],
        )
        # sending the data to the service to finally save it to the DB
        service.create_farmer_csv(db, db_farmer)

    file.file.close()

    # returning the ok status after data added successfully
    data = {
        "status": "ok",
        "detail": "file uploaded"
    }
    return data


# endpoint created to fetch all the data available in the table
@app.get("/farmers", response_model=list[schemas.FarmerFinal])
async def fetch_all_farmer_data(
    db: Session = Depends(deps.get_db),
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):
    farmers = service.get_farmers_all(db)
    return farmers


# endpoint is created to fetch the data and then convert it to the desired language
@app.get("/farmers/{lang}", response_model=list[schemas.FarmerFinal])
async def fetch_farmer_data_in_given_language(
    lang: str = "hi",
    db: Session = Depends(deps.get_db),
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):

    # fetching all the data here
    farmers = service.get_farmers_all(db)

    # going through every row of data fetched
    for i in farmers:
        # combining the rows to translate it altogether
        translated_data = await translate.join_farmer_data(i, lang)

        # changing the data to the translated data
        i.farmer_name = translated_data[0]
        i.state_name = translated_data[1]
        i.district_name = translated_data[2]
        i.village_name = translated_data[3]

    # returning the list with translated data
    return farmers


# endpoint to translate the given text in the given language
@app.get("/translate", response_model=schemas.Message)
async def translate_the_given_text(
    lang: str = "hi",
    text: str = "test",
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):

    # calling the helper function to translate the text
    translated_text = await translate.translate_text(text, lang)
    translated_text = translated_text["translatedText"]

    # returning ok status after successful translation
    data = {
        "status": "ok",
        "detail": f"You translated text is {translated_text}"
    }
    return data


# endpoint for the users to login
@app.post("/login", response_model=schemas.Token)
async def user_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
):

    # firstly checking whether the farmer exist in the database or not
    farmer = service.get_farmer(db, form_data.username)

    # if it does not exist, raise the exception
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your details doesn't exist, please signup first",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # if it exists, authenticate the farmer
    farmer = auth.authenticate_user(
        db, form_data.username, form_data.password
    )

    # if it fails, raise the exception with wrong credentials
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong Password, If you are trying for first time, password is your phone-number.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # access token time limit
    access_token_expires = timedelta(
        minutes=int(ACCESS_TOKEN_EXPIRES_MINUTES)
    )

    # creting a new access token
    access_token = auth.create_access_token(
        data={"sub": farmer.username}, expires_delta=access_token_expires
    )

    # saving the token for future api calls
    response.set_cookie(key="access_token", value=f"Bearer {access_token}")
    
    # returning the access token as response
    access_token = {
        "access_token": access_token,
        "access_token_type": "bearer",
    }
    return access_token


# endpoint for new users to signup
@app.post("/signup", response_model=schemas.FarmerExport)
async def user_signup(
    signupitem: schemas.FarmerSignUp, db: Session = Depends(deps.get_db)
):
    # checking for duplicate entry
    farmer = service.get_farmer(db, signupitem.username)

    # if farmer with the same number already exists in the DB, raise exception
    if farmer:
        raise HTTPException(
            status_code=400,
            detail="Farmer with this phone number already exists",
        )

    # it it does not exist, create new farmer and return it
    farmer = service.create_farmer(db, signupitem)
    return farmer


# endpoint to get the current logged in user
@app.get("/me", response_model=schemas.FarmerExport)
async def read_user_me(
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
):
    return farmer


# endpoints for user to update their data except their phone number and user-name
@app.patch("/update/{username}", response_model=schemas.FarmerExport)
async def update_data(
    username: str,
    new_farmer: schemas.FarmerUpdate,
    farmer: schemas.FarmerExport = Depends(auth.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    # checking whether the user is changing data for themself only
    if username != farmer.username:
        raise HTTPException(
            status_code=401,
            detail=f"You are allowed to make changes for {farmer.username} but you requested for {username}",
        )
    
    # update the data and return it
    return service.update_data(db, new_farmer, farmer)


# endpoints to check whether backend is working or not
@app.get("/health")
async def check_health():
    return {"message": "Farmer App"}
