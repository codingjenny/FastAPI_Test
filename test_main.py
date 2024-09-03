import pytest
from fastapi.testclient import TestClient
from main import app
import zipfile

client = TestClient(app)

@pytest.fixture
def user_data():
    return {"username": "testuser", "password": "testpassword"}

def test_register_user(user_data):
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == user_data["username"]

def test_login_user(user_data):
    client.post("/register", json=user_data)

    response = client.post("/login", data=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    return response.json()["access_token"]

def test_upload_file(user_data):
    token = test_login_user(user_data)

    zip_filename = "test.zip"
    with zipfile.ZipFile(zip_filename, "w") as zip_file:
        zip_file.writestr("test/A.txt", "A content")
        zip_file.writestr("test/B.txt", "B content")

    with open(zip_filename, "rb") as zip_file:
        response = client.post(
            "/uploadfile/",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (zip_filename, zip_file, "application/zip")}
        )

    assert response.status_code == 200
    assert response.json()["status"] == "Success"

def test_get_upload_records(user_data):
    token = test_login_user(user_data)

    zip_filename = "test.zip"
    with zipfile.ZipFile(zip_filename, "w") as zip_file:
        zip_file.writestr("test/A.txt", "A content")
        zip_file.writestr("test/B.txt", "B content")

    with open(zip_filename, "rb") as zip_file:
        client.post(
            "/uploadfile/",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (zip_filename, zip_file, "application/zip")}
        )

    response = client.get("/upload-records/", params={"user": "testuser"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    records = response.json()
    assert len(records) > 0
    assert records[0]["user"] == "testuser"

