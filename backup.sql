-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: go_user_admin
-- ------------------------------------------------------
-- Server version	8.0.45

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

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `created_at` datetime(3) DEFAULT NULL,
  `updated_at` datetime(3) DEFAULT NULL,
  `deleted_at` datetime(3) DEFAULT NULL,
  `username` varchar(32) NOT NULL,
  `password` varchar(64) NOT NULL,
  `phone` varchar(11) DEFAULT NULL,
  `role` varchar(16) NOT NULL DEFAULT 'user',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `phone` (`phone`),
  KEY `idx_users_deleted_at` (`deleted_at`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'2026-03-28 16:25:43.530','2026-03-28 16:25:43.530',NULL,'testuser','123456','13812345678','user'),(2,'2026-03-28 21:04:22.748','2026-03-28 21:04:22.748',NULL,'admin','123456','','admin'),(17,'2026-03-28 21:18:51.331','2026-03-28 21:18:51.331',NULL,'admin123','123456','19150670269','admin'),(21,'2026-03-28 21:51:12.688','2026-03-28 21:51:12.688',NULL,'user','123456','18014392680','user'),(23,NULL,NULL,NULL,'test','$2b$10$fyggSGaMY.oUJK9D1trcWO4AfDcqIkThjyeYr78Aa5j0/TiCvWELW',NULL,'user'),(24,NULL,NULL,NULL,'fudian','$2b$10$9NOjodLtVt5I15ThqjO7l.ptbb5NNp94eJzm61Q9O0iAOa.paKe2e',NULL,'user'),(25,NULL,NULL,NULL,'fudian123','$2b$10$H/W7/R1FiOlSRWUkTPRejOW5Lkp5cKu.Nh0tHeeiLUKiDzRHgzqB2',NULL,'teacher'),(26,NULL,NULL,NULL,'teacher','$2b$10$4SFxi5bB2pU90GzHInRxA.Xuh8s/aR7Mi5eJJIJCYMLFg1yLluDNa',NULL,'teacher'),(27,NULL,NULL,NULL,'fudian1234','$2b$10$XWi1QA6.TQ7Z36u6dp.LuOFy.TQML9rMZK8/TMFNil0VjuGOd4yaS',NULL,'doctor');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-02  9:48:08
