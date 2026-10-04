from app.models import User, Reservation


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
    reservation = session.query(Reservation).filter(Reservation.user_id == user_id).first()
    if reservation:
        raise ValueError("Cannot delete user with existing reservations.")
    try:
        session.delete(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def list_users(session):
    return session.query(User).all()