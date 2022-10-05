from sqlalchemy.orm import Session

from schema import schemas
from util import auth
from model import models


def create_farmer(db: Session, farmer: schemas.FarmerExport):
    db_farmer = models.Farmer(
        farmer_name=farmer.farmer_name,
        state_name=farmer.state_name,
        district_name=farmer.district_name,
        village_name=farmer.village_name,
        username=farmer.username,
        password=auth.get_password_hash(farmer.password),
        disabled=False,
    )

    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer


def create_farmer_csv(db: Session, farmer: schemas.FarmerExport):
    db_farmer = models.Farmer(
        farmer_name=farmer.farmer_name,
        state_name=farmer.state_name,
        district_name=farmer.district_name,
        village_name=farmer.village_name,
        username=farmer.username,
        disabled=False,
        password=auth.get_password_hash(farmer.username),
    )

    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer


def get_farmer(db: Session, username: str):
    return (
        db.query(models.Farmer)
        .filter(models.Farmer.username == username)
        .first()
    )


def get_farmers(db: Session, skip: int = 0, limit: int = 4):
    return db.query(models.Farmer).offset(skip).limit(limit).all()


def get_farmers_all(db: Session):
    return db.query(models.Farmer).all()
