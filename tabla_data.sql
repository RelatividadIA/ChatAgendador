-- Crear un nuevo esquema llamado `crud_guardias`
CREATE DATABASE IF NOT EXISTS `crud_clientes`;
USE `crud_clientes`;

-- Crear la tabla `clientes`
CREATE TABLE `clientes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `edad` int,
  `sexo` enum('masculino', 'femenino') NOT NULL,
  `teléfono` char(10) NOT NULL,
  `cedula` char(10) NOT NULL,
  `email` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

