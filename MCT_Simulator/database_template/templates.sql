SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `mct` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `mct` ;


-- ----------------------------------------------------------------------------
-- Table `mct`.`AVALIABLE_RESOURCES`
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `mct`.`PLAYER` ;

CREATE TABLE IF NOT EXISTS `mct`.`PLAYER` (
  `player_id`		VARCHAR(45) NOT NULL,
  `vcpus`		INT NULL DEFAULT 0,
  `vcpus_used`		INT NULL DEFAULT 0,
  `local_gb`		INT NULL DEFAULT 0,
  `local_gb_used`	INT NULL DEFAULT 0,
  `memory`		INT NULL DEFAULT 0, 
  `memory_mb_used`	INT NULL DEFAULT 0,
  `max_instance`	INT NULL DEFAULT 0,
  `instance_used`	INT NULL DEFAULT 0,
  `requests`		INT NULL DEFAULT 0,
  `accepted`		INT NULL DEFAULT 0,
  `fairness`		FLOAT NULL DEFAULT 0.0,
  PRIMARY KEY (`player_id`))
ENGINE = InnoDB
PACK_KEYS = DEFAULT;


-- ----------------------------------------------------------------------------
-- Table `mct`.STATE`
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `mct`.`STATE` ;

CREATE TABLE IF NOT EXISTS `mct`.`STATE` (
  `player_id`	VARCHAR(45) NOT NULL,
  `vm_id`	VARCHAR(45) NOT NULL,
  `vm_owner`	VARCHAR(45) NOT NULL,
  `vm_type`	VARCHAR(45) NOT NULL,
  `running`     VARCHAR(45) NOT NULL,
  PRIMARY KEY (`player_id`))
ENGINE = InnoDB
PACK_KEYS = DEFAULT;
--


-- -----------------------------------------------------
-- Table `mct`.`REQUEST`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`REQUEST` ;

CREATE TABLE IF NOT EXISTS `mct`.`REQUEST` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` VARCHAR(45) NOT NULL,
  `request_id` VARCHAR(45) NOT NULL,
  `message` LONGTEXT NOT NULL,
  `action` INT NULL,
  `timestamp_received` TIMESTAMP NULL,
  `timestamp_finished` TIMESTAMP NULL,
  `status` TINYINT(1) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
PACK_KEYS = DEFAULT;


-- -----------------------------------------------------
-- Table `mct`.`MAP`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`MAP` ;

CREATE TABLE IF NOT EXISTS `mct`.`MAP` (
  `uuid_src` VARCHAR(45) NOT NULL,
  `uuid_dst` VARCHAR(45) NOT NULL,
  `type_obj` VARCHAR(45) NOT NULL,
  `date`     TIMESTAMP NULL,
  PRIMARY KEY (`uuid_src`))
ENGINE = InnoDB
PACK_KEYS = DEFAULT;


-- ---------------------------------------------------------------------------
-- CREATE USER
-- ---------------------------------------------------------------------------
-- CREATE USER 'mct'@'localhost' IDENTIFIED BY 'password';
-- GRANT ALL PRIVILEGES ON mct.* TO 'mct'@'localhost';
-- FLUSH PRIVILEGES;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

