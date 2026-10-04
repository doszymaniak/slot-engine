from app.models import Reservation, Resource, User


def create_reservation(session, user_id, resource_id, start, end):
    if start >= end:
        raise ValueError("Start time must be before end time")
    
    if not session.query(User).filter(User.id == user_id).first():
        raise ValueError("User does not exist")

    if not session.query(Resource).filter(Resource.id == resource_id).first():
        raise ValueError("Resource does not exist")
    
    if not is_available(session, resource_id, start, end):
        raise ValueError("Resource is not available for the given time slot")
    
    reservation = Reservation(user_id=user_id, resource_id=resource_id, start=start, end=end)
    try:
        session.add(reservation)
        session.commit()
        session.refresh(reservation)
    except Exception as e:
        session.rollback()
        raise e
    
    return reservation


def delete_reservation(session, reservation_id):
    reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise ValueError("Reservation does not exist")
    try:
        session.delete(reservation)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e 


def is_available(session,resource_id, start, end):
    overlapping = session.query(Reservation).filter(
        Reservation.resource_id == resource_id,
        Reservation.start < end,
        Reservation.end > start
    ).first()

    return overlapping is None


def list_reservations(session):
    return session.query(Reservation).all()