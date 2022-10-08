def test_upload_csv_when_user_is_not_logged_in(client):
    test_file = {"file": open("./test.csv", "rb")}
    response = client.post("/upload", files=test_file)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_upload_csv_when_user_is_logged_in(client, token_headers):
    test_file = {"file": open("./test.csv", "rb")}
    response = client.post("/upload", files=test_file)
    assert response.status_code == 200
    assert response.json() == {"message": "data added"}


def test_get_farmers_endpoint_without_user_login(client):
    response = client.get("/farmers")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_farmers_endpoint_when_user_is_logged_in(
    client, token_headers
):
    response = client.get("/farmers")
    assert response.status_code == 200
    assert response.json()[0]["username"] == "test"
    assert response.json()[0]["farmer_name"] == "test"
    assert response.json()[0]["state_name"] == "test"
    assert response.json()[0]["district_name"] == "test"
    assert response.json()[0]["village_name"] == "test"
    assert response.json()[0]["phone_number"] == "test"


def test_get_farmers_data_in_hindi(client, token_headers):
    response = client.get("/farmers/hi")
    assert response.status_code == 200
    assert response.json()[0]["username"] == "test"
    assert response.json()[0]["farmer_name"] == "परीक्षण"
    assert response.json()[0]["state_name"] == " परीक्षण"
    assert response.json()[0]["district_name"] == " परीक्षण"
    assert response.json()[0]["village_name"] == " परीक्षण"
    assert response.json()[0]["phone_number"] == "test"


def test_get_farmers_data_in_hindi_without_user_login(client):
    response = client.get("/farmers/hi")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
