import json
from util.auth import verify_password, get_password_hash


def test_password_hash_functions():
    hashed_password = get_password_hash("testing")
    assert verify_password("testing", hashed_password) == True
    assert verify_password("testindg", hashed_password) == False


def test_google_translate_api_when_user_logged_in(client, token_headers):
    data = {"lang": "hi", "text": "test"}
    response = client.get("/translate", data=data)
    assert response.status_code == 200
    assert response.json() == {"translated_text": "परीक्षण"}


def test_google_translate_api_when_user_logged_in(client):
    data = {"lang": "hi", "text": "test"}
    response = client.get("/translate", data=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_health_endpoint_before_login(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "I am okay"}


def test_health_endpoint_after_login(client, token_headers):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "I am okay"}


def test_me_endpoint_before_login(client):
    response = client.get("/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_me_endpoint_after_login(client, token_headers):
    response = client.get("/me")
    assert response.status_code == 200
    assert response.json()["username"] == "test"
    assert response.json()["farmer_name"] == "test"
    assert response.json()["state_name"] == "test"
    assert response.json()["district_name"] == "test"
    assert response.json()["village_name"] == "test"


def test_login_when_user_does_not_exist(client):
    data = {
        "username": "something_random",
        "password": "test",
    }
    response = client.post("/login", data=data)
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Your details doesn't exist, please signup first"
    }


def test_login_with_correct_credentials(client, token_headers):
    data = {
        "username": "test",
        "password": "test",
    }
    response = client.post("/login", data=data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token_headers == {"Authorization": f"Bearer {token}"}


def test_login_with_wrong_password(client, token_headers):
    data = {
        "username": "test",
        "password": "wrong",
    }
    response = client.post("/login", data=data)
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Wrong Password, If you are trying for first time, password is your phone-number."
    }


def test_signup_with_username_already_exists(client, token_headers):
    new_farmer = {
        "farmer_name": "test",
        "state_name": "test",
        "district_name": "test",
        "village_name": "test",
        "username": "test",
        "password": "test",
    }
    response = client.post("/signup", json.dumps(new_farmer))
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Farmer with this phone number already exists"
    }
