-- MySQL dump 10.13  Distrib 8.0.19, for osx10.14 (x86_64)
--
-- Host: 127.0.0.1    Database: world
-- ------------------------------------------------------
-- Server version	8.0.19-debug

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @old_autocommit=@@autocommit;

--
-- Current Database: `LinkedInScrape`
--

/*!40000 DROP DATABASE IF EXISTS `LinkedInScrape`*/;

DROP DATABASE IF EXISTS LinkedInScrape;
CREATE DATABASE LinkedInScrape DEFAULT CHARACTER SET utf8mb4;
USE LinkedInScrape;

DROP TABLE IF EXISTS `Job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Job` (
	`JobID` int NOT NULL AUTO_INCREMENT,
    `Name` VARCHAR(30) NOT NULL DEFAULT '',
    `Business` VARCHAR(30) NOT NULL DEFAULT '',
    `Location` VARCHAR(30) NOT NULL DEFAULT '',
	`Salary` int NOT NULL DEFAULT 0,
    `JobType` VARCHAR(30) NOT NULL DEFAULT '',
    `WorkType` varchar(15) NOT NULL DEFAULT '',
    `Duration` varchar(15) NOT NULL DEFAULT '',
    `URL` CHAR(10) NOT NULL, /* A unique identifier for the purposes of finding duplicates */
    primary key(`JobID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

set autocommit=0;

DROP TABLE IF EXISTS `Skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Skills` (
	`SkillID` int NOT NULL AUTO_INCREMENT,
    `Skill` varchar(50) NOT NULL,
    primary key(`SkillID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

set autocommit=0;

DROP TABLE IF EXISTS `SkillsLink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SkillsLink` (
	`JobID` int NOT NULL,
    `SkillID` int NOT NULL,
    key `JobID` (`JobID`),
    key `SkillID` (`SkillID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

GRANT ALL PRIVILEGES ON LinkedInScrape.* TO 'myuser'@'%';
