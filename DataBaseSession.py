from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DataBaseSession:
    user_name = "root"
    password = "258258"
    scheme = "jsp"
    engine = create_engine(f'mysql+pymysql://{user_name}:{password}@localhost/{scheme}', convert_unicode=True,
                           connect_args=dict(use_unicode=True), pool_size=5)
    Session = sessionmaker(bind=engine)
    session = Session()
