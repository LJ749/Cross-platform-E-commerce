-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 08, 2024 at 05:27 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ecommerce`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

CREATE TABLE `accounts` (
  `id` int(11) NOT NULL,
  `firstname` varchar(100) NOT NULL,
  `middlename` varchar(250) NOT NULL,
  `lastname` varchar(250) NOT NULL,
  `birthdate` varchar(20) NOT NULL,
  `sex` varchar(10) NOT NULL,
  `address` varchar(50) NOT NULL,
  `email` varchar(30) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `profile_picture` varchar(255) DEFAULT NULL,
  `otp` int(11) DEFAULT NULL,
  `shop_name` varchar(250) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('Offline','Online','banned','permanent_ban','temporary_ban') DEFAULT 'Offline',
  `housenumber` varchar(250) NOT NULL,
  `street` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `province` varchar(100) DEFAULT NULL,
  `region` varchar(100) DEFAULT NULL,
  `barangay` varchar(100) DEFAULT NULL,
  `valid_id` varchar(255) DEFAULT NULL,
  `account_status` varchar(250) NOT NULL,
  `ban_reason` text DEFAULT NULL,
  `banned_at` datetime DEFAULT NULL,
  `ban_count` int(11) DEFAULT 0,
  `temp_ban_until` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`id`, `firstname`, `middlename`, `lastname`, `birthdate`, `sex`, `address`, `email`, `password`, `role`, `profile_picture`, `otp`, `shop_name`, `created_at`, `status`, `housenumber`, `street`, `city`, `province`, `region`, `barangay`, `valid_id`, `account_status`, `ban_reason`, `banned_at`, `ban_count`, `temp_ban_until`) VALUES
(40, 'Gary', 'T', 'Pascual', '2004-06-08', 'Male', '', 'fivejelle003@gmail.com', 'markkunat', 'Seller', '382552422_6620877701282505_7787427874181815131_n.jpg', NULL, 'Bain', '2024-12-02 14:55:42', 'Offline', '2000', 'Street1', 'Libungan', 'Cotabato', 'Region XII (SOCCSKSARGEN)', 'Abaga', '451715215_1137614994158264_2111053659220931947_n.jpg', 'Approved', NULL, NULL, 2, NULL),
(43, 'Vien Andrai', 'Apilado', 'Millando', '2002-11-01', 'Male', '', 'apilado.vienandrai28@gmail.com', 'bain1234', 'Buyer', '434734460_1056408328752737_8527047114698074504_n.jpg', NULL, NULL, '2024-12-08 05:15:30', 'Offline', '567', 'National Highway', 'Calauan', 'Laguna', 'Region IV-A (CALABARZON)', 'Bangyas', '451715215_1137614994158264_2111053659220931947_n.jpg', 'Approved', NULL, NULL, 1, NULL),
(44, 'Bain', 'sopo', 'Millando', '2002-12-18', 'Female', '', 'lordjoaquin73@gmail.com', 'sopomillando', 'Seller', 'sopo.png', NULL, NULL, '2024-12-08 11:58:14', 'Offline', '567', 'National Highway', 'Carmona', 'Cavite', 'Region IV-A (CALABARZON)', 'Maduya', '451715215_1137614994158264_2111053659220931947_n.jpg', 'Approved', NULL, NULL, 0, NULL),
(45, 'Gary', 'taleon', 'Pascua', '2003-06-03', 'Male', '', 'pascuagary5@gmail.com', 'gary1234', 'Buyer', 'FB_IMG_1712820448511.jpg', NULL, NULL, '2024-12-08 13:28:15', 'Online', '567', 'Phase 8', 'Santa Cruz', 'Laguna', 'Region IV-A (CALABARZON)', 'Bubukal', '449828168_485541214166335_7545808675628203604_n.jpg', 'Approved', NULL, NULL, 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(30) NOT NULL,
  `email` varchar(30) NOT NULL,
  `password` varchar(30) NOT NULL,
  `role` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `email`, `password`, `role`) VALUES
(2, 'admin@gmail.com', '123', 'Admin');

-- --------------------------------------------------------

--
-- Table structure for table `archive_users`
--

CREATE TABLE `archive_users` (
  `id` int(11) NOT NULL,
  `original_id` int(11) NOT NULL,
  `firstname` varchar(100) NOT NULL,
  `middlename` varchar(250) DEFAULT NULL,
  `lastname` varchar(250) NOT NULL,
  `birthdate` varchar(20) DEFAULT NULL,
  `sex` varchar(10) DEFAULT NULL,
  `address` varchar(50) DEFAULT NULL,
  `email` varchar(30) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(20) DEFAULT NULL,
  `profile_picture` varchar(255) DEFAULT NULL,
  `ban_reason` text DEFAULT NULL,
  `archived_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `street` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `province` varchar(100) DEFAULT NULL,
  `region` varchar(100) DEFAULT NULL,
  `barangay` varchar(100) DEFAULT NULL,
  `valid_id` varchar(255) DEFAULT NULL,
  `account_status` varchar(250) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('offline','active','banned','permanent_ban','temporary_ban') DEFAULT 'offline',
  `ban_count` int(11) DEFAULT 0,
  `banned_at` datetime DEFAULT NULL,
  `temp_ban_until` datetime DEFAULT NULL,
  `otp` int(11) DEFAULT NULL,
  `shop_name` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `buyer_address`
