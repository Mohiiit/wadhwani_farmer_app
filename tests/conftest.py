from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator, Any

import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import schemas
from util import auth, deps
from service import service
from model import models
from db import database
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./project_farmer_test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

database.Base.metadata.create_all(bind=engine)


@pytest.fixture
def client() -> Generator[TestClient, Any, None]:
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[deps.get_db] = override_get_db
    client = TestClient(app)
    yield client


@pytest.fixture
def token_headers(client: TestClient):
    new_farmer = schemas.FarmerSignUp(
        farmer_name="test",
        state_name="test",
        district_name="test",
        village_name="test",
        username="test",
        password="test",
    )
    db = TestingSessionLocal()
    farmer = db.query(models.Farmer).filter(models.Farmer.username == new_farmer.username).first()
    if not farmer:
        service.create_farmer(db, new_farmer)

    data = {"username": new_farmer.username, "password": new_farmer.password}
    response = client.post("/login", data=data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}