from dictalchemy import make_class_dictable
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from DataBaseSession import DataBaseSession
from Part import Part

Base = declarative_base()
make_class_dictable(Base)


class PartMapper(Base):
    __tablename__ = 'part_mapping'

    id = Column("id", Integer, autoincrement=True, primary_key=True, nullable=False)
    part_name = Column("part_name", String(255), ForeignKey(Part.name), quote=True, nullable=False)
    car_name = Column("car_name", String(255), quote=True)
    part_number = Column("part_number", String(255), quote=True)

    db_session = DataBaseSession.session

    def __init__(self, part_name: str, car_name: str, part_number: str):
        self.part_name = part_name
        self.car_name = car_name
        self.part_number = part_number

    @classmethod
    def get_obj_by_names(cls, obj):
        return cls.db_session.query(cls).filter(cls.part_name == obj.part_name, cls.car_name == obj.car_name).first()

    @classmethod
    def add_part(cls, obj):
        db_obj = cls.get_obj_by_names(obj)
        if not db_obj:
            cls.db_session.add(obj)
            cls.db_session.commit()

    @classmethod
    def create_db(cls):
        cls.__table__.create(DataBaseSession.engine)


if __name__ == '__main__':
    PartMapper.create_db()