--

CREATE TABLE `buyer_address` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `address` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `carts`
--

CREATE TABLE `carts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `total_items` int(11) DEFAULT 0,
  `total_price` decimal(10,2) DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `carts`
--

INSERT INTO `carts` (`id`, `user_id`, `total_items`, `total_price`, `created_at`) VALUES
(20, 40, 10, 1300.00, '2024-12-06 22:19:51'),
(21, 43, 2, 110.00, '2024-12-08 00:54:50'),
(22, 45, 240, 8740.00, '2024-12-08 05:30:00');

-- --------------------------------------------------------

--
-- Table structure for table `cart_items`
--

CREATE TABLE `cart_items` (
  `id` int(11) NOT NULL,
  `cart_id` int(11) NOT NULL,
  `inventory_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `variation_name` varchar(255) DEFAULT NULL,
  `variation_value` varchar(255) DEFAULT NULL,
  `variation_id` int(11) DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `variation_attribute_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `role` varchar(50) NOT NULL,
  `user_name` varchar(255) NOT NULL,
  `comment` text DEFAULT NULL,
  `rating` int(11) DEFAULT NULL CHECK (`rating` between 1 and 5),
  `photo` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`id`, `product_id`, `user_id`, `role`, `user_name`, `comment`, `rating`, `photo`, `created_at`) VALUES
(8, 184, 45, 'Buyer', 'Gary taleon Pascua', 'kulang system', 1, 'FB_IMG_1712820453286.jpg', '2024-12-08 05:34:37');

-- --------------------------------------------------------

--
-- Table structure for table `inventory`
--

CREATE TABLE `inventory` (
  `id` int(11) NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `quantity` int(11) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `details` text DEFAULT NULL,
  `product_picture` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `shop_name` varchar(250) NOT NULL,
  `seller_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `inventory`
--

