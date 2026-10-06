from datetime import datetime
import pytest
from app.services import reservation_service, resource_service, user_service


def test_create_resource_success(session):
    resource = resource_service.create_resource(session, "Room 67")

    assert resource.id is not None
    assert resource.name == "Room 67"


def test_create_resource_failure(session):
    with pytest.raises(ValueError, match="Name cannot be empty"):
        resource_service.create_resource(session, "")


def test_delete_resource_success(session):
    resource = resource_service.create_resource(session, "Room 67")

    resource_service.delete_resource(session, resource.id)

    assert session.query(resource_service.Resource).filter_by(id=resource.id).first() is None


def test_delete_resource_failure_one(session):
    with pytest.raises(ValueError, match="Resource does not exist"):
        resource_service.delete_resource(session, 999)


def test_delete_resource_failure_two(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    with pytest.raises(ValueError, match="Cannot delete resource with existing reservations."):
        resource_service.delete_resource(session, resource.id)


def test_list_resources_success(session):
    resource = resource_service.create_resource(session, "Room 67")

    resources = resource_service.list_resources(session)

    assert len(resources) == 1
    assert resources[0].id == resource.id


def test_update_resource_success(session):
    resource = resource_service.create_resource(session, "Room 67")

    resource_service.update_resource(session, resource.id, "Room 68")

    assert resource.name == "Room 68"


def test_update_resource_failure_one(session):
    with pytest.raises(ValueError, match="Resource does not exist"):
        resource_service.update_resource(session, 999, "Room 68")


def test_update_resource_failure_two(session):
    resource = resource_service.create_resource(session, "Room 67")

    with pytest.raises(ValueError, match="Name cannot be empty"):
        resource_service.update_resource(session, resource.id, "")
