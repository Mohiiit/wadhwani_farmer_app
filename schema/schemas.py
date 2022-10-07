from pydantic import BaseModel
from typing import Union, Optional


class FarmerBase(BaseModel):
    username: str


class FarmerExport(FarmerBase):
    farmer_name: str
    state_name: str
    district_name: str
    village_name: str

    class Config:
        orm_mode = True

class FarmerFinal(FarmerExport):
    phone_number: str

class FarmerLogIn(FarmerBase):
    password: str

class FarmerSignUp(FarmerExport):
    password: str

class FarmerCreate(FarmerExport):
    password: str
    disabled: Union[bool, None] = None

class FarmerUpdate(BaseModel):
    farmer_name: Optional[str] = None
    state_name: Optional[str] = None
    district_name: Optional[str] = None
    village_name: Optional[str] = None
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    access_token_type: str
