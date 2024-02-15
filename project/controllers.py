from models import User, Car, Image, session


def add_object_to_database(obj: object):
    try:
        session.add(obj)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        return 'Error'


def get_all_cars():
    car = session.query(Car).all()
    data = []
    for i in car:
        data.append(
            {'model': i.model, 'colors': i.colors.split(', '), 'description': i.description, 'price': i.price})
    return data