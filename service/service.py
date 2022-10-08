from sqlalchemy.orm import Session

from schema import schemas
from util import auth
from model import models

# function is called when a new farmer sign up and it will create the new farmer
# and will save it to the backend
def create_farmer(db: Session, farmer: schemas.FarmerSignUp):

    # creating a new farmer based on the data provided
    db_farmer = models.Farmer(
        farmer_name=farmer.farmer_name,
        state_name=farmer.state_name,
        district_name=farmer.district_name,
        village_name=farmer.village_name,
        username=farmer.username,
        phone_number=farmer.username, # phone number and username is same
        password=auth.get_password_hash(farmer.password), # hashed password will be store in the backend
    )

    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer


# function to call when user wants to add data using csv file
# the password here is create by backend and it is same as the phone number of the farmer
def create_farmer_csv(db: Session, farmer: schemas.FarmerExport):

    # creating a new farmer based on the data provided in csv file
    db_farmer = models.Farmer(
        farmer_name=farmer.farmer_name,
        state_name=farmer.state_name,
        district_name=farmer.district_name,
        village_name=farmer.village_name,
        username=farmer.username,
        phone_number=farmer.username,
        password=auth.get_password_hash(farmer.username), # password is same as the phone number
    )

    # checking for duplicates
    curr_farmer = get_farmer(db, db_farmer.username)

    # if farmer's phone number does not exist in the database, add it to the database
    if not curr_farmer:
        db.add(db_farmer)
        db.commit()
        db.refresh(db_farmer)
        return db_farmer

    return curr_farmer


# function will return the farmer with queried username (phone-number)
def get_farmer(db: Session, username: str):
    return (
        db.query(models.Farmer)
        .filter(models.Farmer.username == username)
        .first()
    )


# function will return the whole data 
def get_farmers_all(db: Session):
    return db.query(models.Farmer).all()


# function is used to update the data of farmer
def update_data(
    db: Session,
    new_farmer: schemas.FarmerUpdate,
    curr_farmer: schemas.FarmerExport,
):
    farmer_data = new_farmer.dict(exclude_unset=True)

    # iterating through the provided list
    for key, pair in farmer_data.items():

        # checking if data was provided or it's empty
        if pair != "string" and pair != "":

            # if it's not empty
            if key == "password":
                # if farmer wants to change password, store the hashed password
                setattr(curr_farmer, key, auth.get_password_hash(pair))
            else:
                # otherwise simply change the data
                setattr(curr_farmer, key, pair)

    # adding the updated data to the database
    db.add(curr_farmer)
    db.commit()
    db.refresh(curr_farmer)
    return curr_farmer