INSERT INTO `inventory` (`id`, `product_name`, `price`, `quantity`, `category`, `details`, `product_picture`, `created_at`, `shop_name`, `seller_id`) VALUES
(182, 'Pedigree Dog Food', 110.00, 18, 'Food', 'Good ', 'Z.png', '2024-12-08 08:39:35', 'Bain', 40),
(183, 'Fish Food Fish Food Fish Food Fish Food Fish Food', 200.00, 0, 'Food', 'sdafasdf', '2Q.png', '2024-12-08 09:10:53', 'Bain', 40),
(184, 'Bird Food', 231.00, 0, 'Food', 'asdsdasd', 'c648734a-39e1-4c60-8b59-5c6aa4f16c0f.jfif', '2024-12-08 12:02:27', 'Bain', 40),
(185, 'Orijen Fish Food', 323.00, 115, 'Grooming', 'adsasdad', 'vitamins.png', '2024-12-08 12:04:45', 'Bain', 40);

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`id`, `sender_id`, `receiver_id`, `message`, `timestamp`) VALUES
(9, 40, 43, 'Yoh', '2024-12-08 11:42:34'),
(10, 43, 40, 'oh ge', '2024-12-08 11:54:25'),
(11, 43, 40, 'adada', '2024-12-08 11:54:34'),
(12, 43, 40, 'afdasdf', '2024-12-08 11:54:35'),
(13, 43, 40, 'wefasf', '2024-12-08 11:54:37'),
(14, 43, 40, 'asdfas', '2024-12-08 11:54:39'),
(15, 43, 40, 'dfasfas', '2024-12-08 11:54:40'),
(16, 43, 40, 'asf', '2024-12-08 11:54:44'),
(17, 43, 40, 'dfasdf', '2024-12-08 11:54:46'),
(18, 43, 40, 'dasdfasdf', '2024-12-08 11:54:50'),
(19, 43, 40, 'fdsfdsdf', '2024-12-08 11:54:51'),
(20, 43, 44, 'yoh', '2024-12-08 12:40:07'),
(21, 44, 43, 'yoh', '2024-12-08 12:40:22'),
(22, 45, 44, 'Yoh', '2024-12-08 16:22:07');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `status` enum('unread','read') DEFAULT 'unread',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `notification_type` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `message`, `status`, `created_at`, `notification_type`) VALUES
(31, 40, 'Your order with Gary T, Pascua (Order ID: 188) has been canceled. Reason: Found a better price', 'unread', '2024-12-02 15:36:15', ''),
(34, 40, 'Your order with Gary T, Pascual (Order ID: 191) has been canceled. Reason: Found a better price', 'read', '2024-12-07 10:25:13', 'order_cancellation'),
(35, 43, 'Please verify your account via OTP.', 'unread', '2024-12-08 05:15:30', 'Account Created'),
(36, 44, 'Please verify your account via OTP.', 'unread', '2024-12-08 11:58:14', 'Account Created'),
(37, 45, 'Please verify your account via OTP.', 'unread', '2024-12-08 13:28:15', 'Account Created'),
(38, 40, 'Your order with Gary T, Pascual (Order ID: 204) has been canceled. Reason: Found a better price', 'unread', '2024-12-08 15:41:23', 'order_cancellation'),
(39, 40, 'Your order with Gary T, Pascual (Order ID: 204) has been canceled. Reason: Found a better price', 'unread', '2024-12-08 15:41:28', 'order_cancellation'),
(40, 40, 'Your order with Gary T, Pascual (Order ID: 205) has been canceled. Reason: Wrong Item Shipped', 'unread', '2024-12-08 15:44:43', 'order_cancellation'),
(41, 40, 'Your order with Gary T, Pascual (Order ID: 206) has been canceled. Reason: Item not Available', 'unread', '2024-12-08 15:52:39', 'order_cancellation'),
(42, 40, 'Your order with Gary T, Pascual (Order ID: 207) has been canceled. Reason: Out Of Stock', 'unread', '2024-12-08 15:54:45', 'order_cancellation'),
(43, 40, 'Your order with Gary T, Pascual (Order ID: 208) has been canceled. Reason: Wrong Item Shipped', 'unread', '2024-12-08 15:56:42', 'order_cancellation'),
(44, 40, 'Your order with Gary T, Pascual (Order ID: 209) has been canceled. Reason: Other', 'unread', '2024-12-08 16:01:11', 'seller_order_cancellation'),
(45, 40, 'Your order with Gary T, Pascual (Order ID: 210) has been canceled. Reason: Other', 'unread', '2024-12-08 16:26:22', 'seller_order_cancellation');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `address` varchar(255) NOT NULL,
  `payment_method` enum('cod','credit_card','gcash') NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `user_id`, `address`, `payment_method`, `total`, `created_at`, `updated_at`) VALUES
