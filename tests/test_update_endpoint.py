import json

def test_update_endpoint_with_wrong_credentials(client):
    updated_farmer = {
        "farmer_name": "updated_test",
        "state_name": "updated_test",
        "district_name": "updated_test",
        "village_name": "updated_test",
        "password": "updated_test",
    }
    response = client.patch("/update/updated_test", json.dumps(updated_farmer))
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_update_endpoint_with_wrong_username_passed(client, token_headers):
    updated_farmer = {
        "farmer_name": "updated_test",
        "state_name": "updated_test",
        "district_name": "updated_test",
        "village_name": "updated_test",
        "password": "updated_test",
    }
    response = client.patch("/update/updated_test", json.dumps(updated_farmer))
    assert response.status_code == 401
    assert response.json() == {"detail": "You are allowed to make changes for test but you requested for updated_test"}


def test_update_endpoint_when_user_update_data(client, token_headers):
    updated_farmer = {
        "farmer_name": "updated_test",
        "state_name": "updated_test",
        "village_name": "updated_test",
    }
    response = client.patch("/update/test", json.dumps(updated_farmer))
    assert response.status_code == 200
    assert response.json()["username"] == "test"
    assert response.json()["farmer_name"] == "updated_test"
    assert response.json()["state_name"] == "updated_test"
    assert response.json()["district_name"] == "test"
    assert response.json()["village_name"] == "updated_test" 
    updated_farmer = {
        "farmer_name": "test",
        "state_name": "test",
        "village_name": "test",
    }
    response = client.patch("/update/test", json.dumps(updated_farmer))
    assert response.status_code == 200
    assert response.json()["username"] == "test"
    assert response.json()["farmer_name"] == "test"
    assert response.json()["state_name"] == "test"
    assert response.json()["district_name"] == "test"
    assert response.json()["village_name"] == "test" 