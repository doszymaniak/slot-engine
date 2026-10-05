from app.models import Resource, Reservation


def create_resource(session, name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Name cannot be empty")
    resource = Resource(name=name)

    try:
        session.add(resource)
        session.commit()
        session.refresh(resource)
    except Exception:
        session.rollback()
        raise
    
    return resource


def delete_resource(session, resource_id):
    resource = session.query(Resource).filter(Resource.id == resource_id).first()
    if resource is None:
        raise ValueError("Resource does not exist")
    reservation = session.query(Reservation).filter(Reservation.resource_id == resource_id).first()
    if reservation:
        raise ValueError("Cannot delete resource with existing reservations.")
    try:
        session.delete(resource)
        session.commit()
    except Exception:
        session.rollback()
        raise


def list_resources(session):
    return session.query(Resource).all()


def update_resource(session, resource_id, name):
    resource = session.query(Resource).filter(Resource.id == resource_id).first()
    if resource is None:
        raise ValueError("Resource does not exist")

    name = (name or "").strip()
    if not name:
        raise ValueError("Name cannot be empty")
    resource.name = name
    
    try:
        session.commit()
        session.refresh(resource)
    except Exception:
        session.rollback()
        raise
    
    return resource