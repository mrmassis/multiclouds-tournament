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
  `player_id` VARCHAR(45) NOT NULL,
  `request_id` INT NOT NULL,
  `type` INT NOT NULL,
  `timestamp_received` TIMESTAMP NULL,
  `timestamp_finished` TIMESTAMP NULL,
  `status` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
PACK_KEYS = DEFAULT;


-- -----------------------------------------------------
-- Table `mct`.`PLAYER`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`PLAYER` ;

CREATE TABLE IF NOT EXISTS `mct`.`PLAYER` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL,
  `address` VARCHAR(45) NULL,
  `queue` VARCHAR(45) NULL,
  `exchange` VARCHAR(45) NULL,
  `route` VARCHAR(45) NULL,
  `division` INT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
