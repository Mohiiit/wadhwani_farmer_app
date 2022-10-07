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


def test_login_when_user_does_not_exist(client):
    data = {
        "username": "something_random",
        "password": "test",
    }
    response = client.post("/login", data=data)
    assert response.status_code == 401

