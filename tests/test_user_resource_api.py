from datetime import datetime

import pytest
from sqlalchemy.orm import sessionmaker
from app.api import routes
from app.api.routes import create_app
from app.services import reservation_service, resource_service, user_service


def configure_api(session, monkeypatch):
    monkeypatch.setattr(
        routes,
        "Session",
        sessionmaker(bind=session.get_bind()),
    )
    app = create_app()
    return app.test_client()


@pytest.mark.parametrize("name", ["Ania", " Ania "])
def test_create_user_success(session, monkeypatch, name):
    client = configure_api(session, monkeypatch)

    response = client.post("/user/", json={"name": name})

    assert response.status_code == 201
    assert response.json["id"] is not None
    assert response.json["name"] == name.strip()


@pytest.mark.parametrize(
    "payload",
    [{}, {"name": ""}, {"name": "   "}, {"name": None}, {"name": 42}],
)
def test_create_user_rejects_invalid_name(session, monkeypatch, payload):
    client = configure_api(session, monkeypatch)

    response = client.post("/user/", json=payload)

    assert response.status_code == 400
    assert response.json == {"error": "Name cannot be empty"}


def test_list_users_returns_empty_list(session, monkeypatch):
    client = configure_api(session, monkeypatch)

    response = client.get("/user/")

    assert response.status_code == 200
    assert response.json == []


def test_list_users_returns_users(session, monkeypatch):
    first = user_service.create_user(session, "Ania")
    second = user_service.create_user(session, "Tomek")
    expected = [
        {"id": first.id, "name": "Ania"},
        {"id": second.id, "name": "Tomek"},
    ]
    client = configure_api(session, monkeypatch)

    response = client.get("/user/")

    assert response.status_code == 200
    assert response.json == expected


@pytest.mark.parametrize("method", ["put", "patch"])
def test_update_user_success(session, monkeypatch, method):
    user = user_service.create_user(session, "Ania")
    user_id = user.id
    client = configure_api(session, monkeypatch)

    response = getattr(client, method)(f"/user/{user_id}", json={"name": "Tomek"})

    assert response.status_code == 200
    assert response.json == {"id": user_id, "name": "Tomek"}


@pytest.mark.parametrize(
    "payload",
    [{}, {"name": ""}, {"name": "   "}, {"name": None}, {"name": 42}],
)
def test_update_user_rejects_invalid_name(session, monkeypatch, payload):
    user = user_service.create_user(session, "Ania")
    user_id = user.id
    client = configure_api(session, monkeypatch)

    response = client.put(f"/user/{user_id}", json=payload)

    assert response.status_code == 400
    assert response.json == {"error": "Name cannot be empty"}


def test_update_user_rejects_unknown_user(session, monkeypatch):
    client = configure_api(session, monkeypatch)

    response = client.put("/user/999", json={"name": "Tomek"})

    assert response.status_code == 400
    assert response.json == {"error": "User does not exist"}


def test_delete_user_success(session, monkeypatch):
    user = user_service.create_user(session, "Ania")
    user_id = user.id
    client = configure_api(session, monkeypatch)

    response = client.delete(f"/user/{user_id}")

    assert response.status_code == 200
    assert response.json == {"message": "User deleted successfully"}
    assert client.get("/user/").json == []


def test_delete_user_rejects_unknown_user(session, monkeypatch):
    client = configure_api(session, monkeypatch)

    response = client.delete("/user/999")

    assert response.status_code == 400
    assert response.json == {"error": "User does not exist"}


def test_delete_user_rejects_user_with_reservations(session, monkeypatch):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    user_id = user.id
    reservation_service.create_reservation(
        session,
        user_id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )
    client = configure_api(session, monkeypatch)

    response = client.delete(f"/user/{user_id}")

    assert response.status_code == 400
    assert response.json == {
        "error": "Cannot delete user with existing reservations."
    }


@pytest.mark.parametrize("name", ["Room 67", " Room 67 "])
def test_create_resource_success(session, monkeypatch, name):
    client = configure_api(session, monkeypatch)

    response = client.post("/resource/", json={"name": name})

    assert response.status_code == 201
    assert response.json["id"] is not None
    assert response.json["name"] == name.strip()


@pytest.mark.parametrize(
    "payload",
    [{}, {"name": ""}, {"name": "   "}, {"name": None}, {"name": 42}],
)
def test_create_resource_rejects_invalid_name(session, monkeypatch, payload):
    client = configure_api(session, monkeypatch)

    response = client.post("/resource/", json=payload)

    assert response.status_code == 400
    assert response.json == {"error": "Name cannot be empty"}


def test_list_resources_returns_empty_list(session, monkeypatch):
    client = configure_api(session, monkeypatch)

    response = client.get("/resource/")

    assert response.status_code == 200
    assert response.json == []


def test_list_resources_returns_resources(session, monkeypatch):
    first = resource_service.create_resource(session, "Room 67")
    second = resource_service.create_resource(session, "Room 68")
    expected = [
        {"id": first.id, "name": "Room 67"},
        {"id": second.id, "name": "Room 68"},
    ]
    client = configure_api(session, monkeypatch)

    response = client.get("/resource/")

    assert response.status_code == 200
    assert response.json == expected


@pytest.mark.parametrize("method", ["put", "patch"])
def test_update_resource_success(session, monkeypatch, method):
    resource = resource_service.create_resource(session, "Room 67")
    resource_id = resource.id
    client = configure_api(session, monkeypatch)

    response = getattr(client, method)(
        f"/resource/{resource_id}", json={"name": "Room 68"}
    )

    assert response.status_code == 200
    assert response.json == {"id": resource_id, "name": "Room 68"}


@pytest.mark.parametrize(
    "payload",
    [{}, {"name": ""}, {"name": "   "}, {"name": None}, {"name": 42}],
)
def test_update_resource_rejects_invalid_name(session, monkeypatch, payload):
    resource = resource_service.create_resource(session, "Room 67")
    resource_id = resource.id
    client = configure_api(session, monkeypatch)

    response = client.put(f"/resource/{resource_id}", json=payload)

    assert response.status_code == 400
    assert response.json == {"error": "Name cannot be empty"}


def test_update_resource_rejects_unknown_resource(session, monkeypatch):
    client = configure_api(session, monkeypatch)

    response = client.put("/resource/999", json={"name": "Room 68"})

    assert response.status_code == 400
    assert response.json == {"error": "Resource does not exist"}


def test_delete_resource_success(session, monkeypatch):
    resource = resource_service.create_resource(session, "Room 67")
    resource_id = resource.id
    client = configure_api(session, monkeypatch)

    response = client.delete("/resource/", json={"id": resource_id})

    assert response.status_code == 200
    assert response.json == {"message": "Resource deleted successfully"}
    assert client.get("/resource/").json == []


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "Resource id is required"),
        ({"id": 999}, "Resource does not exist"),
    ],
)
def test_delete_resource_rejects_missing_or_unknown_resource(
    session, monkeypatch, payload, message):
    client = configure_api(session, monkeypatch)

    response = client.delete("/resource/", json=payload)

    assert response.status_code == 400
    assert response.json == {"error": message}


def test_delete_resource_rejects_resource_with_reservations(session, monkeypatch):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    resource_id = resource.id
    reservation_service.create_reservation(
        session,
        user.id,
        resource_id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )
    client = configure_api(session, monkeypatch)

    response = client.delete("/resource/", json={"id": resource_id})

    assert response.status_code == 400
    assert response.json == {
        "error": "Cannot delete resource with existing reservations."
    }