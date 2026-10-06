import pytest
from datetime import datetime
from app.services import user_service, reservation_service, resource_service


def test_create_user_success(session):
    user = user_service.create_user(session, "Ania")

    assert user.id is not None
    assert user.name == "Ania"


def test_create_user_failure(session):
    with pytest.raises(ValueError, match="Name cannot be empty"):
        user_service.create_user(session, "")


def test_delete_user_success(session):
    user = user_service.create_user(session, "Ania")

    user_service.delete_user(session, user.id)

    assert session.query(user_service.User).filter_by(id=user.id).first() is None


def test_delete_user_failure_one(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    start_date = datetime(2026, 1, 1, 9, 0)
    end_date = datetime(2026, 1, 1, 10, 0)
    reservation = reservation_service.create_reservation(session, user.id, resource.id, start_date, end_date)

    with pytest.raises(ValueError, match="Cannot delete user with existing reservations."):
        user_service.delete_user(session, user.id)


def test_delete_user_failure_two(session):
    user = user_service.create_user(session, "Ania")
    user_service.delete_user(session, user.id)

    with pytest.raises(ValueError, match="User does not exist"):
        user_service.delete_user(session, user.id)


def test_update_user_success(session):
    user = user_service.create_user(session, "Ania")

    user_service.update_user(session, user.id, "Tomek")

    assert user.name == "Tomek"


def test_update_user_failure_one(session):
    user = user_service.create_user(session, "Ania")
    user_service.delete_user(session, user.id)

    with pytest.raises(ValueError, match="User does not exist"):
        user_service.update_user(session, user.id, "Tomek")


def test_update_user_failure_two(session):
    user = user_service.create_user(session, "Ania")

    with pytest.raises(ValueError, match="Name cannot be empty"):
        user_service.update_user(session, user.id, "")