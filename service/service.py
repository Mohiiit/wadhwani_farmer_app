from sqlalchemy.orm import Session

from schema import schemas

from model import models


def create_farmer(db: Session, farmer: schemas.FarmerSignUp):
    # fake_hashed_password = user.password + "notreallyhashed"
    db_farmer = models.Farmer(
        farmer_name=farmer.farmer_name,
        state_name=farmer.state_name,
        district_name=farmer.district_name,
        village_name=farmer.village_name,
        username=farmer.username,
        password=farmer.password,
    )

    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer


def get_farmer(db: Session, username: str):
    return db.query(models.Farmer).filter(models.Farmer.username == username).first()


def get_farmers(db: Session, skip: int = 0, limit: int = 4):
    return db.query(models.Farmer).offset(skip).limit(limit).all()


def get_farmers_all(db: Session):
    return db.query(models.Farmer).all()
