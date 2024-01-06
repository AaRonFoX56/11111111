from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from create_app import app

engine = create_engine('sqlite:///app.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return session.query(User).get(user_id)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


Base.metadata.create_all(engine)