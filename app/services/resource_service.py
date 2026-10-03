from app.models import Resource


def create_resource(session, name):
    resource = Resource(name=name)
    session.add(resource)
    session.commit()
    return resource

def delete_resource(session, resource_id):
    resource = session.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise ValueError("Resource does not exist")
    session.delete(resource)
    session.commit()

def list_resources(session):
    return session.query(Resource).all()