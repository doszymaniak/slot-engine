from app.models import Resource


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
    try:
        session.delete(resource)
        session.commit()
        session.refresh(resource)
    except Exception as e:
        session.rollback()
        raise e


def list_resources(session):
    return session.query(Resource).all()