(163, 40, 'Lynville, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 650.00, '2024-12-02 07:34:18', '2024-12-02 15:34:18'),
(165, 40, 'Akbar, Bulalo, Sultan Kudarat, Maguindanao del Norte, Bangsamoro Autonomous Region In Muslim Mindanao (BARMM)', 'cod', 750.00, '2024-12-07 02:05:39', '2024-12-07 10:05:39'),
(166, 40, 'Akbar, Bulalo, Sultan Kudarat, Maguindanao del Norte, Bangsamoro Autonomous Region In Muslim Mindanao (BARMM)', 'cod', 750.00, '2024-12-07 02:07:19', '2024-12-07 10:07:19'),
(167, 40, 'Akbar, Bulalo, Sultan Kudarat, Maguindanao del Norte, Bangsamoro Autonomous Region In Muslim Mindanao (BARMM)', 'cod', 150.00, '2024-12-07 02:09:20', '2024-12-07 10:09:20'),
(168, 43, 'National Highway, Bangyas, Calauan, Laguna, Region IV-A (CALABARZON)', 'cod', 160.00, '2024-12-08 00:55:03', '2024-12-08 08:55:03'),
(169, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 173.00, '2024-12-08 05:31:21', '2024-12-08 13:31:21'),
(170, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 2450.00, '2024-12-08 05:44:38', '2024-12-08 13:44:38'),
(171, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 15088.00, '2024-12-08 06:34:37', '2024-12-08 14:34:37'),
(172, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 3130.00, '2024-12-08 06:35:07', '2024-12-08 14:35:07'),
(173, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 7310.00, '2024-12-08 06:42:46', '2024-12-08 14:42:46'),
(174, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 114.00, '2024-12-08 07:24:47', '2024-12-08 15:24:47'),
(175, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 11490.00, '2024-12-08 07:29:11', '2024-12-08 15:29:11'),
(176, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 1480.00, '2024-12-08 07:30:23', '2024-12-08 15:30:23'),
(177, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 7200.00, '2024-12-08 07:40:59', '2024-12-08 15:40:59'),
(178, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 1480.00, '2024-12-08 07:44:25', '2024-12-08 15:44:25'),
(179, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 1480.00, '2024-12-08 07:51:46', '2024-12-08 15:51:46'),
(180, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 114.00, '2024-12-08 07:54:35', '2024-12-08 15:54:35'),
(181, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 82.00, '2024-12-08 07:56:28', '2024-12-08 15:56:28'),
(182, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 82.00, '2024-12-08 08:00:46', '2024-12-08 16:00:46'),
(183, 45, '567, Phase 8, Bubukal, Santa Cruz, Laguna, Region IV-A (CALABARZON)', 'cod', 82.00, '2024-12-08 08:26:05', '2024-12-08 16:26:05');

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `product_price` decimal(10,2) NOT NULL,
  `quantity` int(11) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `variation_name` varchar(255) DEFAULT NULL,
  `variation_value` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `product_image` varchar(250) NOT NULL,
  `status` varchar(250) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `variation_id` int(11) DEFAULT NULL,
  `cancellation_reason` varchar(250) DEFAULT NULL,
  `date_received` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_items`
--

INSERT INTO `order_items` (`id`, `order_id`, `product_id`, `product_name`, `product_price`, `quantity`, `total`, `variation_name`, `variation_value`, `created_at`, `product_image`, `status`, `seller_id`, `variation_id`, `cancellation_reason`, `date_received`) VALUES
(194, 168, 182, 'Pedigree Dog Food', 110.00, 1, 110.00, 'Wet', '1kg', '2024-12-08 08:55:03', 'Z.png', 'cancelled', 40, 185, NULL, NULL),
(195, 169, 184, 'Bird Food', 123.00, 1, 123.00, 'Kilo', '1kg', '2024-12-08 13:31:21', 'c648734a-39e1-4c60-8b59-5c6aa4f16c0f.jfif', 'Received', 40, 188, NULL, '2024-12-08 13:33:31'),
(196, 170, 183, 'Fish Food Fish Food Fish Food Fish Food Fish Food', 200.00, 12, 2400.00, 'Volume', '1kg', '2024-12-08 13:44:38', '2Q.png', 'Out for Delivery', 40, 187, NULL, NULL),
(197, 171, 184, 'Bird Food', 123.00, 122, 15006.00, 'Kilo', '1kg', '2024-12-08 14:34:37', 'c648734a-39e1-4c60-8b59-5c6aa4f16c0f.jfif', 'Order Shipped', 40, 188, NULL, NULL),
(198, 171, 185, 'Orijen Fish Food', 32.00, 1, 32.00, 'Dry', '10kg', '2024-12-08 14:34:37', 'vitamins.png', 'Order Received', 40, 189, NULL, NULL),
(199, 172, 182, 'Pedigree Dog Food', 110.00, 28, 3080.00, 'Wet', '1kg', '2024-12-08 14:35:07', 'Z.png', 'Order Shipped', 40, 185, NULL, NULL),
(200, 173, 182, 'Pedigree Dog Food', 220.00, 33, 7260.00, 'Dry', '2kg', '2024-12-08 14:42:46', 'Z.png', 'Cancelled', 40, 186, NULL, NULL),
(201, 174, 185, 'Orijen Fish Food', 32.00, 2, 64.00, 'Dry', '10kg', '2024-12-08 15:24:47', 'vitamins.png', 'Cancelled', 40, 189, NULL, NULL),
(202, 175, 182, 'Pedigree Dog Food', 1430.00, 8, 11440.00, 'Wet', '13kg', '2024-12-08 15:29:11', 'Z.png', 'Cancelled', 40, 185, NULL, NULL),
(203, 176, 182, 'Pedigree Dog Food', 1430.00, 1, 1430.00, 'Wet', '13kg', '2024-12-08 15:30:23', 'Z.png', 'Cancelled', 40, 185, NULL, NULL),
(204, 177, 182, 'Pedigree Dog Food', 1430.00, 5, 7150.00, 'Wet', '13kg', '2024-12-08 15:40:59', 'Z.png', 'Cancelled', 40, 185, 'Found a better price', NULL),
(205, 178, 182, 'Pedigree Dog Food', 1430.00, 1, 1430.00, 'Wet', '13kg', '2024-12-08 15:44:25', 'Z.png', 'Cancelled', 40, 185, 'Wrong Item Shipped', NULL),
(206, 179, 182, 'Pedigree Dog Food', 1430.00, 1, 1430.00, 'Wet', '13kg', '2024-12-08 15:51:46', 'Z.png', 'Cancelled', 40, 185, 'Item not Available', NULL),
(207, 180, 185, 'Orijen Fish Food', 32.00, 2, 64.00, 'Dry', '10kg', '2024-12-08 15:54:35', 'vitamins.png', 'Cancelled', 40, 189, 'Out Of Stock', NULL),
(208, 181, 185, 'Orijen Fish Food', 32.00, 1, 32.00, 'Dry', '10kg', '2024-12-08 15:56:28', 'vitamins.png', 'Cancelled', 40, 189, 'Wrong Item Shipped', NULL),
(209, 182, 185, 'Orijen Fish Food', 32.00, 1, 32.00, 'Dry', '10kg', '2024-12-08 16:00:46', 'vitamins.png', 'Cancelled', 40, 189, 'Other', NULL),
(210, 183, 185, 'Orijen Fish Food', 32.00, 1, 32.00, 'Dry', '10kg', '2024-12-08 16:26:05', 'vitamins.png', 'Cancelled', 40, 189, 'Other', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `private_messages`
--

CREATE TABLE `private_messages` (
  `id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `recipient_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `sent_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `product_variations`
--

CREATE TABLE `product_variations` (
  `id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_variations`
--

INSERT INTO `product_variations` (`id`, `product_id`) VALUES
(185, 182),
(186, 182),
(187, 183),
(188, 184),
(189, 185);

-- --------------------------------------------------------

--
-- Table structure for table `variation_attributes`
--

CREATE TABLE `variation_attributes` (
  `id` int(11) NOT NULL,
  `variation_id` int(11) DEFAULT NULL,
  `attribute_name` varchar(50) DEFAULT NULL,
  `attribute_value` varchar(50) DEFAULT NULL,
  `attribute_image` varchar(255) DEFAULT NULL,
  `attribute_stock` int(11) NOT NULL,
  `attribute_price` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `variation_attributes`
--

INSERT INTO `variation_attributes` (`id`, `variation_id`, `attribute_name`, `attribute_value`, `attribute_image`, `attribute_stock`, `attribute_price`) VALUES
(188, 185, 'Wet', '1kg', NULL, 0, 110),
(189, 185, 'Wet', '13kg', NULL, 18, 1430),
(190, 186, 'Dry', '2kg', NULL, 0, 220),
(191, 187, 'Volume', '1kg', NULL, 0, 200),
(192, 188, 'Kilo', '1kg', NULL, 0, 123),
(193, 189, 'Dry', '10kg', NULL, 115, 32);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `archive_users`
--
ALTER TABLE `archive_users`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `buyer_address`
--
ALTER TABLE `buyer_address`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `carts`
--
ALTER TABLE `carts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_cart_item` (`cart_id`,`inventory_id`,`variation_name`,`variation_value`),
  ADD KEY `cart_items_ibfk_2` (`inventory_id`),
  ADD KEY `cart_items_ibfk_3` (`variation_id`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_feedback_product` (`product_id`),
  ADD KEY `fk_feedback_user` (`user_id`);

--
-- Indexes for table `inventory`
--
ALTER TABLE `inventory`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_seller_id` (`seller_id`) USING BTREE;

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `receiver_id` (`receiver_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `product_variations`
--
ALTER TABLE `product_variations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_variations_ibfk_1` (`product_id`);

--
-- Indexes for table `variation_attributes`
--
ALTER TABLE `variation_attributes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `variation_id` (`variation_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(30) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `archive_users`
--
ALTER TABLE `archive_users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `buyer_address`
--
ALTER TABLE `buyer_address`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `carts`
--
ALTER TABLE `carts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `cart_items`
--
ALTER TABLE `cart_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=173;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `inventory`
--
ALTER TABLE `inventory`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=186;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=184;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=211;

--
-- AUTO_INCREMENT for table `product_variations`
--
ALTER TABLE `product_variations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=190;

--
-- AUTO_INCREMENT for table `variation_attributes`
--
ALTER TABLE `variation_attributes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=194;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `buyer_address`
--
ALTER TABLE `buyer_address`
  ADD CONSTRAINT `buyer_address_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `carts`
--
ALTER TABLE `carts`
  ADD CONSTRAINT `carts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`cart_id`) REFERENCES `carts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`inventory_id`) REFERENCES `inventory` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cart_items_ibfk_3` FOREIGN KEY (`variation_id`) REFERENCES `product_variations` (`id`);

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `fk_feedback_product` FOREIGN KEY (`product_id`) REFERENCES `inventory` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_feedback_user` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `inventory`
--
ALTER TABLE `inventory`
  ADD CONSTRAINT `fk_user_id` FOREIGN KEY (`seller_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `inventory` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `product_variations`
--
ALTER TABLE `product_variations`
  ADD CONSTRAINT `product_variations_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `inventory` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `variation_attributes`
--
ALTER TABLE `variation_attributes`
  ADD CONSTRAINT `variation_attributes_ibfk_1` FOREIGN KEY (`variation_id`) REFERENCES `product_variations` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
