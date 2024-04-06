from fastapi.testclient import TestClient
from fastapi import status
import requests

from main import app

from main import app
import json
import uuid


url = "http://127.0.0.1:8000"

client = TestClient(app=app)


def test_user_login_endpoint():

    payload = json.dumps(
        {"email_id": "admin@everimpact.com", "password": "admin@everimpact"}
    )
    headers = {"Content-Type": "application/json"}

    response = client.request("GET", "/users/login", headers=headers, data=payload)

    global admin_token
    admin_token = response.json()["token"]
    assert response.status_code == status.HTTP_200_OK


def test_list_all_coverage():
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/coverage", headers=headers)
    global coverage_id
    coverage_id = response.json()[0]["id"]
    assert response.status_code == 200


def test_create_user():

    headers = {"Content-Type": "application/json"}
    random_uid = str(uuid.uuid4())
    data = {
        "email_id": f"{random_uid}@test.com",
        "password": random_uid,
        "coverage_id": coverage_id,
    }

    response = client.post("/users", json=data, headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_get_credential_endpoint():
    payload = {}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request("GET", "/users/me", headers=headers, data=payload)
    assert response.status_code == status.HTTP_200_OK


def test_get_list_users_endpoint():
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request("GET", "/users/all", headers=headers)
    global user_id
    user_id = response.json()["data"][0]["id"]
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json()["data"], list)


def test_change_user_permission_endpoint():
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"is_admin": True}
    response = client.request("PUT", f"/users/{user_id}", headers=headers, json=payload)
    assert response.status_code == status.HTTP_200_OK


def test_delete_user_endpoint():
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request("DELETE", f"/users/{user_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_create_coverage_endpoint():
    random_uuid = str(uuid.uuid4())
    payload = {"name": random_uuid}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request("POST", "/coverage", headers=headers, json=payload)
    assert response.status_code == status.HTTP_200_OK


def test_get_sensor_data_endpoint():
    payload = {"page_no": 0}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request(
        "GET", "/coverage/Dijon/sensor", headers=headers, json=payload
    )
    assert response.status_code == status.HTTP_200_OK


def test_filter_sensor_data_endpoint():
    payload = {
        "start_time": "20220323054307",
        "end_time": "20220423054307",
        "polygon": "POLYGON ((5.1135 47.304, 5.115 47.304, 5.115 47.307, 5.1135 47.307, 5.1135 47.304))",
    }

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request(
        "GET", "/coverage/Dijon/sensor/filter", headers=headers, json=payload
    )
    assert response.status_code == status.HTTP_200_OK


def test_get_sink_data_endpoint():
    payload = {}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.request(
        "GET", "/coverage/Ishinomaki/sinks", headers=headers, json=payload
    )
    assert response.status_code == status.HTTP_200_OK


def test_filter_sink_data_endpoint():
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"start_time": "19351001000000", "end_time": "19661101000100"}
    response = client.request(
        "GET", "/coverage/Ishinomaki/sinks/filter", headers=headers, json=payload
    )
    assert response.status_code == status.HTTP_200_OK


def test_delete_coverage_endpoint():
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/coverage", headers=headers)
    for x in response.json():
        if x["name"] not in ["Dijon", "Ishinomaki"]:
            coverage_name = x["name"]
            break

    response = client.request(
        "DELETE", f"/coverage/{coverage_name}", headers=headers, json={}
    )
    assert response.status_code == status.HTTP_200_OK
