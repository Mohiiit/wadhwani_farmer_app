from typing import Any
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

import csv
import codecs

from sqlalchemy.orm import Session

from model import models

from schema import schemas

from service import service
from db.database import SessionLocal, engine
from util import deps


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/upload")
async def upload(file: UploadFile = File(...), db: Session = Depends(deps.get_db)):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    data = {}
    for rows in csvReader:
        print(rows)
        db_farmer = schemas.FarmerBase(
            farmer_name=rows["farmer_name"],
            state_name=rows["state_name"],
            district_name=rows["district_name"],
            village_name=rows["village_name"],
            phone_number=rows["phone_number"],
        )
        service.create_farmer(db, db_farmer)

    file.file.close()
    return data


@app.get("/farmers/", response_model=list[schemas.FarmerBase])
async def read_farmers(
    skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)
):
    farmers = service.get_farmers(db, skip=skip, limit=limit)
    return farmers
