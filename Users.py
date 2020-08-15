from dictalchemy import make_class_dictable
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from DataBaseSession import DataBaseSession

Base = declarative_base()
make_class_dictable(Base)


class Users(UserMixin, Base):
    __tablename__ = 'users'

    id = Column("id", Integer, autoincrement=True, primary_key=True, nullable=False)
    user_name = Column("user_name", String(32), quote=True)
    password = Column("password", String(32), quote=True)

    db_session = DataBaseSession.session

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    @classmethod
    def get_user(cls, user_name: str):
        from sqlalchemy import func
        return cls.db_session.query(Users).filter(func.lower(Users.user_name) == func.lower(user_name)).first()

    def is_verify(self, password: str):
        return self.password == password

    @classmethod
    def create_db(cls):
        cls.__table__.create(DataBaseSession.engine)

    @classmethod
    def get_user_by_id(cls, user_id):
        try:
            return cls.db_session.query(Users).filter(Users.id == user_id).first()
        except:
            cls.db_session.rollback()
            return cls.db_session.query(Users).filter(Users.id == user_id).first()


if __name__ == '__main__':
    Users.create_db()
