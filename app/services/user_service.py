from app.models import User


def create_user(session, name):
    user = User(name=name)
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        session.rollback()
        raise e
    
    return user


def delete_user(session, user_id):
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User does not exist")
    try:
        session.delete(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        session.rollback()
        raise e


def list_users(session):
    return session.query(User).all()