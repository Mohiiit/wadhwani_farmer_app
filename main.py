from fastapi import Depends, FastAPI, HTTPException, File, UploadFile

import csv
import codecs

from sqlalchemy.orm import Session

from model import models

from schema import schemas

from service import service
from db.database import engine
from util import deps, translate


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/upload")
async def upload(
    file: UploadFile = File(...), db: Session = Depends(deps.get_db)
):
    csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    data = {}
    for rows in csvReader:
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


@app.get("/farmers/{lang}", response_model=list[schemas.FarmerBase])
async def read_farmers_lang(
    lang: str,
    skip: int = 0,
    limit: int = 100,
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
