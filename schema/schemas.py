from typing import Union

from pydantic import BaseModel

from model.models import Farmer


class FarmerBase(BaseModel):
    farmer_name: str
    state_name: str
    district_name: str
    village_name: str
    phone_number: str

    class Config:
        orm_mode = True


class Farmers(BaseModel):
    info: list[FarmerBase] = []


class FarmerCreate(FarmerBase):
    pass
