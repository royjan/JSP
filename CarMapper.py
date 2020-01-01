from dictalchemy import make_class_dictable
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from DataBaseSession import DataBaseSession
from Log import logger

Base = declarative_base()
make_class_dictable(Base)


class CarMapper(Base):
    __tablename__ = 'car_mapping'

    vin = Column("vin", String(32), primary_key=True, quote=True)
    license_plate = Column("num_vehicle", String(32), quote=True)
    car_name = Column("car_name", String(255), quote=True)

    db_session = DataBaseSession.session

    def __init__(self, vin: str, license_plate: str = None):
        self.vin = vin
        self.license_plate = license_plate

    def __eq__(self, other):
        return self.vin == other.vin and self.license_plate == other.license_plate

    @classmethod
    def create_db(cls):
        cls.__table__.create(DataBaseSession.engine)

    @classmethod
    def get_all_cars_vin(cls):
        lst = cls.db_session.query(cls.vin).all()
        return {item.vin for item in lst}

    @classmethod
    def get_all_cars_plate(cls):
        lst = cls.db_session.query(cls.license_plate).all()
        return {item.license_plate for item in lst}

    def add_to_db_result(self):
        db_car = None
        if self.vin:                                                            # try to get car by vin
            db_car = CarMapper.get_car_by_vin(self.vin)
            if not self.license_plate and db_car:                               # if not has license plate
                self.license_plate = db_car.license_plate
                return
        elif self.license_plate and not self.vin:                               # try to get car by license plate
            db_car = CarMapper.get_car_by_license_plate(self.license_plate)
            if db_car:
                self.vin = db_car.vin                                           # if exists -> update object
                return
        if db_car:                                                              # if exists but the same
            if self == db_car:
                return
            if self.vin and self.license_plate:                                 # if needs to overwrite
                if self.license_plate != db_car.license_plate:
                    CarMapper.update_car_by_license_plate(self, "roy")
        else:
            CarMapper.add_if_needed(self)                                       # a new one

    @classmethod
    def get_car_by_vin(cls, vin: str):
        return cls.db_session.query(cls).filter(cls.vin == vin).first()

    @classmethod
    def get_car_by_license_plate(cls, license_plate: str):
        return cls.db_session.query(cls).filter(cls.license_plate == license_plate).first()

    @classmethod
    def name_car_by_vin(cls, obj, name: str):
        cls.db_session.query(cls).filter(cls.vin == obj.vin).update({cls.car_name: name})
        cls.db_session.commit()

    @classmethod
    def update_car_by_license_plate(cls, obj, user: str):
        logger.warning(f"Overwrite an existing VIN {obj.vin} license plate to {obj.license_plate} by {user}")
        cls.db_session.query(cls).filter(cls.vin == obj.vin).update({cls.license_plate: obj.license_plate})
        cls.db_session.commit()

    @classmethod
    def add_car(cls, obj):
        cls.db_session.add(obj)
        cls.db_session.commit()

    @classmethod
    def add_if_needed(cls, obj):
        result = cls.get_car_by_vin(obj.vin)
        if not result:
            cls.add_car(obj)

    def check_same_license_plate(self, db_obj) -> bool:
        return self.license_plate == db_obj.license_plate

    def check_same_vin(self, db_obj) -> bool:
        return self.vin == db_obj.vin

    def check_same_car(self, db_car):
        return self.check_same_license_plate(db_car) and self.check_same_vin(db_car)


if __name__ == '__main__':
    CarMapper.create_db()
