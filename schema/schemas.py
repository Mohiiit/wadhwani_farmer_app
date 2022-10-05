from pydantic import BaseModel


class FarmerBase(BaseModel):
    username: str


class Farmer(FarmerBase):
    farmer_name: str
    state_name: str
    district_name: str
    village_name: str

    class Config:
        orm_mode = True


class Farmers(BaseModel):
    info: list[FarmerBase] = []


class FarmerLogIn(FarmerBase):
    password: str


class FarmerSignUp(Farmer):
    password: str
