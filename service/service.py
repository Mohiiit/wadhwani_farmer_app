from sqlalchemy.orm import Session

from schema import schemas
from util import auth
from model import models


def create_farmer(db: Session, farmer: schemas.FarmerSignUp):
    db_farmer = models.Farmer(
        farmer_name=farmer.farmer_name,
        state_name=farmer.state_name,
        district_name=farmer.district_name,
        village_name=farmer.village_name,
        username=farmer.username,
        phone_number=farmer.username,
        password=auth.get_password_hash(farmer.password),
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
        phone_number=farmer.username,
        password=auth.get_password_hash(farmer.username),
    )

    curr_farmer = get_farmer(db, db_farmer.username)

    if not curr_farmer:
        db.add(db_farmer)
        db.commit()
        db.refresh(db_farmer)
        return db_farmer

    return curr_farmer


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


def update_data(
    db: Session,
    new_farmer: schemas.FarmerUpdate,
    curr_farmer: schemas.FarmerExport,
):
    farmer_data = new_farmer.dict(exclude_unset=True)
    for key, pair in farmer_data.items():
        if pair != "string" and pair != "":
            if key == "password":
                setattr(curr_farmer, key, auth.get_password_hash(pair))
            else:
                setattr(curr_farmer, key, pair)

    db.add(curr_farmer)
    db.commit()
    db.refresh(curr_farmer)
    return curr_farmer
