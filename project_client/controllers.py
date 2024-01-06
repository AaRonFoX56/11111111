from models import User, session


def add_object_to_database(obj: object):
    try:
        session.add(obj)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        return 'err'
