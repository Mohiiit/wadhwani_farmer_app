from pydoc import cli
from urllib import response
from schema import schemas
from util import auth, deps
from service import service
from model import models
from db import database
from main import app
from fastapi import Depends
from fastapi.testclient import TestClient
from http import client

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./project_farmer_auth_test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

database.Base.metadata.create_all(bind=engine)


def override_get_db():
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    yield db

    db.rollback()
    connection.close()

app.dependency_overrides[deps.get_db] = override_get_db

client = TestClient(app)

def test_auth():
    assert 2==2


def test_login_when_user_does_not_exist():
    data = {
        "username": "test",
        "password": "test",
    }
    response = client.post("/login", data=data)
    assert response.status_code == 401


def test_login_when_user_submit_wrong_password(db: Session = Depends(override_get_db)):
    new_farmer = schemas.FarmerSignUp(
        farmer_name="test",
        state_name="test",
        district_name="test",
        village_name="test",
        username="test",
        password="test",
    )
    service.create_farmer(db ,new_farmer)
    data = schemas.FarmerLogIn(
        username="test",
        password="nottest",
    )
    response = client.post("/login", data)
    assert response.status_code == 401
# def test_wrong_login()