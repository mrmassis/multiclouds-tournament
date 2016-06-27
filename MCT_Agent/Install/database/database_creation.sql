SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `mct` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `mct` ;

-- -----------------------------------------------------
-- Table `mct`.`REQUEST`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`REQUEST` ;

CREATE TABLE IF NOT EXISTS `mct`.`REQUEST` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `request_id` VARCHAR(45) NOT NULL,
  `message` VARCHAR(200) NOT NULL,
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


-- -----------------------------------------------------
-- Table `mct`.`INSTANCES`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`INSTANCES` ;

CREATE TABLE IF NOT EXISTS `mct`.`INSTANCES` (
  `uuid`      VARCHAR(45) NOT NULL,
  `name`      VARCHAR(45) NULL,
  `vcpu`      INT NULL,
  `disk`      INT NULL,
  `memory`    INT NULL,
  `mct_state` VARCHAR(45) NULL,
  `pwr_state` INT NULL,
  PRIMARY KEY (`uuid`))
ENGINE = InnoDB
PACK_KEYS = DEFAULT;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

