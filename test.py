import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    app = FastAPI()
    with TestClient(app) as client:
        yield client


def test_main_route(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_coil(client):
    coil_data = {"length": 10.0, "weight": 20.0}
    response = client.post("/api/coil", json=coil_data)
    assert response.status_code == 200
    assert "id" in response.json()

    response = client.get(f"/api/coil/{response.json()['id']}")
    assert response.status_code == 200
    assert response.json()["length"] == coil_data["length"]
    assert response.json()["weight"] == coil_data["weight"]


def test_delete_coil(client):
    coil_data = {"length": 10.0, "weight": 20.0}
    response = client.post("/api/coil", json=coil_data)
    assert response.status_code == 200
    coil_id = response.json()["id"]

    response = client.delete(f"/api/coil/{coil_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Coil deleted"

    response = client.get(f"/api/coil/{coil_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Coil not found"


def test_get_coils(client):
    for i in range(5):
        coil_data = {"length": 10.0 * i, "weight": 20.0 * i}
        response = client.post("/api/coil", json=coil_data)
        assert response.status_code == 200

    response = client.get("/api/coil")
    assert response.status_code == 200
    assert len(response.json()) == 5

    response = client.get("/api/coil?id_min=2&id_max=4")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert all(2 <= coil["id"] <= 4 for coil in response.json())

    response = client.get("/api/coil?weight_min=40&weight_max=80")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert all(40 <= coil["weight"] <= 80 for coil in response.json())

    response = client.get("/api/coil?length_min=20&length_max=60")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert all(20 <= coil["length"] <= 60 for coil in response.json())
