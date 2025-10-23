-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 01, 2025 at 01:06 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `intpt_easms`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin_accounts`
--

CREATE TABLE `admin_accounts` (
  `admin_id` int(11) NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin_accounts`
--

INSERT INTO `admin_accounts` (`admin_id`, `username`, `password`, `name`) VALUES
(1, 'admin', 'admin', 'admin'),
(2, '123', '123', '123'),
(3, '112233', '112233', 'Jerecho');

-- --------------------------------------------------------

--
-- Table structure for table `attendance_logs`
--

CREATE TABLE `attendance_logs` (
  `attendance_id` int(11) NOT NULL,
  `employee_id` int(11) DEFAULT NULL,
  `date_in` date DEFAULT NULL,
  `date_out` date DEFAULT NULL,
  `time_in` time DEFAULT NULL,
  `time_out` time DEFAULT NULL,
  `hours_worked` decimal(5,2) DEFAULT NULL,
  `hours_overtime` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `attendance_logs`
--

INSERT INTO `attendance_logs` (`attendance_id`, `employee_id`, `date_in`, `date_out`, `time_in`, `time_out`, `hours_worked`, `hours_overtime`) VALUES
(2, 1, '2025-06-01', '2025-06-01', '11:20:50', '11:20:52', 0.00, 0.00),
(3, 1, '2025-06-01', '2025-06-01', '11:22:15', '11:22:18', 0.00, 0.00),
(4, 2, '2025-06-01', '2025-06-01', '11:24:09', '11:24:11', 0.00, 0.00),
(5, 2, '2025-06-01', '2025-06-01', '11:26:31', '11:26:35', 0.00, 0.00),
(6, 1, '2025-06-01', '2025-06-01', '14:07:34', '14:07:41', 0.00, 0.00);

-- --------------------------------------------------------

--
-- Table structure for table `employees`
--

CREATE TABLE `employees` (
  `employee_id` int(11) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `birthdate` date DEFAULT NULL,
  `contact_number` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `position` varchar(50) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `employees`
--

INSERT INTO `employees` (`employee_id`, `first_name`, `last_name`, `birthdate`, `contact_number`, `address`, `position`, `username`, `password`) VALUES
(1, 'Jerecho', 'Framil', '2002-09-23', '09563179622', 'Imus City, Cavite', 'Back-end Programmer', 'Jerecho', 'Framil'),
(2, 'Jairus', 'Espiritu', '2002-09-23', '09123456789', 'Pasay', 'Back-end Programmer', 'Jai', 'dasdas'),
(3, 'Stephannie ', 'Rosas', '2005-05-19', '09876543211', 'Pasay City', 'Front-end Programmer', 'Stephannie', 'Rosas'),
(4, 'Maria', 'Vallido', '2005-04-02', '09562147855', 'Laguna', 'Front-end Programmer', 'Maria', 'Vallido'),
(5, 'Jeira Mae', 'Quinto', '2005-04-18', '09587412688', 'Taguig', 'Front-end Programmer', 'Jeira', 'Quinto');

-- --------------------------------------------------------

--
-- Table structure for table `payroll`
--

CREATE TABLE `payroll` (
  `payroll_id` int(11) NOT NULL,
  `employee_id` int(11) DEFAULT NULL,
  `total_hours` decimal(6,2) DEFAULT NULL,
  `total_overtime_hours` decimal(6,2) DEFAULT NULL,
  `basic_salary` decimal(10,2) DEFAULT NULL,
  `basic_pay_per_hour` decimal(8,2) DEFAULT NULL,
  `overtime_pay_per_hour` decimal(8,2) DEFAULT NULL,
  `gross_salary` decimal(10,2) DEFAULT NULL,
  `pagibig` decimal(8,2) DEFAULT NULL,
  `philhealth` decimal(8,2) DEFAULT NULL,
  `SSS` decimal(8,2) DEFAULT NULL,
  `tax` decimal(8,2) DEFAULT NULL,
  `total_deduction` decimal(10,2) DEFAULT NULL,
  `bonus` decimal(8,2) DEFAULT NULL,
  `net_salary` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `payroll`
--

INSERT INTO `payroll` (`payroll_id`, `employee_id`, `total_hours`, `total_overtime_hours`, `basic_salary`, `basic_pay_per_hour`, `overtime_pay_per_hour`, `gross_salary`, `pagibig`, `philhealth`, `SSS`, `tax`, `total_deduction`, `bonus`, `net_salary`) VALUES
(1, 1, 80.00, 20.00, 40000.00, 125.00, 156.25, 13125.00, 200.00, 1600.00, 1350.00, 1052.76, 4202.76, 2.00, 8924.24),
(2, 2, 160.00, 10.00, 40000.00, 187.50, 234.37, 32343.70, 200.00, 1600.00, 1350.00, 2594.29, 5744.29, 0.00, 26599.41),
(3, 3, 20.00, 10.00, 20000.00, 125.00, 156.25, 4062.50, 200.00, 800.00, 900.00, 0.00, 1900.00, 0.00, 2162.50),
(4, 4, 50.00, 20.00, 50000.00, 312.50, 390.63, 23437.50, 200.00, 2000.00, 1350.00, 2050.64, 5600.64, 0.00, 17836.86),
(5, 5, 90.00, 30.00, 90000.00, 562.50, 703.13, 71718.75, 200.00, 3200.00, 1350.00, 11457.17, 16207.17, 0.00, 55511.58);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin_accounts`
--
ALTER TABLE `admin_accounts`
  ADD PRIMARY KEY (`admin_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `attendance_logs`
--
ALTER TABLE `attendance_logs`
  ADD PRIMARY KEY (`attendance_id`),
  ADD KEY `employee_id` (`employee_id`);

--
-- Indexes for table `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`employee_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `payroll`
--
ALTER TABLE `payroll`
  ADD PRIMARY KEY (`payroll_id`),
  ADD KEY `employee_id` (`employee_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin_accounts`
--
ALTER TABLE `admin_accounts`
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `attendance_logs`
--
ALTER TABLE `attendance_logs`
  MODIFY `attendance_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `employees`
--
ALTER TABLE `employees`
  MODIFY `employee_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `payroll`
--
ALTER TABLE `payroll`
  MODIFY `payroll_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `attendance_logs`
--
ALTER TABLE `attendance_logs`
  ADD CONSTRAINT `attendance_logs_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`);

--
-- Constraints for table `payroll`
--
ALTER TABLE `payroll`
  ADD CONSTRAINT `payroll_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
