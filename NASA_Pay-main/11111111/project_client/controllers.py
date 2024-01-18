from models import User, session


def add_object_to_database(obj: object):
    try:
        session.add(obj)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        return 'err'


def get_user_by_id(user_id):
    return session.query(User).filter(User.id == user_id).first()


def change_subscribied_state_to_true(user_id):
    session.query(User).filter(User.id == user_id).update({'subscribied_state': True})
    session.commit()


