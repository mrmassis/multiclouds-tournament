SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ALLOW_INVALID_DATES';

DROP DATABASE IF EXISTS `mct`;
CREATE SCHEMA IF NOT EXISTS `mct` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `mct` ;


-- ----------------------------------------------------------------------------
-- Table `mct`.`AVALIABLE_RESOURCES`
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `mct`.`PLAYER` ;

CREATE TABLE IF NOT EXISTS `mct`.`PLAYER` (
  `name`               VARCHAR(45) NOT NULL,
  `address`            VARCHAR(45)     NULL,
  `division`           INT             NULL,
  `score`              FLOAT           DEFAULT 0.0,
  `history`            INT             DEFAULT 0,
  `accepts`            INT             DEFAULT 0,
  `rejects`            INT             DEFAULT 0,
  `running`            INT             DEFAULT 0,
  `finished`           INT             DEFAULT 0,
  `problem_del`        INT             DEFAULT 0,
  `vcpus`              INT             DEFAULT 0,
  `memory`             BIGINT(20)      DEFAULT 0,
  `local_gb`           BIGINT(20)      DEFAULT 0,
  `vcpus_used`         BIGINT(20)      DEFAULT 0,
  `memory_used`        BIGINT(20)      DEFAULT 0,
  `local_gb_used`      BIGINT(20)      DEFAULT 0,
  `max_instance`       INT             DEFAULT 0,
  `token`              VARCHAR(45)     NULL,
  PRIMARY KEY (`name`))
ENGINE = InnoDB;


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
GRANT ALL PRIVILEGES ON mct.* TO 'mct'@'localhost' IDENTIFIED BY 'password'; 
FLUSH PRIVILEGES;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

