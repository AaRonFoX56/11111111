from models import Session, User
from werkzeug.security import generate_password_hash


def create_admin():
    session = Session()

    name = 'admin'
    email = 'danillitvin531@gmail.com'
    password = generate_password_hash('admin')

    user = User(name=name, email=email, password=password)
    session.add(user)
    session.commit()
    session.close()


def check_admin():
    session = Session()

    admins = session.query(User).where(User.name == 'admin').all()
    print(admins)

create_admin()
check_admin()

admin_email = 'danillitvin531@gmail.com'