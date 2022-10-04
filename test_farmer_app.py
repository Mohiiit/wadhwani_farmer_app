from http import client
from urllib import response
from fastapi.testclient import TestClient

from service import service
from main import app
from util import deps
from db import database
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./project_farmer_test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

database.Base.metadata.create_all(bind=engine)


def override_get_db():
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    yield db

    db.rollback()
    connection.close()


# def override_get_db():
#     connection = engine.connect()
#     connection.begin()
#     db = TestingSessionLocal(bind=connection)
#     yield db
#     db.close()
#     # db.rollback()
#     connection.close()

app.dependency_overrides[deps.get_db] = override_get_db

client = TestClient(app)


def test_create_farmer():
    test_file = {"file": open("./test.csv", "rb")}
    response = client.post("/upload", files=test_file)
    assert response.status_code == 200


def test_create_farmer_data():
    test_file = {"file": open("./test.csv", "rb")}
    response = client.post("/upload", files=test_file)
    assert response.json() == {"files": "files added"}


# def test_get_farmer_data():
#     test_file = {'file': open("./test.csv", "rb")}
#     client.post("/upload", files=test_file)
#     assert response.status_code==200
#     response.json()
#     assert len(response.json()) == 4
