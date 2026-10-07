from datetime import datetime
import pytest
from app.services import reservation_service, resource_service, user_service


def test_create_reservation_success(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")

    reservation = reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    assert reservation.id is not None
    assert reservation.user_id == user.id
    assert reservation.resource_id == resource.id


def test_create_reservation_failure_one(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")

    user_service.delete_user(session, user.id)

    with pytest.raises(ValueError, match="User does not exist"):
        reservation_service.create_reservation(
            session,
            user.id,
            resource.id,
            datetime(2026, 1, 1, 9, 0),
            datetime(2026, 1, 1, 10, 0),
        )


def test_create_reservation_failure_two(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")

    resource_service.delete_resource(session, resource.id)

    with pytest.raises(ValueError, match="Resource does not exist"):
        reservation_service.create_reservation(
            session,
            user.id,
            resource.id,
            datetime(2026, 1, 1, 9, 0),
            datetime(2026, 1, 1, 10, 0),
        )


def test_create_reservation_failure_three(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")

    reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    with pytest.raises(ValueError, match="Resource is not available for the given time slot"):
        reservation_service.create_reservation(
            session,
            user.id,
            resource.id,
            datetime(2026, 1, 1, 9, 0),
            datetime(2026, 1, 1, 10, 0),
        )


def test_create_reservation_failure_four(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")

    with pytest.raises(ValueError, match="Start time must be before end time"):
        reservation_service.create_reservation(
            session,
            user.id,
            resource.id,
            datetime(2026, 1, 1, 10, 0),
            datetime(2026, 1, 1, 9, 0),
        )


def test_delete_reservation_success(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")

    reservation = reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    reservation_service.delete_reservation(session, reservation.id)

    assert session.query(reservation_service.Reservation).filter_by(id=reservation.id).first() is None


def test_delete_reservation_failure(session):
    with pytest.raises(ValueError, match="Reservation does not exist"):
        reservation_service.delete_reservation(session, 999)


def test_list_reservations_success(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    reservation = reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    reservations = reservation_service.list_reservations(session)

    assert len(reservations) == 1
    assert reservations[0].id == reservation.id


def test_update_reservation_success(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    reservation = reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    reservation_service.update_reservation(
        session,
        reservation.id,
        datetime(2026, 1, 1, 10, 0),
        datetime(2026, 1, 1, 11, 0),
    )

    assert reservation.start == datetime(2026, 1, 1, 10, 0)
    assert reservation.end == datetime(2026, 1, 1, 11, 0)


def test_update_reservation_failure_one(session):
    with pytest.raises(ValueError, match="Reservation does not exist"):
        reservation_service.update_reservation(
            session,
            999,
            datetime(2026, 1, 1, 10, 0),
            datetime(2026, 1, 1, 11, 0),
        )


def test_update_reservation_failure_two(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    reservation = reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    with pytest.raises(ValueError, match="Start time must be before end time"):
        reservation_service.update_reservation(
            session,
            reservation.id,
            datetime(2026, 1, 1, 11, 0),
            datetime(2026, 1, 1, 10, 0),
        )


def test_update_reservation_failure_three(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    first_reservation = reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )
    reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 11, 0),
        datetime(2026, 1, 1, 12, 0),
    )

    with pytest.raises(ValueError, match="Resource is not available for the given time slot"):
        reservation_service.update_reservation(
            session,
            first_reservation.id,
            datetime(2026, 1, 1, 11, 30),
            datetime(2026, 1, 1, 12, 30),
        )


def test_reservation_partial_overlap_failure(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    with pytest.raises(ValueError, match="Resource is not available for the given time slot"):
        reservation_service.create_reservation(
            session,
            user.id,
            resource.id,
            datetime(2026, 1, 1, 9, 30),
            datetime(2026, 1, 1, 10, 30),
        )


def test_reservation_adjacent_slots_success(session):
    user = user_service.create_user(session, "Ania")
    resource = resource_service.create_resource(session, "Room 67")
    reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    reservation = reservation_service.create_reservation(
        session,
        user.id,
        resource.id,
        datetime(2026, 1, 1, 10, 0),
        datetime(2026, 1, 1, 11, 0),
    )

    assert reservation.id is not None


def test_reservation_same_time_different_resource_success(session):
    user = user_service.create_user(session, "Ania")
    first_resource = resource_service.create_resource(session, "Room 67")
    second_resource = resource_service.create_resource(session, "Room 68")
    reservation_service.create_reservation(
        session,
        user.id,
        first_resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    reservation = reservation_service.create_reservation(
        session,
        user.id,
        second_resource.id,
        datetime(2026, 1, 1, 9, 0),
        datetime(2026, 1, 1, 10, 0),
    )

    assert reservation.id is not None
    assert reservation.resource_id == second_resource.id