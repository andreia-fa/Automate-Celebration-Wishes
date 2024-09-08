-- MySQL dump 10.13  Distrib 8.4.0, for Linux (x86_64)
--
-- Host: localhost    Database: sendlove
-- ------------------------------------------------------
-- Server version	8.4.0

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
-- Table structure for table `contacts_info`
--

DROP TABLE IF EXISTS `contacts_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contacts_info` (
  `Username` varchar(255) DEFAULT NULL,
  `Personal_relationship` varchar(255) DEFAULT NULL,
  `Message_receiver` varchar(255) DEFAULT NULL,
  `Telegram_name` varchar(255) DEFAULT NULL,
  `Birthday_date` date DEFAULT NULL,
  `Created_at` date DEFAULT NULL,
  `Updated_at` date DEFAULT NULL,
  `Recurrence` varchar(255) DEFAULT NULL,
  `Type` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contacts_info`
--

LOCK TABLES `contacts_info` WRITE;
/*!40000 ALTER TABLE `contacts_info` DISABLE KEYS */;
INSERT INTO `contacts_info` VALUES ('Gil Dias','Family','Gil Dias','Gil Dias','2024-06-05','2024-05-10','2024-05-31','Annual','Birthday'),('Mammy','Family','Mammy','(D)','1961-10-26','2024-05-10','2024-05-31','Annual','Birthday'),('Goofy','Gil_new_dog','Gil Dias','Gil Dias','2024-07-17','2024-08-18','2024-08-18','Monthly','puppy');
/*!40000 ALTER TABLE `contacts_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_log`
--

DROP TABLE IF EXISTS `message_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(255) DEFAULT NULL,
  `message` text NOT NULL,
  `date_sent` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_log`
--

LOCK TABLES `message_log` WRITE;
/*!40000 ALTER TABLE `message_log` DISABLE KEYS */;
INSERT INTO `message_log` VALUES (1,'Gil Dias','Happy Birthday! Wishing you a day filled with joy, laughter, and all the things that make you smile! :)','2024-06-05');
/*!40000 ALTER TABLE `message_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `text_message` text,
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,'You are always in my thoughts. ','Nurturing'),(2,'Thank you for being there for me! :)','Nurturing'),(3,'You are always in my thoughts. :)','Nurturing'),(4,'Happy New Year! Wishing you a wonderful year ahead, full of joy and happiness :)','New Year'),(5,'I hope you are having a great day! (L)','Nurturing'),(6,'Remember to take breaks and look after yourself. (L)','Nurturing'),(7,'Thank you for being there for me! :)','Nurturing'),(8,'Sending you lots of love and hugs! :)','Nurturing'),(9,'You brighten my day with your smile! :)','Nurturing'),(10,'Thinking of you always. (L)','Nurturing'),(11,'Your smile means the world to me! :)','Nurturing'),(12,'You are amazing to me, even if today is being a bit challenging for you! Don\'t forget :)','Nurturing'),(13,'Merry Christmas! May your heart be filled with the joy of the season and your home be warmed by the love of family and friends. ','Christmas'),(14,'Wishing you a magical holiday season filled with love, laughter, and all the happiness in the world. Merry Christmas! <3','Christmas'),(15,'May the spirit of Christmas fill your home with peace, joy, and endless blessings. Merry Christmas to you and your loved ones! :*','Christmas'),(16,'Happy Birthday! Wishing you a day filled with joy, laughter, and all the things that make you smile! :)','Birthday'),(17,'On your special day, may the happiest of moments surround you, and may all your dreams and wishes come true! Happy Birthday! <3','Birthday'),(18,'Another year older, another reason to celebrate how incredible you are! Happy Birthday! :*)','Birthday'),(19,'Wishing you a New Year filled with new hope, new joy, and new beginnings. Happy New Year! :)','New Year'),(20,'May this New Year bring you peace, happiness, and prosperity. Cheers to a wonderful year ahead! <3','New Year'),(21,'As the New Year dawns, may all your dreams and aspirations come true. Wishing you a year filled with love and success! :*','New Year'),(22,'New Year, new opportunities, new adventures! May you seize every moment and make the most of the coming year. Happy New Year! :)','New Year'),(23,'Here\'s to a fresh start and a new chapter in your life. May the New Year bring you endless possibilities and endless happiness. Cheers! (^_^)','New Year'),(24,'Hi (#username#), I want to celebrate with you this (#monthplaceholder#) with our blessed (#baby#). May your day be filled with giggles and joy! :) <3','baby'),(25,'Hi (#username#), every month with (#baby#) is a reason to celebrate. In this (#monthplaceholder#), keep shining bright! :D *','baby'),(26,'Hi (#username#), watching (#baby#) grow is the greatest joy. Lets celebrate this (#monthplaceholder#) with love and laughter! :) *','baby'),(27,'Hi (#username#), sending hugs and kisses to the sweetest (#baby#). In this (#monthplaceholder#), may your days be full of wonder. :* <3','baby'),(28,'Hi (#username#), another month, another milestone for (#baby#)! Lets celebrate this (#monthplaceholder#) and make every day special! :) *','baby'),(29,'Hi (#username#), may your (#monthplaceholder#) be as bright as (#baby#)\'s smile and as sweet as their laughter! :D <3','baby'),(30,'Hi (#username#), hugs and kisses to you, little (#baby#). Every day with you is a blessing. In this (#monthplaceholder#), lets celebrate! :) *','baby'),(31,'Hi (#username#), heres to celebrating another month with (#baby#)! In this (#monthplaceholder#), may it be filled with wonderful moments and joy! :D *','baby'),(32,'Hi (#username#), your giggles are music to our ears. Wishing (#baby#) a (#monthplaceholder#) filled with happiness and fun! :) <3','baby'),(33,'Hi (#username#), another month, another reason to celebrate (#baby#)! Lets make this (#monthplaceholder#) full of growth and joy. :D *','baby'),(34,'Hi (#username#), may (#baby#)\'s heart be as full as the love we have for them this (#monthplaceholder#). Happy new month! :) <3','baby'),(35,'Hi (#username#), to the sweetest (#baby#): May this (#monthplaceholder#) be filled with love, joy, and endless smiles! :D *','baby'),(36,'Hi (#username#), every month, (#baby#) brings new joys into our lives. In this (#monthplaceholder#), lets celebrate with brightness! :) <3','baby'),(37,'Hi (#username#), sending you all the love in the world. May (#baby#)\'s days in this (#monthplaceholder#) be as magical as they are! :D *','baby'),(38,'Hi (#username#), another month of growing and glowing for (#baby#)! Lets celebrate this (#monthplaceholder#) with pride. :) <3','baby'),(39,'Hi (#username#), may (#baby#)\'s (#monthplaceholder#) be filled with playful giggles and warm cuddles. We love you! :D *','baby'),(40,'Hi (#username#), heres to discovering new joys with (#baby#) in this (#monthplaceholder#). Lets make sweet memories! :) <3','baby'),(41,'Hi (#username#), every day with (#baby#) is a treasure. Wishing you a (#monthplaceholder#) full of love and joy! :D *','baby'),(42,'Hi (#username#), (#baby#)\'s smile lights up our lives. Heres to another (#monthplaceholder#) of happiness and wonder! :) <3','baby'),(43,'Hi (#username#), another month of joy with (#baby#), our little star. In this (#monthplaceholder#), lets celebrate and keep shining! :D *','baby'),(44,'Hi (#username#), to my furry friend (#puppy#), I want to celebrate this (#monthplaceholder#) with you. Keep wagging and spreading joy! :) <3','puppy'),(45,'Hi (#username#), every month with (#puppy#) is a celebration. In this (#monthplaceholder#), lets enjoy the wagging tails and joyful barks! :D *','puppy'),(46,'Hi (#username#), (#puppy#)\'s playful spirit brightens every day. In this (#monthplaceholder#), lets celebrate with fun and frolic! :) <3','puppy'),(47,'Hi (#username#), to my four-legged buddy (#puppy#): May this (#monthplaceholder#) be full of treats, belly rubs, and endless fun! :D *','puppy'),(48,'Hi (#username#), another month with you, (#puppy#), my loyal companion. Lets make this (#monthplaceholder#) memorable with wagging tails and happy moments! :) <3','puppy'),(49,'Hi (#username#), every day is better with (#puppy#) by my side. In this (#monthplaceholder#), lets celebrate with happy adventures! :D *','puppy'),(50,'Hi (#username#), you brighten my days with your wagging tail, (#puppy#). In this (#monthplaceholder#), lets celebrate with more fun and joy! :) <3','puppy'),(51,'Hi (#username#), may your (#monthplaceholder#) be filled with belly rubs, treats, and lots of playtime, (#puppy#)! Thanks for being the best friend ever. :D *','puppy'),(52,'Hi (#username#), (#puppy#)\'s loyalty and love make every month special. In this (#monthplaceholder#), lets celebrate with cuddles and wagging tails! :) <3','puppy'),(53,'Hi (#username#), another month of joy with (#puppy#), my favorite furry friend. Lets make this (#monthplaceholder#) amazing and full of happiness! :D *','puppy'),(54,'Hi (#username#), to my playful (#puppy#), may this (#monthplaceholder#) be filled with joy, treats, and endless tail wags! :) <3','puppy'),(55,'Hi (#username#), youre my daily joy, (#puppy#). In this (#monthplaceholder#), lets celebrate with fun adventures and happy moments! :D *','puppy'),(56,'Hi (#username#), every month with (#puppy#) is a celebration of our bond. Lets make this (#monthplaceholder#) special! :) <3','puppy'),(57,'Hi (#username#), may your (#monthplaceholder#) be full of happy barks, playful paws, and cozy naps, (#puppy#)! You make life better! :D *','puppy'),(58,'Hi (#username#), another month of joy with (#puppy#), my furry buddy. Lets keep making fun memories in this (#monthplaceholder#)! :) <3','puppy'),(59,'Hi (#username#), your wagging tail and loving eyes bring so much happiness. Heres to a fantastic (#monthplaceholder#) with (#puppy#)! :D *','puppy'),(60,'Hi (#username#), cheers to another month of adventures with (#puppy#). In this (#monthplaceholder#), lets enjoy every moment! :) <3','puppy'),(61,'Hi (#username#), your playful antics brighten every day. Happy (#monthplaceholder#) to my best buddy (#puppy#)! :D *','puppy'),(62,'Hi (#username#), may your (#monthplaceholder#) be filled with belly rubs, new toys, and plenty of treats, (#puppy#)! Thanks for being awesome. :) <3','puppy'),(63,'Hi (#username#), another month, another chance to enjoy life with (#puppy#), my loyal friend. Heres to a great (#monthplaceholder#)! :D *','puppy');
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-18 13:38:52
