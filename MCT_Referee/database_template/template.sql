SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ALLOW_INVALID_DATES';

DROP DATABASE IF EXISTS `mct`;
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
-- Table `mct`.`PLAYER`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`PLAYER` ;

CREATE TABLE IF NOT EXISTS `mct`.`PLAYER` (
  `id`                 INT         NOT NULL AUTO_INCREMENT,
  `name`               VARCHAR(45) NOT NULL,
  `address`            VARCHAR(45) NOT NULL,
  `division`           INT             NULL,
  `score`              FLOAT           DEFAULT 0.0,
  `history`            INT             DEFAULT 0,
  `fairness`           FLOAT           DEFAULT 0.0,
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
  `suspend`            TIMESTAMP       NULL,
  `enabled`            INT             DEFAULT 0,
  `last_choice`        TIMESTAMP       DEFAULT '2018-01-01 00:00:00',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mct`.`VM`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`VM` ;

CREATE  TABLE IF NOT EXISTS `mct`.`VM` (
  `id`                 INT         NOT NULL AUTO_INCREMENT,
  `origin_add`         VARCHAR(45) NOT NULL,
  `origin_id`          VARCHAR(45) NOT NULL,
  `origin_name`        VARCHAR(45) NOT NULL,
  `destiny_add`        VARCHAR(45) NOT NULL,
  `destiny_name`       VARCHAR(45) NOT NULL,
  `destiny_id`         VARCHAR(45) NOT NULL,
  `status`             TINYINT(1)  NOT NULL,
  `vcpus`              INT         NOT NULL,
  `mem`                BIGINT      NOT NULL,
  `disk`               BIGINT      NOT NULL,
  `timestamp_received` TIMESTAMP       NULL,
  `timestamp_finished` TIMESTAMP       NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mct`.`STATUS`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`STATUS` ;

CREATE  TABLE IF NOT EXISTS `mct`.`STATUS` (
  `id`                 INT         NOT NULL AUTO_INCREMENT,
  `players`            INT         DEFAULT 0,
  `all_requests`       INT         DEFAULT 0,
  `accepts`            INT         DEFAULT 0,
  `rejects`            INT         DEFAULT 0,
  `fairness`           FLOAT       DEFAULT 0.0,
  `timestamp`          TIMESTAMP   NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mct`.`FIELDS`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mct`.`FIELDS` ;

CREATE  TABLE IF NOT EXISTS `mct`.`FIELDS` (
  `operation` INT NOT NULL,
  `fields` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`operation`))
ENGINE = InnoDB;

INSERT INTO FIELDS (operation, fields) VALUES (0, 'name mem image vcpus disk uuid');

-- ---------------------------------------------------------------------------
-- CREATE USER
-- ---------------------------------------------------------------------------
GRANT ALL PRIVILEGES ON mct.* TO 'mct'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON mct.* TO 'mct'@'%'         IDENTIFIED BY 'password' WITH GRANT OPTION;
FLUSH PRIVILEGES;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
