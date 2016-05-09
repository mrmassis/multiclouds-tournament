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
  `request_id` VARCHAR(45) NOT NULL,
  `action` INT NOT NULL,
  `timestamp_received` TIMESTAMP NULL,
  `timestamp_finished` TIMESTAMP NULL,
  `status` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
PACK_KEYS = DEFAULT;


-- -----------------------------------------------------
-- Table `mct`.`LAST_IDX`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`LAST_IDX` ;

CREATE TABLE IF NOT EXISTS `mct`.`LAST_IDX` (
  `division` INT NOT NULL,
  `idx`      INT NOT NULL,
  PRIMARY KEY (`division`))
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
  `division` INT NULL,
  `score` FLOAT NULL,
  `historic` INT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mct`.`RESOURCE`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`RESOURCE` ;

CREATE  TABLE IF NOT EXISTS `mct`.`RESOURCE` (
  `division` INT NOT NULL ,
  `vcpu` INT NOT NULL ,
  `memory` BIGINT NOT NULL ,
  `disk` BIGINT NOT NULL ,
  `vcpu_used` BIGINT NOT NULL ,
  `memory_used` BIGINT NOT NULL ,
  `disk_used` BIGINT NOT NULL ,
  PRIMARY KEY (`division`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mct`.`INSTANCE`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`INSTANCE` ;

CREATE  TABLE IF NOT EXISTS `mct`.`INSTANCE` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_id` VARCHAR(45) NOT NULL,
  `request_id` VARCHAR(45) NOT NULL,
  `timestamp_received` TIMESTAMP NULL,
  `timestamp_finished` TIMESTAMP NULL,
  `status` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;



--
--
--
-- DIVISAO 1: 300vcpus, 1 terabytes de memoria e 1 terabytes de disco;
-- DIVISAO 2: 200vcpus, 500 gigabytes de memoria e 500 gigabytes de disco;
-- DIVISAO 3: 100vcpus, 100 gigabytes de memoria e 100 gigabytes de disco;
INSERT INTO RESOURCE (division, vcpu, memory, disk, vcpu_used, memory_used, disk_used) VALUES (1, 300, 1048576, 1048576, 0, 0, 0);
INSERT INTO RESOURCE (division, vcpu, memory, disk, vcpu_used, memory_used, disk_used) VALUES (2, 200,  512000,  512000, 0, 0, 0);
INSERT INTO RESOURCE (division, vcpu, memory, disk, vcpu_used, memory_used, disk_used) VALUES (3, 100,  102400,  102400, 0, 0, 0);

-- PLAYER;
INSERT INTO PLAYER (name, address, division, score, historic) VALUES ('Player1', '10.0.0.30',  3,  0.0, 0);
INSERT INTO PLAYER (name, address, division, score, historic) VALUES ('Player2', '20.0.0.30',  3,  0.0, 0);

-- PLAYER;
INSERT INTO LAST_IDX (division, idx) VALUES (1, 1);
INSERT INTO LAST_IDX (division, idx) VALUES (2, 1);
INSERT INTO LAST_IDX (division, idx) VALUES (3, 1);

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
