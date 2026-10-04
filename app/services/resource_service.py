from app.models import Resource, Reservation


def create_resource(session, name):
    resource = Resource(name=name)
    try:
        session.add(resource)
        session.commit()
        session.refresh(resource)
    except Exception as e:
        session.rollback()
        raise e
    
    return resource


def delete_resource(session, resource_id):
    resource = session.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise ValueError("Resource does not exist")
    reservation = session.query(Reservation).filter(Reservation.resource_id == resource_id).first()
    if reservation:
        raise ValueError("Cannot delete resource with existing reservations.")
    try:
        session.delete(resource)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def list_resources(session):
    return session.query(Resource).all()