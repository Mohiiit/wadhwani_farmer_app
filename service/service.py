from sqlalchemy.orm import Session

from schema import schemas

from model import models


def create_farmer(db: Session, farmer: schemas.FarmerCreate):
    # fake_hashed_password = user.password + "notreallyhashed"
    db_farmer = models.Farmer(
        farmer_name=farmer.farmer_name, 
        state_name=farmer.state_name,
        district_name=farmer.district_name,
        village_name=farmer.village_name,
        phone_number=farmer.phone_number,
        )
    
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer


def get_farmer(db: Session, phone_number: str):
    return db.query(models.Farmer).filter(models.Farmer.phone_number == phone_number).first()


def get_farmers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Farmer).offset(skip).limit(limit).all()
