-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema ece1779a1
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema ece1779a1
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ece1779a1` DEFAULT CHARACTER SET utf8 ;
USE `ece1779a1` ;

-- -----------------------------------------------------
-- Table `ece1779a1`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ece1779a1`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `login` VARCHAR(16) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ece1779a1`.`images`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ece1779a1`.`images` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `key1` VARCHAR(255) NULL,
  `key2` VARCHAR(255) NULL,
  `key3` VARCHAR(255) NULL,
  `key4` VARCHAR(255) NULL,
  `users_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_images_users_idx` (`users_id` ASC),
  CONSTRAINT `fk_images_users`
    FOREIGN KEY (`users_id`)
    REFERENCES `ece1779a1`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;


CREATE USER 'ece1779A1admin'@'localhost' IDENTIFIED BY 'ece1779pass';

GRANT ALL PRIVILEGES ON ece1779a1 . * TO 'ece1779A1admin'@'localhost';