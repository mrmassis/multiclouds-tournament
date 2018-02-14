-- MySQL dump 10.14  Distrib 5.5.58-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: mct
-- ------------------------------------------------------
-- Server version	5.5.58-MariaDB-1ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `FIELDS`
--

DROP TABLE IF EXISTS `FIELDS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `FIELDS` (
  `operation` int(11) NOT NULL,
  `fields` varchar(45) NOT NULL,
  PRIMARY KEY (`operation`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FIELDS`
--

LOCK TABLES `FIELDS` WRITE;
/*!40000 ALTER TABLE `FIELDS` DISABLE KEYS */;
INSERT INTO `FIELDS` VALUES (0,'name mem image vcpus disk uuid');
/*!40000 ALTER TABLE `FIELDS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PLAYER`
--

DROP TABLE IF EXISTS `PLAYER`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PLAYER` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `address` varchar(45) NOT NULL,
  `division` int(11) DEFAULT NULL,
  `score` float DEFAULT '0',
  `history` int(11) DEFAULT '0',
  `fairness` float DEFAULT '0',
  `accepts` int(11) DEFAULT '0',
  `rejects` int(11) DEFAULT '0',
  `running` int(11) DEFAULT '0',
  `finished` int(11) DEFAULT '0',
  `problem_del` int(11) DEFAULT '0',
  `vcpus` int(11) DEFAULT '0',
  `memory` bigint(20) DEFAULT '0',
  `local_gb` bigint(20) DEFAULT '0',
  `vcpus_used` bigint(20) DEFAULT '0',
  `memory_used` bigint(20) DEFAULT '0',
  `local_gb_used` bigint(20) DEFAULT '0',
  `max_instance` int(11) DEFAULT '0',
  `token` varchar(45) DEFAULT NULL,
  `suspend` timestamp NULL DEFAULT NULL,
  `enabled` int(11) DEFAULT '0',
  `last_choice` timestamp NOT NULL DEFAULT '2018-01-01 02:00:00',
  `playoff` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PLAYER`
--

LOCK TABLES `PLAYER` WRITE;
/*!40000 ALTER TABLE `PLAYER` DISABLE KEYS */;
INSERT INTO `PLAYER` VALUES (1,'playerVirtual1','192.168.0.200',4,-3,0,1,0,3,0,0,0,1023,1047552,10230,0,0,0,99,'71b939fb415ad4adb82aaf80156114e89cd3c4e9',NULL,0,'2018-02-12 14:02:47',1),(2,'playerVirtual11','192.168.0.200',3,3.32,3,0,4,0,4,0,0,1023,1047552,10230,5,7168,62,99,'718cfeb906ec03dbac4702a47196172ec5aaa0f9',NULL,1,'2018-02-12 14:10:15',0),(3,'playerVirtual4','192.168.0.200',3,2.66,3,1,4,0,4,0,0,1023,1047552,10230,5,7168,62,99,'cffca23c0f4c3901766e731358ac3a85e71a1547',NULL,1,'2018-02-12 14:10:31',0),(4,'playerVirtual8','192.168.0.200',3,2.66,3,1,4,0,4,0,0,1023,1047552,10230,4,3584,23,99,'a24bca0b87e2df710203c565b2fe714dfa983fd2',NULL,1,'2018-02-12 14:10:42',0),(5,'playerVirtual2','192.168.0.200',3,3.98,3,1,4,0,4,0,0,1023,1047552,10230,6,12288,120,99,'117e2f444de85ed8aa2e65858061e83fa43f2686',NULL,1,'2018-02-12 14:11:07',0),(6,'playerVirtual13','192.168.0.200',2,4.65,3,1,4,0,4,0,0,1023,1047552,10230,5,5632,43,99,'5d82f2ae0b3c7833a1ef69221802cbb4c2151a74',NULL,1,'2018-02-12 14:11:12',0),(7,'playerVirtual3','192.168.0.200',2,4.65,3,1,3,0,3,0,0,1023,1047552,10230,4,5120,42,99,'439f38dea4cb4c0caf911364e52411e82110071c',NULL,1,'2018-02-12 14:03:16',0),(8,'playerVirtual6','192.168.0.200',3,3.98,3,1,4,0,4,0,0,1023,1047552,10230,6,12288,120,99,'5699ca79ceca2c9098c784020b31094733f9765c',NULL,1,'2018-02-12 14:10:55',0),(9,'playerVirtual15','192.168.0.200',3,1.99,3,1,4,0,4,0,0,1023,1047552,10230,5,10240,100,99,'26c4f2dfa7e8a7233a00275911607db677647db2',NULL,1,'2018-02-12 14:11:37',0),(10,'playerVirtual17','192.168.0.200',3,1.33,3,1,4,0,4,0,0,1023,1047552,10230,4,5120,42,99,'94c3706cde092ebe20d546d140ab0ae16ec04c8d',NULL,1,'2018-02-12 14:11:15',0),(11,'playerVirtual19','192.168.0.200',3,1.33,3,1,4,0,4,0,0,1023,1047552,10230,4,6656,61,99,'2e790136e4b70b5ddac26e056ad903a201194630',NULL,1,'2018-02-12 14:11:29',0),(12,'playerVirtual5','192.168.0.200',3,2.66,3,1,4,0,4,0,0,1023,1047552,10230,4,3584,23,99,'3da3f87e6f3bce6df079c5232f23381e8bd26538',NULL,1,'2018-02-12 14:11:40',0),(13,'playerVirtual9','192.168.0.200',3,1.99,3,1,4,0,4,0,0,1023,1047552,10230,5,10240,100,99,'0517c4c1b8c0dfa6a6d9323b7faf6edce612f4a6',NULL,1,'2018-02-12 14:12:04',0),(14,'playerVirtual7','192.168.0.200',3,1.33,3,1,4,0,4,0,0,1023,1047552,10230,4,6656,61,99,'501ef2960cc48140ff61fe21b20e5115e877d1d2',NULL,1,'2018-02-12 14:11:53',0),(15,'playerVirtual14','192.168.0.200',3,3.32,3,1,4,0,3,1,0,1023,1047552,10230,4,8192,80,99,'58f196cddcc11d8afd99bb84e9054c40d74a55fd',NULL,1,'2018-02-12 14:12:11',0),(16,'playerVirtual12','192.168.0.200',3,2.66,3,1,4,0,3,1,0,1023,1047552,10230,3,4608,41,99,'f009007e641a426f259ab1599e56f0d89242a8d8',NULL,1,'2018-02-12 14:12:03',0),(17,'playerVirtual0','192.168.0.200',4,-2,0,1,0,2,0,0,0,1023,1047552,10230,0,0,0,99,'ec8f181eaad59e8a68d906c68c344866b369a1e3',NULL,0,'2018-02-12 14:00:41',1),(18,'playerVirtual16','192.168.0.200',3,1.33,3,0.333333,3,0,3,0,0,1023,1047552,10230,3,4608,41,99,'e38a4d7db4ebaea5eff8347b91835ac87f2372c7',NULL,1,'2018-02-12 14:05:29',0),(19,'playerVirtual18','192.168.0.200',3,1.99,3,1,3,0,2,1,0,1023,1047552,10230,3,6144,60,99,'3459bcf3c4e17353c6f87a4981661a684d2f487f',NULL,1,'2018-02-12 14:05:43',0),(20,'playerVirtual10','192.168.0.200',3,0,3,1,3,0,3,0,0,1023,1047552,10230,3,4608,41,99,'782cd3571a6c119c42d359f0effbb07354bf2ad6',NULL,1,'2018-02-12 14:09:12',0);
/*!40000 ALTER TABLE `PLAYER` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `REQUEST`
--

DROP TABLE IF EXISTS `REQUEST`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `REQUEST` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `player_id` varchar(45) NOT NULL,
  `request_id` varchar(45) NOT NULL,
  `action` int(11) NOT NULL,
  `timestamp_received` timestamp NULL DEFAULT NULL,
  `timestamp_finished` timestamp NULL DEFAULT NULL,
  `status` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=241 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `REQUEST`
--

LOCK TABLES `REQUEST` WRITE;
/*!40000 ALTER TABLE `REQUEST` DISABLE KEYS */;
INSERT INTO `REQUEST` VALUES (1,'playerVirtual1','playerVirtual1_eeb5d5e034',4,'2018-02-12 13:55:03',NULL,0),(2,'playerVirtual11','playerVirtual11_0214f914b3',4,'2018-02-12 13:55:03',NULL,0),(3,'playerVirtual4','playerVirtual4_a0960280b7',4,'2018-02-12 13:55:03',NULL,0),(4,'playerVirtual8','playerVirtual8_5e8baf078f',4,'2018-02-12 13:55:03',NULL,0),(5,'playerVirtual2','playerVirtual2_0da4b550e3',4,'2018-02-12 13:55:03',NULL,0),(6,'playerVirtual13','playerVirtual13_01ef430e12',4,'2018-02-12 13:55:04',NULL,0),(7,'playerVirtual3','playerVirtual3_48acc80f7c',4,'2018-02-12 13:55:04',NULL,0),(8,'playerVirtual6','playerVirtual6_4d7f53ef34',4,'2018-02-12 13:55:04',NULL,0),(9,'playerVirtual15','playerVirtual15_1206bb0a50',4,'2018-02-12 13:55:04',NULL,0),(10,'playerVirtual17','playerVirtual17_e9a58b7a38',4,'2018-02-12 13:55:04',NULL,0),(11,'playerVirtual19','playerVirtual19_96c6ec5fda',4,'2018-02-12 13:55:05',NULL,0),(12,'playerVirtual5','playerVirtual5_5e1044be4c',4,'2018-02-12 13:55:05',NULL,0),(13,'playerVirtual9','playerVirtual9_35735e5f96',4,'2018-02-12 13:55:05',NULL,0),(14,'playerVirtual7','playerVirtual7_463fc51ac5',4,'2018-02-12 13:55:06',NULL,0),(15,'playerVirtual14','playerVirtual14_3ff536342e',4,'2018-02-12 13:55:06',NULL,0),(16,'playerVirtual12','playerVirtual12_ebb5243b77',4,'2018-02-12 13:55:06',NULL,0),(17,'playerVirtual0','playerVirtual0_376b49e49b',4,'2018-02-12 13:55:06',NULL,0),(18,'playerVirtual16','playerVirtual16_99da5628e5',4,'2018-02-12 13:55:06',NULL,0),(19,'playerVirtual18','playerVirtual18_4abfd1ea98',4,'2018-02-12 13:55:07',NULL,0),(20,'playerVirtual10','playerVirtual10_e9b87007ce',4,'2018-02-12 13:55:07',NULL,0),(21,'playerVirtual1','playerVirtual1_450512000',0,'2018-02-12 13:56:04',NULL,0),(22,'playerVirtual1','playerVirtual1_450512000',0,'2018-02-12 13:56:04',NULL,0),(23,'playerVirtual11','playerVirtual11_1438244924',0,'2018-02-12 13:56:06',NULL,0),(24,'playerVirtual11','playerVirtual11_1438244924',0,'2018-02-12 13:56:06',NULL,0),(25,'playerVirtual4','playerVirtual4_640692267',0,'2018-02-12 13:56:09',NULL,0),(26,'playerVirtual4','playerVirtual4_640692267',0,'2018-02-12 13:56:09',NULL,0),(27,'playerVirtual8','playerVirtual8_2381571381',0,'2018-02-12 13:56:10',NULL,0),(28,'playerVirtual8','playerVirtual8_2381571381',0,'2018-02-12 13:56:11',NULL,0),(29,'playerVirtual2','playerVirtual2_5297461910',0,'2018-02-12 13:56:11',NULL,0),(30,'playerVirtual2','playerVirtual2_5297461910',0,'2018-02-12 13:56:12',NULL,0),(31,'playerVirtual13','playerVirtual13_2790332778',0,'2018-02-12 13:56:14',NULL,0),(32,'playerVirtual13','playerVirtual13_2790332778',0,'2018-02-12 13:56:15',NULL,0),(33,'playerVirtual3','playerVirtual3_369721705',0,'2018-02-12 13:56:16',NULL,0),(34,'playerVirtual6','playerVirtual6_317469422',0,'2018-02-12 13:56:16',NULL,0),(35,'playerVirtual3','playerVirtual3_369721705',0,'2018-02-12 13:56:16',NULL,0),(36,'playerVirtual15','playerVirtual15_6955737',0,'2018-02-12 13:56:16',NULL,0),(37,'playerVirtual6','playerVirtual6_317469422',0,'2018-02-12 13:56:16',NULL,0),(38,'playerVirtual15','playerVirtual15_6955737',0,'2018-02-12 13:56:17',NULL,0),(39,'playerVirtual17','playerVirtual17_257338104',0,'2018-02-12 13:56:17',NULL,0),(40,'playerVirtual19','playerVirtual19_3584940347',0,'2018-02-12 13:56:17',NULL,0),(41,'playerVirtual17','playerVirtual17_257338104',0,'2018-02-12 13:56:17',NULL,0),(42,'playerVirtual5','playerVirtual5_2433236783',0,'2018-02-12 13:56:18',NULL,0),(43,'playerVirtual19','playerVirtual19_3584940347',0,'2018-02-12 13:56:18',NULL,0),(44,'playerVirtual5','playerVirtual5_2433236783',0,'2018-02-12 13:56:18',NULL,0),(45,'playerVirtual9','playerVirtual9_3338579772',0,'2018-02-12 13:56:19',NULL,0),(46,'playerVirtual7','playerVirtual7_257407216',0,'2018-02-12 13:56:19',NULL,0),(47,'playerVirtual9','playerVirtual9_3338579772',0,'2018-02-12 13:56:19',NULL,0),(48,'playerVirtual7','playerVirtual7_257407216',0,'2018-02-12 13:56:19',NULL,0),(49,'playerVirtual14','playerVirtual14_182859403',0,'2018-02-12 13:56:26',NULL,0),(50,'playerVirtual14','playerVirtual14_182859403',0,'2018-02-12 13:56:27',NULL,0),(51,'playerVirtual12','playerVirtual12_2359368952',0,'2018-02-12 13:56:30',NULL,0),(52,'playerVirtual12','playerVirtual12_2359368952',0,'2018-02-12 13:56:30',NULL,0),(53,'playerVirtual0','playerVirtual0_16917741',0,'2018-02-12 13:56:33',NULL,0),(54,'playerVirtual0','playerVirtual0_16917741',0,'2018-02-12 13:56:33',NULL,0),(55,'playerVirtual16','playerVirtual16_2545640208',0,'2018-02-12 13:56:42',NULL,0),(56,'playerVirtual16','playerVirtual16_2545640208',0,'2018-02-12 13:56:42',NULL,0),(57,'playerVirtual18','playerVirtual18_908315',0,'2018-02-12 13:56:43',NULL,0),(58,'playerVirtual18','playerVirtual18_908315',0,'2018-02-12 13:56:44',NULL,0),(59,'playerVirtual10','playerVirtual10_539194189',0,'2018-02-12 13:56:51',NULL,0),(60,'playerVirtual10','playerVirtual10_539194189',0,'2018-02-12 13:56:52',NULL,0),(61,'playerVirtual1','playerVirtual1_d32dc61f01',3,'2018-02-12 13:57:04',NULL,0),(62,'playerVirtual11','playerVirtual11_26a0219393',3,'2018-02-12 13:57:06',NULL,0),(63,'playerVirtual4','playerVirtual4_eadc3a7a95',3,'2018-02-12 13:57:09',NULL,0),(64,'playerVirtual8','playerVirtual8_0e01c3d6bd',3,'2018-02-12 13:57:10',NULL,0),(65,'playerVirtual2','playerVirtual2_5342243ee7',3,'2018-02-12 13:57:11',NULL,0),(66,'playerVirtual13','playerVirtual13_2b5fe60f73',3,'2018-02-12 13:57:15',NULL,0),(67,'playerVirtual3','playerVirtual3_37fe221d18',3,'2018-02-12 13:57:16',NULL,0),(68,'playerVirtual6','playerVirtual6_ebc910cf28',3,'2018-02-12 13:57:16',NULL,0),(69,'playerVirtual15','playerVirtual15_3ad5ccae5c',3,'2018-02-12 13:57:16',NULL,0),(70,'playerVirtual17','playerVirtual17_4334f0178b',3,'2018-02-12 13:57:17',NULL,0),(71,'playerVirtual19','playerVirtual19_32dd26f53a',3,'2018-02-12 13:57:17',NULL,0),(72,'playerVirtual5','playerVirtual5_9274527aab',3,'2018-02-12 13:57:18',NULL,0),(73,'playerVirtual9','playerVirtual9_15c2ec94ba',3,'2018-02-12 13:57:19',NULL,0),(74,'playerVirtual7','playerVirtual7_f8847d8599',3,'2018-02-12 13:57:19',NULL,0),(75,'playerVirtual14','playerVirtual14_c6e92014ef',3,'2018-02-12 13:57:27',NULL,0),(76,'playerVirtual12','playerVirtual12_2a13c3450f',3,'2018-02-12 13:57:30',NULL,0),(77,'playerVirtual0','playerVirtual0_2ddb522348',3,'2018-02-12 13:57:33',NULL,0),(78,'playerVirtual16','playerVirtual16_c932c4fb42',3,'2018-02-12 13:57:42',NULL,0),(79,'playerVirtual18','playerVirtual18_9af8eb02a4',3,'2018-02-12 13:57:43',NULL,0),(80,'playerVirtual10','playerVirtual10_0916d96857',3,'2018-02-12 13:57:52',NULL,0),(81,'playerVirtual1','playerVirtual1_4820204870',0,'2018-02-12 13:59:29',NULL,0),(82,'playerVirtual1','playerVirtual1_4820204870',0,'2018-02-12 13:59:30',NULL,0),(83,'playerVirtual11','playerVirtual11_8058564',0,'2018-02-12 14:00:19',NULL,0),(84,'playerVirtual11','playerVirtual11_8058564',0,'2018-02-12 14:00:20',NULL,0),(85,'playerVirtual4','playerVirtual4_1429160667',0,'2018-02-12 14:00:21',NULL,0),(86,'playerVirtual4','playerVirtual4_1429160667',0,'2018-02-12 14:00:21',NULL,0),(87,'playerVirtual8','playerVirtual8_3338010893',0,'2018-02-12 14:00:22',NULL,0),(88,'playerVirtual8','playerVirtual8_3338010893',0,'2018-02-12 14:00:22',NULL,0),(89,'playerVirtual2','playerVirtual2_82730999',0,'2018-02-12 14:00:27',NULL,0),(90,'playerVirtual2','playerVirtual2_82730999',0,'2018-02-12 14:00:27',NULL,0),(91,'playerVirtual13','playerVirtual13_351652724',0,'2018-02-12 14:00:28',NULL,0),(92,'playerVirtual3','playerVirtual3_6571218',0,'2018-02-12 14:00:28',NULL,0),(93,'playerVirtual13','playerVirtual13_351652724',0,'2018-02-12 14:00:28',NULL,0),(94,'playerVirtual3','playerVirtual3_6571218',0,'2018-02-12 14:00:29',NULL,0),(95,'playerVirtual1','playerVirtual1_69bc120007',4,'2018-02-12 14:00:30',NULL,0),(96,'playerVirtual6','playerVirtual6_778566023',0,'2018-02-12 14:00:30',NULL,0),(97,'playerVirtual6','playerVirtual6_778566023',0,'2018-02-12 14:00:31',NULL,0),(98,'playerVirtual15','playerVirtual15_1436344784',0,'2018-02-12 14:00:34',NULL,0),(99,'playerVirtual15','playerVirtual15_1436344784',0,'2018-02-12 14:00:35',NULL,0),(100,'playerVirtual17','playerVirtual17_1339662',0,'2018-02-12 14:00:36',NULL,0),(101,'playerVirtual17','playerVirtual17_1339662',0,'2018-02-12 14:00:36',NULL,0),(102,'playerVirtual19','playerVirtual19_317497342',0,'2018-02-12 14:00:37',NULL,0),(103,'playerVirtual5','playerVirtual5_284794223',0,'2018-02-12 14:00:37',NULL,0),(104,'playerVirtual19','playerVirtual19_317497342',0,'2018-02-12 14:00:37',NULL,0),(105,'playerVirtual9','playerVirtual9_359920779',0,'2018-02-12 14:00:38',NULL,0),(106,'playerVirtual5','playerVirtual5_284794223',0,'2018-02-12 14:00:38',NULL,0),(107,'playerVirtual7','playerVirtual7_904011',0,'2018-02-12 14:00:38',NULL,0),(108,'playerVirtual9','playerVirtual9_359920779',0,'2018-02-12 14:00:38',NULL,0),(109,'playerVirtual7','playerVirtual7_904011',0,'2018-02-12 14:00:38',NULL,0),(110,'playerVirtual12','playerVirtual12_257338074',0,'2018-02-12 14:00:39',NULL,0),(111,'playerVirtual14','playerVirtual14_2904109077',0,'2018-02-12 14:00:39',NULL,0),(112,'playerVirtual0','playerVirtual0_905614',0,'2018-02-12 14:00:40',NULL,0),(113,'playerVirtual12','playerVirtual12_257338074',0,'2018-02-12 14:00:40',NULL,0),(114,'playerVirtual14','playerVirtual14_2904109077',0,'2018-02-12 14:00:40',NULL,0),(115,'playerVirtual0','playerVirtual0_905614',0,'2018-02-12 14:00:41',NULL,0),(116,'playerVirtual16','playerVirtual16_1093460',0,'2018-02-12 14:00:41',NULL,0),(117,'playerVirtual16','playerVirtual16_1093460',0,'2018-02-12 14:00:42',NULL,0),(118,'playerVirtual18','playerVirtual18_6569547',0,'2018-02-12 14:00:42',NULL,0),(119,'playerVirtual18','playerVirtual18_6569547',0,'2018-02-12 14:00:42',NULL,0),(120,'playerVirtual10','playerVirtual10_470485660',0,'2018-02-12 14:00:43',NULL,0),(121,'playerVirtual10','playerVirtual10_470485660',0,'2018-02-12 14:00:43',NULL,0),(122,'playerVirtual11','playerVirtual11_4e3d56448c',4,'2018-02-12 14:01:20',NULL,0),(123,'playerVirtual4','playerVirtual4_004e260c9a',4,'2018-02-12 14:01:21',NULL,0),(124,'playerVirtual8','playerVirtual8_30f17b2d5f',4,'2018-02-12 14:01:22',NULL,0),(125,'playerVirtual2','playerVirtual2_57a424cfa2',4,'2018-02-12 14:01:28',NULL,0),(126,'playerVirtual13','playerVirtual13_ebcf498372',4,'2018-02-12 14:01:31',NULL,0),(127,'playerVirtual3','playerVirtual3_76a6d5ce2a',4,'2018-02-12 14:01:31',NULL,0),(128,'playerVirtual6','playerVirtual6_aebaf43821',4,'2018-02-12 14:01:31',NULL,0),(129,'playerVirtual15','playerVirtual15_e2187f5c2d',4,'2018-02-12 14:01:35',NULL,0),(130,'playerVirtual17','playerVirtual17_5050f1c65b',4,'2018-02-12 14:01:36',NULL,0),(131,'playerVirtual19','playerVirtual19_cf11abe281',4,'2018-02-12 14:01:37',NULL,0),(132,'playerVirtual5','playerVirtual5_3080699be7',4,'2018-02-12 14:01:37',NULL,0),(133,'playerVirtual9','playerVirtual9_eb965dfea0',4,'2018-02-12 14:01:38',NULL,0),(134,'playerVirtual7','playerVirtual7_a64ccbc22b',4,'2018-02-12 14:01:38',NULL,0),(135,'playerVirtual12','playerVirtual12_32328522bb',4,'2018-02-12 14:01:39',NULL,0),(136,'playerVirtual14','playerVirtual14_f04cff26cc',4,'2018-02-12 14:01:40',NULL,0),(137,'playerVirtual0','playerVirtual0_e52c0b1ba9',4,'2018-02-12 14:01:40',NULL,0),(138,'playerVirtual16','playerVirtual16_427b112d66',4,'2018-02-12 14:01:41',NULL,0),(139,'playerVirtual18','playerVirtual18_d9ca764c2c',4,'2018-02-12 14:01:42',NULL,0),(140,'playerVirtual10','playerVirtual10_47f08deb03',4,'2018-02-12 14:01:43',NULL,0),(141,'playerVirtual1','playerVirtual1_30788568',0,'2018-02-12 14:02:45',NULL,0),(142,'playerVirtual1','playerVirtual1_30788568',0,'2018-02-12 14:02:45',NULL,0),(143,'playerVirtual11','playerVirtual11_5792765',0,'2018-02-12 14:02:47',NULL,0),(144,'playerVirtual11','playerVirtual11_5792765',0,'2018-02-12 14:02:47',NULL,0),(145,'playerVirtual4','playerVirtual4_38671842',0,'2018-02-12 14:02:57',NULL,0),(146,'playerVirtual4','playerVirtual4_38671842',0,'2018-02-12 14:02:58',NULL,0),(147,'playerVirtual8','playerVirtual8_400453824',0,'2018-02-12 14:02:58',NULL,0),(148,'playerVirtual8','playerVirtual8_400453824',0,'2018-02-12 14:02:59',NULL,0),(149,'playerVirtual2','playerVirtual2_4820318661',0,'2018-02-12 14:03:08',NULL,0),(150,'playerVirtual2','playerVirtual2_4820318661',0,'2018-02-12 14:03:08',NULL,0),(151,'playerVirtual13','playerVirtual13_4819935267',0,'2018-02-12 14:03:12',NULL,0),(152,'playerVirtual13','playerVirtual13_4819935267',0,'2018-02-12 14:03:12',NULL,0),(153,'playerVirtual3','playerVirtual3_4820217293',0,'2018-02-12 14:03:16',NULL,0),(154,'playerVirtual6','playerVirtual6_6264344062',0,'2018-02-12 14:03:16',NULL,0),(155,'playerVirtual3','playerVirtual3_4820217293',0,'2018-02-12 14:03:16',NULL,0),(156,'playerVirtual6','playerVirtual6_6264344062',0,'2018-02-12 14:03:17',NULL,0),(157,'playerVirtual15','playerVirtual15_2378747961',0,'2018-02-12 14:03:26',NULL,0),(158,'playerVirtual15','playerVirtual15_2378747961',0,'2018-02-12 14:03:26',NULL,0),(159,'playerVirtual17','playerVirtual17_5068098508',0,'2018-02-12 14:03:34',NULL,0),(160,'playerVirtual17','playerVirtual17_5068098508',0,'2018-02-12 14:03:37',NULL,0),(161,'playerVirtual11','playerVirtual11_96f34947a3',3,'2018-02-12 14:03:47',NULL,0),(162,'playerVirtual4','playerVirtual4_fccd944741',3,'2018-02-12 14:03:58',NULL,0),(163,'playerVirtual8','playerVirtual8_fe94ccb1a0',3,'2018-02-12 14:03:58',NULL,0),(164,'playerVirtual2','playerVirtual2_c91f3b2769',3,'2018-02-12 14:04:08',NULL,0),(165,'playerVirtual13','playerVirtual13_1b1c3e352c',3,'2018-02-12 14:04:12',NULL,0),(166,'playerVirtual3','playerVirtual3_7d31ab457f',3,'2018-02-12 14:04:16',NULL,0),(167,'playerVirtual6','playerVirtual6_c3fb3b517e',3,'2018-02-12 14:04:16',NULL,0),(168,'playerVirtual15','playerVirtual15_2577595b02',3,'2018-02-12 14:04:26',NULL,0),(169,'playerVirtual17','playerVirtual17_9cab74dc87',3,'2018-02-12 14:04:32',NULL,0),(170,'playerVirtual12','playerVirtual12_2359368952',1,'2018-02-12 14:04:42',NULL,0),(171,'playerVirtual12','playerVirtual12_df5e4edb40',3,'2018-02-12 14:04:42',NULL,0),(172,'playerVirtual12','playerVirtual12_2359368952',1,'2018-02-12 14:04:42',NULL,0),(173,'playerVirtual19','playerVirtual19_227443932',0,'2018-02-12 14:04:45',NULL,0),(174,'playerVirtual5','playerVirtual5_1095593',0,'2018-02-12 14:04:46',NULL,0),(175,'playerVirtual19','playerVirtual19_227443932',0,'2018-02-12 14:04:46',NULL,0),(176,'playerVirtual5','playerVirtual5_1095593',0,'2018-02-12 14:04:46',NULL,0),(177,'playerVirtual9','playerVirtual9_2148750930',0,'2018-02-12 14:04:51',NULL,0),(178,'playerVirtual9','playerVirtual9_2148750930',0,'2018-02-12 14:04:51',NULL,0),(179,'playerVirtual7','playerVirtual7_563574327',0,'2018-02-12 14:04:55',NULL,0),(180,'playerVirtual7','playerVirtual7_563574327',0,'2018-02-12 14:04:55',NULL,0),(181,'playerVirtual14','playerVirtual14_765651',0,'2018-02-12 14:05:06',NULL,0),(182,'playerVirtual14','playerVirtual14_765651',0,'2018-02-12 14:05:06',NULL,0),(183,'playerVirtual16','playerVirtual16_5623125514',0,'2018-02-12 14:05:28',NULL,0),(184,'playerVirtual16','playerVirtual16_5623125514',0,'2018-02-12 14:05:28',NULL,0),(185,'playerVirtual18','playerVirtual18_284757920',0,'2018-02-12 14:05:29',NULL,0),(186,'playerVirtual18','playerVirtual18_284757920',0,'2018-02-12 14:05:30',NULL,0),(187,'playerVirtual10','playerVirtual10_272887063',0,'2018-02-12 14:05:43',NULL,0),(188,'playerVirtual10','playerVirtual10_272887063',0,'2018-02-12 14:05:43',NULL,0),(189,'playerVirtual19','playerVirtual19_39d339d356',3,'2018-02-12 14:05:46',NULL,0),(190,'playerVirtual5','playerVirtual5_655aeb9724',3,'2018-02-12 14:05:46',NULL,0),(191,'playerVirtual9','playerVirtual9_915459d5e2',3,'2018-02-12 14:05:51',NULL,0),(192,'playerVirtual7','playerVirtual7_e79def2729',3,'2018-02-12 14:05:55',NULL,0),(193,'playerVirtual14','playerVirtual14_37b7eba686',3,'2018-02-12 14:06:06',NULL,0),(194,'playerVirtual16','playerVirtual16_2642184fab',3,'2018-02-12 14:06:28',NULL,0),(195,'playerVirtual18','playerVirtual18_d2bd0b121d',3,'2018-02-12 14:06:29',NULL,0),(196,'playerVirtual10','playerVirtual10_4d674bc8f7',3,'2018-02-12 14:06:42',NULL,0),(197,'playerVirtual11','playerVirtual11_38676294',0,'2018-02-12 14:09:12',NULL,0),(198,'playerVirtual11','playerVirtual11_38676294',0,'2018-02-12 14:09:12',NULL,0),(199,'playerVirtual14','playerVirtual14_182859403',1,'2018-02-12 14:09:51',NULL,0),(200,'playerVirtual14','playerVirtual14_31efbe37cc',4,'2018-02-12 14:09:51',NULL,0),(201,'playerVirtual14','playerVirtual14_182859403',1,'2018-02-12 14:09:54',NULL,0),(202,'playerVirtual11','playerVirtual11_4415156bff',4,'2018-02-12 14:10:12',NULL,0),(203,'playerVirtual4','playerVirtual4_182859403',0,'2018-02-12 14:10:15',NULL,0),(204,'playerVirtual4','playerVirtual4_182859403',0,'2018-02-12 14:10:15',NULL,0),(205,'playerVirtual8','playerVirtual8_4820204870',0,'2018-02-12 14:10:31',NULL,0),(206,'playerVirtual8','playerVirtual8_4820204870',0,'2018-02-12 14:10:31',NULL,0),(207,'playerVirtual12','playerVirtual12_6282149131',0,'2018-02-12 14:10:41',NULL,0),(208,'playerVirtual12','playerVirtual12_6282149131',0,'2018-02-12 14:10:42',NULL,0),(209,'playerVirtual2','playerVirtual2_990694203',0,'2018-02-12 14:10:55',NULL,0),(210,'playerVirtual2','playerVirtual2_990694203',0,'2018-02-12 14:10:59',NULL,0),(211,'playerVirtual13','playerVirtual13_990694203',0,'2018-02-12 14:11:07',NULL,0),(212,'playerVirtual13','playerVirtual13_990694203',0,'2018-02-12 14:11:08',NULL,0),(213,'playerVirtual3','playerVirtual3_6280638724',0,'2018-02-12 14:11:12',NULL,0),(214,'playerVirtual3','playerVirtual3_6280638724',0,'2018-02-12 14:11:13',NULL,0),(215,'playerVirtual6','playerVirtual6_6280643141',0,'2018-02-12 14:11:15',NULL,0),(216,'playerVirtual6','playerVirtual6_6280643141',0,'2018-02-12 14:11:15',NULL,0),(217,'playerVirtual4','playerVirtual4_42864e4433',4,'2018-02-12 14:11:15',NULL,0),(218,'playerVirtual15','playerVirtual15_4476462938',0,'2018-02-12 14:11:29',NULL,0),(219,'playerVirtual15','playerVirtual15_4476462938',0,'2018-02-12 14:11:29',NULL,0),(220,'playerVirtual8','playerVirtual8_e03bfc716a',4,'2018-02-12 14:11:31',NULL,0),(221,'playerVirtual17','playerVirtual17_272887063',0,'2018-02-12 14:11:37',NULL,0),(222,'playerVirtual17','playerVirtual17_272887063',0,'2018-02-12 14:11:37',NULL,0),(223,'playerVirtual19','playerVirtual19_2359368952',0,'2018-02-12 14:11:40',NULL,0),(224,'playerVirtual19','playerVirtual19_2359368952',0,'2018-02-12 14:11:41',NULL,0),(225,'playerVirtual12','playerVirtual12_b5fe13e11d',4,'2018-02-12 14:11:42',NULL,0),(226,'playerVirtual10','playerVirtual10_272887063',1,'2018-02-12 14:11:43',NULL,0),(227,'playerVirtual10','playerVirtual10_e886e18040',4,'2018-02-12 14:11:43',NULL,0),(228,'playerVirtual10','playerVirtual10_272887063',1,'2018-02-12 14:11:43',NULL,0),(229,'playerVirtual5','playerVirtual5_1436323714',0,'2018-02-12 14:11:53',NULL,0),(230,'playerVirtual2','playerVirtual2_52f5e38f72',4,'2018-02-12 14:11:55',NULL,0),(231,'playerVirtual5','playerVirtual5_1436323714',0,'2018-02-12 14:11:58',NULL,0),(232,'playerVirtual9','playerVirtual9_682797',0,'2018-02-12 14:12:03',NULL,0),(233,'playerVirtual9','playerVirtual9_682797',0,'2018-02-12 14:12:03',NULL,0),(234,'playerVirtual7','playerVirtual7_214880781',0,'2018-02-12 14:12:04',NULL,0),(235,'playerVirtual7','playerVirtual7_214880781',0,'2018-02-12 14:12:04',NULL,0),(236,'playerVirtual13','playerVirtual13_e921afb7e1',4,'2018-02-12 14:12:08',NULL,0),(237,'playerVirtual16','playerVirtual16_16914091',0,'2018-02-12 14:12:11',NULL,0),(238,'playerVirtual16','playerVirtual16_16914091',0,'2018-02-12 14:12:12',NULL,0),(239,'playerVirtual3','playerVirtual3_5cf5a64e92',4,'2018-02-12 14:12:13',NULL,0),(240,'playerVirtual6','playerVirtual6_cdcf97553f',4,'2018-02-12 14:12:15',NULL,0);
/*!40000 ALTER TABLE `REQUEST` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `STATUS`
--

DROP TABLE IF EXISTS `STATUS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `STATUS` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `players` int(11) DEFAULT '0',
  `all_requests` int(11) DEFAULT '0',
  `accepts` int(11) DEFAULT '0',
  `rejects` int(11) DEFAULT '0',
  `fairness` float DEFAULT '0',
  `timestamp` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `STATUS`
--

LOCK TABLES `STATUS` WRITE;
/*!40000 ALTER TABLE `STATUS` DISABLE KEYS */;
INSERT INTO `STATUS` VALUES (1,0,0,0,0,0,'2018-02-12 13:53:22'),(2,20,20,18,2,0.9,'2018-02-12 13:58:22'),(3,20,48,43,5,0.895833,'2018-02-12 14:03:23'),(4,20,58,53,5,0.913793,'2018-02-12 14:08:23');
/*!40000 ALTER TABLE `STATUS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `THRESHOLD`
--

DROP TABLE IF EXISTS `THRESHOLD`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `THRESHOLD` (
  `division` int(11) NOT NULL,
  `botton` float DEFAULT '0',
  `top` float DEFAULT '0',
  PRIMARY KEY (`division`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `THRESHOLD`
--

LOCK TABLES `THRESHOLD` WRITE;
/*!40000 ALTER TABLE `THRESHOLD` DISABLE KEYS */;
INSERT INTO `THRESHOLD` VALUES (1,8.76,20),(2,4.38,8.76),(3,0,4.38);
/*!40000 ALTER TABLE `THRESHOLD` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `VM`
--

DROP TABLE IF EXISTS `VM`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `VM` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `origin_add` varchar(45) NOT NULL,
  `origin_id` varchar(45) NOT NULL,
  `origin_name` varchar(45) NOT NULL,
  `destiny_add` varchar(45) NOT NULL,
  `destiny_name` varchar(45) NOT NULL,
  `destiny_id` varchar(45) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `vcpus` int(11) NOT NULL,
  `mem` bigint(20) NOT NULL,
  `disk` bigint(20) NOT NULL,
  `timestamp_received` timestamp NULL DEFAULT NULL,
  `timestamp_finished` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `VM`
--

LOCK TABLES `VM` WRITE;
/*!40000 ALTER TABLE `VM` DISABLE KEYS */;
INSERT INTO `VM` VALUES (1,'192.168.0.200','playerVirtual1_450512000','playerVirtual1','192.168.0.200','playerVirtual11','playerVirtual11_6f67be9edb',1,1,2048,20,'2018-02-12 13:56:04',NULL),(2,'192.168.0.200','playerVirtual11_1438244924','playerVirtual11','192.168.0.200','playerVirtual1','playerVirtual11_1438244924',0,1,2048,20,'2018-02-12 13:56:06','2018-02-12 13:56:06'),(3,'192.168.0.200','playerVirtual4_640692267','playerVirtual4','192.168.0.200','playerVirtual8','playerVirtual8_e2e07791c2',1,1,512,1,'2018-02-12 13:56:09',NULL),(4,'192.168.0.200','playerVirtual8_2381571381','playerVirtual8','192.168.0.200','playerVirtual4','playerVirtual4_75a084d834',1,1,2048,20,'2018-02-12 13:56:11',NULL),(5,'192.168.0.200','playerVirtual2_5297461910','playerVirtual2','192.168.0.200','playerVirtual13','playerVirtual13_a9c44d2708',1,1,512,1,'2018-02-12 13:56:12',NULL),(6,'192.168.0.200','playerVirtual13_2790332778','playerVirtual13','192.168.0.200','playerVirtual2','playerVirtual2_a09e3478ff',1,2,4096,40,'2018-02-12 13:56:15',NULL),(7,'192.168.0.200','playerVirtual3_369721705','playerVirtual3','192.168.0.200','playerVirtual6','playerVirtual6_48fdaa8e09',1,2,4096,40,'2018-02-12 13:56:16',NULL),(8,'192.168.0.200','playerVirtual6_317469422','playerVirtual6','192.168.0.200','playerVirtual3','playerVirtual3_11cee1f945',1,2,4096,40,'2018-02-12 13:56:17',NULL),(9,'192.168.0.200','playerVirtual15_6955737','playerVirtual15','192.168.0.200','playerVirtual17','playerVirtual17_3c40716afe',1,1,2048,20,'2018-02-12 13:56:17',NULL),(10,'192.168.0.200','playerVirtual17_257338104','playerVirtual17','192.168.0.200','playerVirtual15','playerVirtual15_8f597e6c76',1,2,4096,40,'2018-02-12 13:56:17',NULL),(11,'192.168.0.200','playerVirtual19_3584940347','playerVirtual19','192.168.0.200','playerVirtual5','playerVirtual5_702fb1e94a',1,1,512,1,'2018-02-12 13:56:18',NULL),(12,'192.168.0.200','playerVirtual5_2433236783','playerVirtual5','192.168.0.200','playerVirtual19','playerVirtual19_9305e61e01',1,1,2048,20,'2018-02-12 13:56:18',NULL),(13,'192.168.0.200','playerVirtual9_3338579772','playerVirtual9','192.168.0.200','playerVirtual7','playerVirtual7_58c8547aa7',1,1,2048,20,'2018-02-12 13:56:19',NULL),(14,'192.168.0.200','playerVirtual7_257407216','playerVirtual7','192.168.0.200','playerVirtual9','playerVirtual9_c91e1fdab0',1,2,4096,40,'2018-02-12 13:56:19',NULL),(15,'192.168.0.200','playerVirtual14_182859403','playerVirtual14','192.168.0.200','playerVirtual12','playerVirtual12_a456b95948',3,1,512,1,'2018-02-12 13:56:27','2018-02-12 14:09:54'),(16,'192.168.0.200','playerVirtual12_2359368952','playerVirtual12','192.168.0.200','playerVirtual14','playerVirtual14_39e7794d4b',3,1,512,1,'2018-02-12 13:56:30','2018-02-12 14:04:42'),(17,'192.168.0.200','playerVirtual0_16917741','playerVirtual0','192.168.0.200','playerVirtual16','playerVirtual16_ac627ea70f',1,1,512,1,'2018-02-12 13:56:33',NULL),(18,'192.168.0.200','playerVirtual16_2545640208','playerVirtual16','192.168.0.200','playerVirtual0','playerVirtual16_2545640208',0,1,2048,20,'2018-02-12 13:56:42','2018-02-12 13:56:42'),(19,'192.168.0.200','playerVirtual18_908315','playerVirtual18','192.168.0.200','playerVirtual10','playerVirtual10_b1340f9eca',1,1,2048,20,'2018-02-12 13:56:44',NULL),(20,'192.168.0.200','playerVirtual10_539194189','playerVirtual10','192.168.0.200','playerVirtual18','playerVirtual18_e6b4497e9e',1,1,2048,20,'2018-02-12 13:56:52',NULL),(21,'192.168.0.200','playerVirtual1_4820204870','playerVirtual1','192.168.0.200','playerVirtual11','playerVirtual11_289896bff1',1,2,4096,40,'2018-02-12 13:59:30',NULL),(22,'192.168.0.200','playerVirtual11_8058564','playerVirtual11','192.168.0.200','playerVirtual1','playerVirtual11_8058564',0,1,2048,20,'2018-02-12 14:00:20','2018-02-12 14:00:20'),(23,'192.168.0.200','playerVirtual4_1429160667','playerVirtual4','192.168.0.200','playerVirtual8','playerVirtual8_5d64e96435',1,1,2048,20,'2018-02-12 14:00:21',NULL),(24,'192.168.0.200','playerVirtual8_3338010893','playerVirtual8','192.168.0.200','playerVirtual4','playerVirtual4_e7b81fa832',1,1,512,1,'2018-02-12 14:00:22',NULL),(25,'192.168.0.200','playerVirtual2_82730999','playerVirtual2','192.168.0.200','playerVirtual13','playerVirtual13_52e28c9992',1,1,512,1,'2018-02-12 14:00:27',NULL),(26,'192.168.0.200','playerVirtual13_351652724','playerVirtual13','192.168.0.200','playerVirtual2','playerVirtual2_ec9dce71bd',1,1,2048,20,'2018-02-12 14:00:28',NULL),(27,'192.168.0.200','playerVirtual3_6571218','playerVirtual3','192.168.0.200','playerVirtual6','playerVirtual6_f633e6c119',1,1,2048,20,'2018-02-12 14:00:29',NULL),(28,'192.168.0.200','playerVirtual6_778566023','playerVirtual6','192.168.0.200','playerVirtual3','playerVirtual3_568b41e738',1,1,512,1,'2018-02-12 14:00:31',NULL),(29,'192.168.0.200','playerVirtual15_1436344784','playerVirtual15','192.168.0.200','playerVirtual17','playerVirtual17_b08f52e3f8',1,1,2048,20,'2018-02-12 14:00:35',NULL),(30,'192.168.0.200','playerVirtual17_1339662','playerVirtual17','192.168.0.200','playerVirtual15','playerVirtual15_9fb77d7c1c',1,1,2048,20,'2018-02-12 14:00:36',NULL),(31,'192.168.0.200','playerVirtual19_317497342','playerVirtual19','192.168.0.200','playerVirtual5','playerVirtual5_92cdacae87',1,1,512,1,'2018-02-12 14:00:37',NULL),(32,'192.168.0.200','playerVirtual5_284794223','playerVirtual5','192.168.0.200','playerVirtual19','playerVirtual19_fddfc82eba',1,1,2048,20,'2018-02-12 14:00:38',NULL),(33,'192.168.0.200','playerVirtual9_359920779','playerVirtual9','192.168.0.200','playerVirtual7','playerVirtual7_418bf454a7',1,1,512,1,'2018-02-12 14:00:38',NULL),(34,'192.168.0.200','playerVirtual7_904011','playerVirtual7','192.168.0.200','playerVirtual9','playerVirtual9_c422b3b8e6',1,1,2048,20,'2018-02-12 14:00:38',NULL),(35,'192.168.0.200','playerVirtual12_257338074','playerVirtual12','192.168.0.200','playerVirtual14','playerVirtual14_5cf11db7ee',1,2,4096,40,'2018-02-12 14:00:40',NULL),(36,'192.168.0.200','playerVirtual14_2904109077','playerVirtual14','192.168.0.200','playerVirtual12','playerVirtual12_8107414c8a',1,1,512,1,'2018-02-12 14:00:41',NULL),(37,'192.168.0.200','playerVirtual0_905614','playerVirtual0','192.168.0.200','playerVirtual16','playerVirtual16_fe4f8973de',1,1,2048,20,'2018-02-12 14:00:41',NULL),(38,'192.168.0.200','playerVirtual16_1093460','playerVirtual16','192.168.0.200','playerVirtual0','playerVirtual16_1093460',0,1,512,1,'2018-02-12 14:00:42','2018-02-12 14:00:42'),(39,'192.168.0.200','playerVirtual18_6569547','playerVirtual18','192.168.0.200','playerVirtual10','playerVirtual10_dfbdeb2d79',1,1,2048,20,'2018-02-12 14:00:42',NULL),(40,'192.168.0.200','playerVirtual10_470485660','playerVirtual10','192.168.0.200','playerVirtual18','playerVirtual18_4142d9acf6',1,2,4096,40,'2018-02-12 14:00:43',NULL),(41,'192.168.0.200','playerVirtual1_30788568','playerVirtual1','192.168.0.200','playerVirtual11','playerVirtual11_ed8ccf154b',1,1,512,1,'2018-02-12 14:02:45',NULL),(42,'192.168.0.200','playerVirtual11_5792765','playerVirtual11','192.168.0.200','playerVirtual1','playerVirtual11_5792765',0,1,512,1,'2018-02-12 14:02:47','2018-02-12 14:02:47'),(43,'192.168.0.200','playerVirtual4_38671842','playerVirtual4','192.168.0.200','playerVirtual8','playerVirtual8_98a0eeb7e8',1,1,512,1,'2018-02-12 14:02:58',NULL),(44,'192.168.0.200','playerVirtual8_400453824','playerVirtual8','192.168.0.200','playerVirtual4','playerVirtual4_bf668a04bc',1,1,512,1,'2018-02-12 14:02:59',NULL),(45,'192.168.0.200','playerVirtual2_4820318661','playerVirtual2','192.168.0.200','playerVirtual13','playerVirtual13_39808d3a8c',1,2,4096,40,'2018-02-12 14:03:08',NULL),(46,'192.168.0.200','playerVirtual13_4819935267','playerVirtual13','192.168.0.200','playerVirtual2','playerVirtual2_173f21b5fa',1,2,4096,40,'2018-02-12 14:03:12',NULL),(47,'192.168.0.200','playerVirtual3_4820217293','playerVirtual3','192.168.0.200','playerVirtual6','playerVirtual6_6cb3e386f8',1,2,4096,40,'2018-02-12 14:03:16',NULL),(48,'192.168.0.200','playerVirtual6_6264344062','playerVirtual6','192.168.0.200','playerVirtual3','playerVirtual3_6627d5016c',1,1,512,1,'2018-02-12 14:03:17',NULL),(49,'192.168.0.200','playerVirtual15_2378747961','playerVirtual15','192.168.0.200','playerVirtual17','playerVirtual17_0d33c31509',1,1,512,1,'2018-02-12 14:03:26',NULL),(50,'192.168.0.200','playerVirtual17_5068098508','playerVirtual17','192.168.0.200','playerVirtual15','playerVirtual15_8454386e1c',1,1,2048,20,'2018-02-12 14:03:37',NULL),(51,'192.168.0.200','playerVirtual19_227443932','playerVirtual19','192.168.0.200','playerVirtual5','playerVirtual5_fb06ed3dee',1,1,2048,20,'2018-02-12 14:04:46',NULL),(52,'192.168.0.200','playerVirtual5_1095593','playerVirtual5','192.168.0.200','playerVirtual19','playerVirtual19_273255811e',1,1,512,1,'2018-02-12 14:04:46',NULL),(53,'192.168.0.200','playerVirtual9_2148750930','playerVirtual9','192.168.0.200','playerVirtual7','playerVirtual7_25fdef2211',1,1,2048,20,'2018-02-12 14:04:51',NULL),(54,'192.168.0.200','playerVirtual7_563574327','playerVirtual7','192.168.0.200','playerVirtual9','playerVirtual9_7a1b07c8b7',1,1,2048,20,'2018-02-12 14:04:56',NULL),(55,'192.168.0.200','playerVirtual14_765651','playerVirtual14','192.168.0.200','playerVirtual12','playerVirtual12_56b6da8d44',1,1,2048,20,'2018-02-12 14:05:07',NULL),(56,'192.168.0.200','playerVirtual16_5623125514','playerVirtual16','192.168.0.200','playerVirtual14','playerVirtual14_b21a10e832',1,1,2048,20,'2018-02-12 14:05:28',NULL),(57,'192.168.0.200','playerVirtual18_284757920','playerVirtual18','192.168.0.200','playerVirtual16','playerVirtual16_bfef4d56e8',1,1,2048,20,'2018-02-12 14:05:30',NULL),(58,'192.168.0.200','playerVirtual10_272887063','playerVirtual10','192.168.0.200','playerVirtual18','playerVirtual18_1dd5754913',3,1,2048,20,'2018-02-12 14:05:43','2018-02-12 14:11:43'),(59,'192.168.0.200','playerVirtual11_38676294','playerVirtual11','192.168.0.200','playerVirtual10','playerVirtual10_dee4d58705',1,1,512,1,'2018-02-12 14:09:12',NULL),(60,'192.168.0.200','playerVirtual4_182859403','playerVirtual4','192.168.0.200','playerVirtual11','playerVirtual11_65e107f719',1,1,512,1,'2018-02-12 14:10:15',NULL),(61,'192.168.0.200','playerVirtual8_4820204870','playerVirtual8','192.168.0.200','playerVirtual4','playerVirtual4_854f4be9b8',1,2,4096,40,'2018-02-12 14:10:31',NULL),(62,'192.168.0.200','playerVirtual12_6282149131','playerVirtual12','192.168.0.200','playerVirtual8','playerVirtual8_480dbf6775',1,1,512,1,'2018-02-12 14:10:42',NULL),(63,'192.168.0.200','playerVirtual2_990694203','playerVirtual2','192.168.0.200','playerVirtual6','playerVirtual6_b70ab17761',1,1,2048,20,'2018-02-12 14:10:59',NULL),(64,'192.168.0.200','playerVirtual13_990694203','playerVirtual13','192.168.0.200','playerVirtual2','playerVirtual2_805f7d47af',1,1,2048,20,'2018-02-12 14:11:08',NULL),(65,'192.168.0.200','playerVirtual3_6280638724','playerVirtual3','192.168.0.200','playerVirtual13','playerVirtual13_61ea5254d3',1,1,512,1,'2018-02-12 14:11:13',NULL),(66,'192.168.0.200','playerVirtual6_6280643141','playerVirtual6','192.168.0.200','playerVirtual17','playerVirtual17_2b7d6861e2',1,1,512,1,'2018-02-12 14:11:15',NULL),(67,'192.168.0.200','playerVirtual15_4476462938','playerVirtual15','192.168.0.200','playerVirtual19','playerVirtual19_597aadc294',1,1,2048,20,'2018-02-12 14:11:29',NULL),(68,'192.168.0.200','playerVirtual17_272887063','playerVirtual17','192.168.0.200','playerVirtual15','playerVirtual15_1d85bb97b7',1,1,2048,20,'2018-02-12 14:11:37',NULL),(69,'192.168.0.200','playerVirtual19_2359368952','playerVirtual19','192.168.0.200','playerVirtual5','playerVirtual5_017771a4db',1,1,512,1,'2018-02-12 14:11:41',NULL),(70,'192.168.0.200','playerVirtual5_1436323714','playerVirtual5','192.168.0.200','playerVirtual7','playerVirtual7_d9eeae6869',1,1,2048,20,'2018-02-12 14:11:58',NULL),(71,'192.168.0.200','playerVirtual9_682797','playerVirtual9','192.168.0.200','playerVirtual12','playerVirtual12_c6021a71a3',1,1,2048,20,'2018-02-12 14:12:03',NULL),(72,'192.168.0.200','playerVirtual7_214880781','playerVirtual7','192.168.0.200','playerVirtual9','playerVirtual9_20e88d3b8a',1,1,2048,20,'2018-02-12 14:12:05',NULL),(73,'192.168.0.200','playerVirtual16_16914091','playerVirtual16','192.168.0.200','playerVirtual14','playerVirtual14_9683e18880',1,1,2048,20,'2018-02-12 14:12:12',NULL);
/*!40000 ALTER TABLE `VM` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-02-12 12:22:54
