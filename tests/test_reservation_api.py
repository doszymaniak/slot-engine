from datetime import datetime
import pytest
from sqlalchemy.orm import sessionmaker
from app.api import routes
from app.services import reservation_service, resource_service, user_service
from app.api.routes import create_app


def configure_api_session(session, monkeypatch):
    monkeypatch.setattr(
        routes,
        "Session",
        sessionmaker(bind=session.get_bind()),
    )
    app = create_app()
    return app.test_client()


def create_api_entities(session, monkeypatch):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    user_id = user.id
    resource_id = resource.id
    client = configure_api_session(session, monkeypatch)
    return client, user_id, resource_id


def test_create_reservation_success(session, monkeypatch):
    client, user_id, resource_id = create_api_entities(session, monkeypatch)

    response = client.post(
        "/reservation/",
        json={
            "user_id": user_id,
            "resource_id": resource_id,
            "start": "2026-01-01T09:00:00",
            "end": "2026-01-01T10:00:00",
        },
    )

    assert response.status_code == 201
    assert response.json["id"] is not None
    assert response.json["user_id"] == user_id
    assert response.json["resource_id"] == resource_id
    assert response.json["start"] == "2026-01-01T09:00:00"
    assert response.json["end"] == "2026-01-01T10:00:00"


def test_create_overlapping_reservation_returns_bad_request(session, monkeypatch):
    client, user_id, resource_id = create_api_entities(session, monkeypatch)
    reservation_service.create_reservation(
        session,
        user_id,
        resource_id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )
    response = client.post(
        "/reservation/",
        json={
            "user_id": user_id,
            "resource_id": resource_id,
            "start": "2026-01-01T09:30:00",
            "end": "2026-01-01T10:30:00",
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "error": "Resource is not available for the given time slot"
    }


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "User id is required"),
        ({"user_id": 1}, "Resource id is required"),
        ({"user_id": 1, "resource_id": 1}, "Start date is required"),
        (
            {
                "user_id": 1,
                "resource_id": 1,
                "start": "2026-01-01T09:00:00",
            },
            "End date is required",
        ),
    ],
)
def test_create_reservation_rejects_missing_fields(session, monkeypatch, payload, message):
    client = configure_api_session(session, monkeypatch)

    response = client.post("/reservation/", json=payload)

    assert response.status_code == 400
    assert response.json == {"error": message}


def test_create_reservation_rejects_malformed_date(session, monkeypatch):
    client, user_id, resource_id = create_api_entities(session, monkeypatch)

    response = client.post(
        "/reservation/",
        json={
            "user_id": user_id,
            "resource_id": resource_id,
            "start": "not-a-date",
            "end": "2026-01-01T10:00:00",
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "error": "Start and end must use YYYY-MM-DDTHH:MM:SS format"
    }


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("2026-01-01T09:00:00", "2026-01-01T09:00:00"),
        ("2026-01-01T10:00:00", "2026-01-01T09:00:00"),
    ],
)
def test_create_reservation_rejects_invalid_time_range(
    session, monkeypatch, start, end):
    client, user_id, resource_id = create_api_entities(session, monkeypatch)

    response = client.post(
        "/reservation/",
        json={
            "user_id": user_id,
            "resource_id": resource_id,
            "start": start,
            "end": end,
        },
    )

    assert response.status_code == 400
    assert response.json == {"error": "Start time must be before end time"}


@pytest.mark.parametrize(
    ("missing_entity", "message"),
    [
        ("user", "User does not exist"),
        ("resource", "Resource does not exist"),
    ],
)
def test_create_reservation_rejects_unknown_entities(
    session, monkeypatch, missing_entity, message):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    user_id = user.id
    resource_id = resource.id
    if missing_entity == "user":
        user_id = 999
    else:
        resource_id = 999
    client = configure_api_session(session, monkeypatch)

    response = client.post(
        "/reservation/",
        json={
            "user_id": user_id,
            "resource_id": resource_id,
            "start": "2026-01-01T09:00:00",
            "end": "2026-01-01T10:00:00",
        },
    )

    assert response.status_code == 400
    assert response.json == {"error": message}


def test_list_reservations_returns_reservation(session, monkeypatch):
    client, user_id, resource_id = create_api_entities(session, monkeypatch)
    reservation = reservation_service.create_reservation(
        session,
        user_id,
        resource_id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )
    reservation_id = reservation.id

    response = client.get("/reservation/")

    assert response.status_code == 200
    assert response.json == [
        {
            "id": reservation_id,
            "user_id": user_id,
            "resource_id": resource_id,
            "start": "2026-01-01T09:00:00",
            "end": "2026-01-01T10:00:00",
        }
    ]


def test_update_reservation_success(session, monkeypatch):
    client, user_id, resource_id = create_api_entities(session, monkeypatch)
    reservation = reservation_service.create_reservation(
        session,
        user_id,
        resource_id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )
    reservation_id = reservation.id

    response = client.put(
        f"/reservation/{reservation_id}",
        json={"start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00"},
    )

    assert response.status_code == 200
    assert response.json == {
        "id": reservation_id,
        "user_id": user_id,
        "resource_id": resource_id,
        "start": "2026-01-01T10:00:00",
        "end": "2026-01-01T11:00:00",
    }


def test_update_reservation_rejects_overlapping_reservation(session, monkeypatch):
    client, user_id, resource_id = create_api_entities(session, monkeypatch)
    reservation = reservation_service.create_reservation(
        session,
        user_id,
        resource_id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )
    reservation_id = reservation.id
    reservation_service.create_reservation(
        session,
        user_id,
        resource_id,
        datetime(2026, 1, 1, 11, 0),
        datetime(2026, 1, 1, 12, 0),
    )

    response = client.put(
        f"/reservation/{reservation_id}",
        json={"start": "2026-01-01T11:30:00", "end": "2026-01-01T12:30:00"},
    )

    assert response.status_code == 400
    assert response.json == {
        "error": "Resource is not available for the given time slot"
    }


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("2026-01-01T10:00:00", "2026-01-01T10:00:00"),
        ("2026-01-01T11:00:00", "2026-01-01T10:00:00"),
    ],
)
def test_update_reservation_rejects_invalid_time_range(
    session, monkeypatch, start, end):
    client, user_id, resource_id = create_api_entities(session, monkeypatch)
    reservation = reservation_service.create_reservation(
        session,
        user_id,
        resource_id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )
    reservation_id = reservation.id

    response = client.put(
        f"/reservation/{reservation_id}",
        json={"start": start, "end": end},
    )

    assert response.status_code == 400
    assert response.json == {"error": "Start time must be before end time"}


def test_update_reservation_rejects_missing_reservation(session, monkeypatch):
    client = configure_api_session(session, monkeypatch)

    response = client.put(
        "/reservation/999",
        json={"start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00"},
    )

    assert response.status_code == 400
    assert response.json == {"error": "Reservation does not exist"}


def test_delete_reservation_success(session, monkeypatch):
    client, user_id, resource_id = create_api_entities(session, monkeypatch)
    reservation = reservation_service.create_reservation(
        session,
        user_id,
        resource_id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )
    reservation_id = reservation.id

    response = client.delete("/reservation/", json={"reservation_id": reservation_id})

    assert response.status_code == 200
    assert response.json == {"message": "Reservation deleted successfully"}
    assert client.get("/reservation/").json == []


def test_delete_reservation_rejects_missing_reservation(session, monkeypatch):
    client = configure_api_session(session, monkeypatch)

    response = client.delete(
        "/reservation/",
        json={"reservation_id": 999},
    )

    assert response.status_code == 400
    assert response.json == {"error": "Reservation does not exist"}