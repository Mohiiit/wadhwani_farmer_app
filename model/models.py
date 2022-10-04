from sqlalchemy import Column, String

from db.database import Base


class Farmer(Base):
    __tablename__ = "farmer"

    farmer_name = Column(String, nullable=True)
    state_name = Column(String, nullable=True)
    district_name = Column(String, nullable=True)
    village_name = Column(String, nullable=True)
    phone_number = Column(String, primary_key=True, index=True, nullable=False)
