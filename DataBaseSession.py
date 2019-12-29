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


"""
CREATE STATEMENT:

CREATE DATABASE `jsp` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

CREATE TABLE `car_mapping` (
  `num_vehicle` text,
  `vin` char(255) NOT NULL,
  PRIMARY KEY (`vin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `part_mapping` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `part_name` varchar(256) NOT NULL,
  `car_name` varchar(256) DEFAULT NULL,
  `part_number` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `part_name` (`part_name`),
  CONSTRAINT `part_mapping_ibfk_1` FOREIGN KEY (`part_name`) REFERENCES `parts` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `parts` (
  `name` varchar(255) NOT NULL,
  `cat` text,
  `section` text,
  `line` text,
  `original_part_name` text,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


"""
