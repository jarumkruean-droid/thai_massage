/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.7.2-MariaDB, for Win64 (AMD64)
--
-- Host: 192.168.100.22    Database: donation
-- ------------------------------------------------------
-- Server version	11.8.5-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `data_donation`
--

DROP TABLE IF EXISTS `data_donation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_donation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `donation` int(11) NOT NULL,
  `image` varchar(100) NOT NULL,
  `details` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_donation`
--

LOCK TABLES `data_donation` WRITE;
/*!40000 ALTER TABLE `data_donation` DISABLE KEYS */;
INSERT INTO `data_donation` VALUES
(1,'นวดน้ำมัน',150,'นวดน้ำมัน.jpg','นวดน้ำมันเพื่อผ่อนคลายกล้ามเนื้อคลายเส้น'),
(2,'นวดตัว',500,'นวดตัว.jpg','นวดตัวผ่อนคลายเส้นยึด ตึง ให้หายปวดเมื่อย'),
(3,'นวดตัว',500,'นวดตัว.jpg','นวดตัวผ่อนคลายเส้นยึด ตึง ให้หายปวดเมื่อย แบบพิเศษ'),
(4,'นวดนํ้ามัน',500,'นวดน้ำมัน.jpg','นวดน้ำมันเพื่อผ่อนคลายกล้ามเนื้อคลายเส้น แบบพิเศษ'),
(5,'นวดเท้า',400,'นวดเท้า.jpg','นวดผ่อนคลายเส้นเพื่อความสบายในการใช้ชีวิตประจำวัน แบบพิเศษ'),
(6,'นวดเท้า',300,'นวดเท้า.jpg','นวดผ่อนคลายเส้นเพื่อความสบายในการใช้ชีวิตประจำวัน'),
(9,'นวดแผนไทยเพื่อสุขภาพ',600,'นวดน้ำมัน.jpg','นวดแผนไทยอบรม บรรยาบสุขภาพ');
/*!40000 ALTER TABLE `data_donation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `massage_bookings`
--

DROP TABLE IF EXISTS `massage_bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `massage_bookings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `service_id` int(11) NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `service_type` varchar(100) NOT NULL,
  `therapist` varchar(100) NOT NULL,
  `strength` varchar(50) NOT NULL,
  `customer_name` varchar(255) DEFAULT 'ลูกค้า',
  `customer_phone` varchar(20) DEFAULT '',
  `notes` text DEFAULT '',
  `status` enum('pending','confirmed','completed','cancelled') DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `service_id` (`service_id`),
  CONSTRAINT `massage_bookings_ibfk_1` FOREIGN KEY (`service_id`) REFERENCES `data_donation` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `massage_bookings`
--

LOCK TABLES `massage_bookings` WRITE;
/*!40000 ALTER TABLE `massage_bookings` DISABLE KEYS */;
INSERT INTO `massage_bookings` VALUES
(1,3,'โครงการช่วยเหลือผู้ยากไร้','นวดตัว','ปัญญา','ปานกลาง','ลูกค้า','','','pending','2026-04-07 06:50:29','2026-04-07 06:50:29'),
(2,1,'บริจาคให้หมาน้อย - Updated','นวดน้ำมัน','ไหม','แรงมาก','ลูกค้า','','','pending','2026-04-07 06:51:57','2026-04-07 06:51:57'),
(3,2,'บริจาดให้กับแมวเป้า','นวดน้ำมัน','บุญญา','ปานกลาง','ลูกค้า','','','pending','2026-04-07 06:52:29','2026-04-07 06:52:29'),
(4,2,'บริจาดให้กับแมวเป้า','นวดน้ำมัน','บุญญา','ปานกลาง','ลูกค้า','','','pending','2026-04-07 06:52:38','2026-04-07 06:52:38'),
(5,4,'โครงการช่วยเหลือผู้ยากไร้','นวดน้ำมัน','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 06:55:09','2026-04-07 06:55:09'),
(6,4,'โครงการช่วยเหลือผู้ยากไร้','นวดตัว','ไหม','อ่อน','ลูกค้า','','','pending','2026-04-07 06:55:50','2026-04-07 06:55:50'),
(7,4,'โครงการช่วยเหลือผู้ยากไร้','นวดตัว','ไหม','อ่อน','ลูกค้า','','','pending','2026-04-07 07:01:42','2026-04-07 07:01:42'),
(8,2,'บริจาดให้กับแมวเป้า','นวดน้ำมัน','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 07:02:10','2026-04-07 07:02:10'),
(9,5,'mim','นวดน้ำมัน','บุญญา','อ่อน','ลูกค้า','','','pending','2026-04-07 07:06:37','2026-04-07 07:06:37'),
(10,3,'โครงการช่วยเหลือผู้ยากไร้','นวดน้ำมัน','ปัญญา','ปานกลาง','ลูกค้า','','','pending','2026-04-07 07:08:59','2026-04-07 07:08:59'),
(11,2,'นวดตัว','นวดน้ำมัน','บุญญา','แรง','ลูกค้า','','','pending','2026-04-07 07:55:02','2026-04-07 07:55:02'),
(12,2,'นวดตัว','นวดตัว','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 08:02:15','2026-04-07 08:02:15'),
(13,1,'นวดน้ำมัน','นวดเท้า','ไหม','อ่อน','ลูกค้า','','','pending','2026-04-07 08:13:08','2026-04-07 08:13:08'),
(14,1,'นวดน้ำมัน','นวดตัว','ปัญญา','ปานกลาง','ลูกค้า','','','pending','2026-04-07 08:52:32','2026-04-07 08:52:32'),
(15,3,'นวดตัว','นวดตัว','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 08:56:55','2026-04-07 08:56:55'),
(16,2,'นวดตัว','นวดน้ำมัน','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 08:58:48','2026-04-07 08:58:48'),
(17,2,'นวดตัว','นวดน้ำมัน','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 09:01:17','2026-04-07 09:01:17'),
(18,2,'นวดตัว','นวดน้ำมัน','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 09:01:22','2026-04-07 09:01:22'),
(19,1,'นวดน้ำมัน','นวดตัว','ปัญญา','ปานกลาง','ลูกค้า','','','pending','2026-04-07 09:01:57','2026-04-07 09:01:57'),
(20,1,'นวดน้ำมัน','นวดตัว','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 09:03:26','2026-04-07 09:03:26'),
(22,1,'นวดน้ำมัน','นวดตัว','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 09:05:16','2026-04-07 09:05:16'),
(23,1,'นวดน้ำมัน','นวดตัว','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 09:05:54','2026-04-07 09:05:54'),
(24,1,'นวดน้ำมัน','นวดตัว','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 09:08:39','2026-04-07 09:08:39'),
(25,1,'นวดน้ำมัน','นวดตัว','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 09:10:02','2026-04-07 09:10:02'),
(26,1,'นวดน้ำมัน','นวดตัว','ปัญญา','แรง','ลูกค้า','','','pending','2026-04-07 09:10:15','2026-04-07 09:10:15'),
(27,1,'นวดน้ำมัน','นวดตัว','ปัญญา','ปานกลาง','ลูกค้า','','','pending','2026-04-07 09:11:34','2026-04-07 09:11:34'),
(28,2,'นวดตัว','นวดตัว','ปัญญา','ปานกลาง','ลูกค้า','','','pending','2026-04-07 09:11:43','2026-04-07 09:11:43'),
(29,1,'นวดน้ำมัน','นวดเท้า','ไหม','ปานกลาง','ลูกค้า','','','pending','2026-04-07 09:55:04','2026-04-07 09:55:04'),
(30,1,'นวดน้ำมัน','นวดตัว','ปัญญา','อ่อน','ลูกค้า','','','pending','2026-04-08 06:11:45','2026-04-08 06:11:45'),
(31,1,'นวดน้ำมัน','นวดเท้า','ไหม','อ่อน','ลูกค้า','','','pending','2026-04-08 06:15:51','2026-04-08 06:15:51'),
(32,1,'นวดน้ำมัน','นวดตัว','ไหม','ปานกลาง','ลูกค้า','','','pending','2026-04-08 08:30:29','2026-04-08 08:30:29'),
(33,1,'นวดน้ำมัน','นวดน้ำมัน','ปัญญา','ปานกลาง','ลูกค้า','','','pending','2026-04-08 08:35:56','2026-04-08 08:35:56');
/*!40000 ALTER TABLE `massage_bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_login`
--

DROP TABLE IF EXISTS `user_login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_login` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(10) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_login`
--

LOCK TABLES `user_login` WRITE;
/*!40000 ALTER TABLE `user_login` DISABLE KEYS */;
INSERT INTO `user_login` VALUES
(1,'since','123','https://share.google/uKjIVMgVqB1iWOKQx'),
(2,'phing','123123',NULL),
(3,'admin','P@ssword',NULL);
/*!40000 ALTER TABLE `user_login` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'donation'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-04-08 15:37:42
