from sqlalchemy import Column, String, Boolean

from db.database import Base


class Farmer(Base):
    __tablename__ = "farmer"

    username = Column(String, primary_key=True, index=True, nullable=False)
    farmer_name = Column(String, nullable=True)
    state_name = Column(String, nullable=True)
    district_name = Column(String, nullable=True)
    village_name = Column(String, nullable=True)
    password = Column(String, nullable=True)
    disabled = Column(Boolean)
    phone_number = Column(String, nullable=False)
