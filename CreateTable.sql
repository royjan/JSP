CREATE DATABASE IF NOT EXISTS `jsp` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

CREATE TABLE IF NOT EXISTS `car_mapping` (
  `num_vehicle` text,
  `vin` char(255) NOT NULL,
  `car_name` text,
  PRIMARY KEY (`vin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `kits` (
  `name` varchar(32) NOT NULL,
  `parts` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `part_mapping` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `part_name` varchar(256) NOT NULL,
  `car_name` varchar(256) DEFAULT NULL,
  `part_number` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `part_name` (`part_name`),
  CONSTRAINT `part_mapping_ibfk_1` FOREIGN KEY (`part_name`) REFERENCES `parts` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `parts` (
  `name` varchar(255) NOT NULL,
  `cat` text,
  `section` text,
  `line` text,
  `original_part_name` text,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
