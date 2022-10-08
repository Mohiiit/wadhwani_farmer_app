from sqlalchemy import Column, String, Boolean

from db.database import Base

# table for storing data
# username is same as phone-number
# username is used as the primary key for searching
class Farmer(Base):
    __tablename__ = "farmer"

    username = Column(String, primary_key=True, index=True, nullable=False)
    farmer_name = Column(String, nullable=True)
    state_name = Column(String, nullable=True)
    district_name = Column(String, nullable=True)
    village_name = Column(String, nullable=True)
    password = Column(String, nullable=True)
    phone_number = Column(String, nullable=False)
