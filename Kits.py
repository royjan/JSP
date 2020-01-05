from dictalchemy import make_class_dictable
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

from DataBaseSession import DataBaseSession

Base = declarative_base()
make_class_dictable(Base)


class Kits(Base):
    __tablename__ = 'kits'

    name = Column("name", String(32), primary_key=True, quote=True)
    parts = Column("parts", String(255), quote=True)

    db_session = DataBaseSession.session

    @classmethod
    def create_db(cls):
        cls.__table__.create(DataBaseSession.engine)

    @classmethod
    def get_kits_names(cls) -> set:
        lst = cls.db_session.query(cls.name).all()
        return {item.name for item in lst}

    @property
    def get_parts(self):
        return ",".join(part.strip() for part in self.parts.split(","))

    @classmethod
    def get_parts_by_kit(cls, name: str):
        return cls.db_session.query(cls).filter(cls.name == name.strip()).first()


if __name__ == '__main__':
    Kits.create_db()
