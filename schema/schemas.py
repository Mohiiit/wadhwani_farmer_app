from pydantic import BaseModel
from typing import Union


class FarmerBase(BaseModel):
    username: str


class FarmerExport(FarmerBase):
    farmer_name: str
    state_name: str
    district_name: str
    village_name: str

    class Config:
        orm_mode = True


class FarmerLogIn(FarmerBase):
    password: str


class FarmerCreate(FarmerExport):
    password: str
    disabled: Union[bool, None] = None


class Token(BaseModel):
    access_token: str
    access_token_type: str
