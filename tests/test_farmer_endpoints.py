from pydoc import cli
from urllib import response
from schema import schemas
from util import auth, deps
from service import service
from model import models
from db import database
from main import app
from fastapi import Depends
from http import client

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator, Any

import pytest
import sys
import os


def test_auth():
    assert 2 == 2

def test_upload_csv_without_login(client):
    test_file = {"file": open("./test.csv", "rb")}
    response = client.post("/upload", files=test_file)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_get_farmers_endpoint_without_login(client):
    response = client.get("/farmers")
    assert response.status_code == 401

def test_get_farmers_endpoint(client, token_headers):
    response = client.get("/farmers")
    assert response.status_code == 200

def test_upload_csv(client, token_headers):
    test_file = {"file": open("./test.csv", "rb")}
    response = client.post("/upload", files=test_file)
    assert response.status_code == 200
    assert response.json() == {"files": "files added"}