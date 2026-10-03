from app.models import User

def create_user(session, name):
    user = User(name=name)
    session.add(user)
    session.commit()
    return user

def delete_user(session, user_id):
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User does not exist")
    session.delete(user)
    session.commit()

def list_users(session):
    return session.query(User).all()