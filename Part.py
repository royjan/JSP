from dictalchemy import make_class_dictable
from sqlalchemy import Column, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from DataBaseSession import DataBaseSession
import pandas as pd

Base = declarative_base()
make_class_dictable(Base)


class Part(Base):
    __tablename__ = 'parts'

    name = Column("name", String(255), primary_key=True, quote=True, nullable=False, unique=True)
    line = Column("line", String(255), quote=True)
    section = Column("section", String(255), quote=True)
    cat = Column("cat", String(255), quote=True)
    # bsquare = Column("bsquare", String(255), quote=True, default='Parts')
    original_part_name = Column("original_part_name", String(255), quote=True)

    db_session = DataBaseSession.session

    @classmethod
    def create_db(cls):
        cls.__table__.create(DataBaseSession.engine)

    def __init__(self, name):
        self.bsquare = 'Parts'
        self.name = name

    def to_dict(self):
        return self.__dict__

    @classmethod
    def get_part_by_name(cls, name: str) -> list:
        parts = []
        for part_name in name.split(","):
            part = cls.db_session.query(cls).filter(cls.name == part_name).first()
            part.bsquare = 'Parts'
            parts.append(part)
        return parts

    @classmethod
    def get_part_names(cls) -> set:
        # cls.db_session.rollback()
        lst = cls.db_session.query(cls.name).all()
        return {item.name for item in lst}

    @staticmethod
    def sort_parts_by_sections(parts):
        from collections import defaultdict
        dic = defaultdict(list)
        for part in parts:
            dic[part.cat, part.section, part.bsquare, part.line].append(part)
        return dic


if __name__ == '__main__':
    # Part.create_db()
    df = pd.read_csv('db2.csv', encoding='utf8')
    df = df.drop_duplicates(subset=['name'])
    for i in range(len(df)):
        try:
            df.iloc[i:i + 1].to_sql(name="parts", if_exists='append', con=DataBaseSession.engine, index=False)
        except IntegrityError:
            pass  # or any other action
