-- ZewedJobs Complete Database Schema
-- This schema is shared between Admin Panel and Telegram Bot

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS zewedjobs_admin 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE zewedjobs_admin;

-- Users table (for admin panel)
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('administrator', 'job_seeker', 'employer') DEFAULT 'job_seeker',
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    profile_image VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    INDEX idx_role (role),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    website VARCHAR(255),
    location VARCHAR(100),
    industry VARCHAR(50),
    description TEXT,
    logo_url VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    jobs_posted INT DEFAULT 0,
    member_since DATE,
    contact_person VARCHAR(100),
    tax_id VARCHAR(50),
    status ENUM('active', 'inactive', 'pending') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_verified (verified),
    INDEX idx_industry (industry),
    INDEX idx_status (status)
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    company_id INT NOT NULL,
    location VARCHAR(100),
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    salary_currency VARCHAR(3) DEFAULT 'USD',
    salary_display VARCHAR(100),
    job_type ENUM('full_time', 'part_time', 'contract', 'internship', 'remote') DEFAULT 'full_time',
    category VARCHAR(50),
    description TEXT NOT NULL,
    requirements JSON,
    experience_level ENUM('entry', 'mid', 'senior', 'executive') DEFAULT 'mid',
    education_level VARCHAR(50),
    posted_date DATE NOT NULL,
    expiry_date DATE,
    status ENUM('active', 'inactive', 'expired', 'filled') DEFAULT 'active',
    applications_count INT DEFAULT 0,
    views_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_company (company_id),
    INDEX idx_status (status),
    INDEX idx_category (category),
    INDEX idx_type (job_type),
    INDEX idx_posted (posted_date),
    FULLTEXT idx_search (title, description, requirements)
);

-- Job applications table (for admin panel)
CREATE TABLE IF NOT EXISTS job_applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    user_id INT NOT NULL,
    cover_letter TEXT,
    resume_url VARCHAR(255),
    status ENUM('pending', 'reviewed', 'shortlisted', 'rejected', 'accepted') DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (job_id, user_id),
    INDEX idx_status (status),
    INDEX idx_applied (applied_at)
);

-- Telegram users table
CREATE TABLE IF NOT EXISTS telegram_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    user_type ENUM('job_seeker', 'employer', 'admin') DEFAULT 'job_seeker',
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    preferences JSON,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_user_type (user_type)
);

-- Telegram sessions table
CREATE TABLE IF NOT EXISTS telegram_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    current_state VARCHAR(100),
    state_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (telegram_id) REFERENCES telegram_users(telegram_id) ON DELETE CASCADE,
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_state (current_state)
);

-- Telegram job applications table
CREATE TABLE IF NOT EXISTS telegram_job_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    telegram_id BIGINT NOT NULL,
    cover_letter TEXT,
    resume_url VARCHAR(500),
    status ENUM('pending', 'reviewed', 'shortlisted', 'rejected', 'accepted') DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL,
    admin_notes TEXT,
    FOREIGN KEY (telegram_id) REFERENCES telegram_users(telegram_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    INDEX idx_job_id (job_id),
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_status (status),
    INDEX idx_applied (applied_at)
);

-- Telegram job alerts table
CREATE TABLE IF NOT EXISTS telegram_job_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    alert_type VARCHAR(50),
    criteria JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sent TIMESTAMP NULL,
    FOREIGN KEY (telegram_id) REFERENCES telegram_users(telegram_id) ON DELETE CASCADE,
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_alert_type (alert_type),
    INDEX idx_is_active (is_active)
);

-- Telegram messages log
CREATE TABLE IF NOT EXISTS telegram_messages_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    message_type VARCHAR(50),
    message_content TEXT,
    direction ENUM('incoming', 'outgoing') DEFAULT 'incoming',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (telegram_id) REFERENCES telegram_users(telegram_id) ON DELETE CASCADE,
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_message_type (message_type),
    INDEX idx_sent_at (sent_at)
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    parent_id INT NULL,
    icon VARCHAR(50),
    job_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_parent (parent_id)
);

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type ENUM('string', 'number', 'boolean', 'json', 'array') DEFAULT 'string',
    category VARCHAR(50) DEFAULT 'general',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_key (setting_key)
);

-- Activity logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
);

-- Backup logs table
CREATE TABLE IF NOT EXISTS backup_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT,
    record_count INT,
    backup_type ENUM('full', 'partial', 'scheduled', 'manual') DEFAULT 'manual',
    status ENUM('success', 'failed', 'in_progress') DEFAULT 'in_progress',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (backup_type),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);

-- ============================================
-- INSERT DEFAULT DATA
-- ============================================

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, password_hash, role, status) 
VALUES ('admin', 'admin@zewedjobs.com', '$2y$10$9wYmNqMz.3mUz8X5D8qj.eGdV9qjJg8Z8q8q8q8q8q8q8q8q8q8q8q8', 'administrator', 'active')
ON DUPLICATE KEY UPDATE email = VALUES(email);

-- Insert default settings
INSERT INTO settings (setting_key, setting_value, setting_type, category, description) VALUES
('site_name', 'ZewedJobs', 'string', 'general', 'Site name displayed in the admin panel'),
('site_email', 'admin@zewedjobs.com', 'string', 'general', 'Default email for system notifications'),
('items_per_page', '20', 'number', 'general', 'Number of items per page in lists'),
('session_timeout', '30', 'number', 'security', 'Session timeout in minutes'),
('maintenance_mode', 'false', 'boolean', 'system', 'Enable maintenance mode'),
('backup_schedule', 'daily', 'string', 'system', 'Automatic backup schedule'),
('email_notifications', 'true', 'boolean', 'notifications', 'Enable email notifications'),
('telegram_bot_enabled', 'true', 'boolean', 'bot', 'Enable Telegram bot'),
('default_currency', 'USD', 'string', 'jobs', 'Default currency for job salaries'),
('job_expiry_days', '30', 'number', 'jobs', 'Default job expiry in days')
ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);

-- Insert default categories
INSERT INTO categories (name, slug, description, icon) VALUES
('Technology', 'technology', 'Technology and IT jobs', 'bi-laptop'),
('Marketing', 'marketing', 'Marketing and sales jobs', 'bi-megaphone'),
('Finance', 'finance', 'Finance and accounting jobs', 'bi-cash-coin'),
('Healthcare', 'healthcare', 'Healthcare and medical jobs', 'bi-heart-pulse'),
('Education', 'education', 'Education and training jobs', 'bi-mortarboard'),
('Engineering', 'engineering', 'Engineering jobs', 'bi-gear'),
('Design', 'design', 'Design and creative jobs', 'bi-palette'),
('Customer Service', 'customer-service', 'Customer service jobs', 'bi-headset'),
('Human Resources', 'human-resources', 'HR and recruitment jobs', 'bi-people'),
('Operations', 'operations', 'Operations and management jobs', 'bi-gear-wide')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- Insert sample companies
INSERT INTO companies (name, email, phone, website, location, industry, description, verified, member_since) VALUES
('TechCorp Ethiopia', 'info@techcorp-et.com', '+251911223344', 'https://techcorp-et.com', 'Addis Ababa', 'Technology', 'Leading tech company in Ethiopia', TRUE, '2023-01-15'),
('Blue Nile Marketing', 'contact@bluenilemarketing.com', '+251922334455', 'https://bluenilemarketing.com', 'Addis Ababa', 'Marketing', 'Digital marketing agency', TRUE, '2023-03-20'),
('Sheger Finance', 'admin@shegerfinance.com', '+251933445566', 'https://shegerfinance.com', 'Addis Ababa', 'Finance', 'Financial services provider', FALSE, '2023-05-10'),
('EthioHealth Solutions', 'support@ethiohealth.com', '+251944556677', 'https://ethiohealth.com', 'Addis Ababa', 'Healthcare', 'Healthcare technology company', TRUE, '2023-02-28')
ON DUPLICATE KEY UPDATE email = VALUES(email);

-- Insert sample jobs
INSERT INTO jobs (title, company_id, location, salary_min, salary_max, salary_display, job_type, category, description, requirements, posted_date, expiry_date, status) VALUES
('Senior PHP Developer', 1, 'Addis Ababa', 60000, 80000, '$60,000 - $80,000', 'full_time', 'Technology', 'We are looking for an experienced PHP developer to join our team...', '["PHP", "Laravel", "MySQL", "JavaScript", "REST API"]', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'active'),
('Digital Marketing Manager', 2, 'Remote', 50000, 70000, '$50,000 - $70,000', 'full_time', 'Marketing', 'Lead our digital marketing team and drive online growth...', '["Digital Marketing", "SEO", "Social Media", "Google Analytics", "Team Management"]', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'active'),
('Financial Analyst', 3, 'Addis Ababa', 45000, 60000, '$45,000 - $60,000', 'full_time', 'Finance', 'Analyze financial data and prepare reports for decision making...', '["Financial Analysis", "Excel", "Accounting", "Reporting", "Data Analysis"]', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'active'),
('Junior Web Developer', 1, 'Addis Ababa', 30000, 40000, '$30,000 - $40,000', 'full_time', 'Technology', 'Entry-level web developer position for recent graduates...', '["HTML", "CSS", "JavaScript", "PHP", "MySQL"]', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'active'),
('Customer Support Specialist', 4, 'Remote', 25000, 35000, '$25,000 - $35,000', 'full_time', 'Customer Service', 'Provide excellent customer support via email and phone...', '["Customer Service", "Communication", "Problem Solving", "English", "Computer Skills"]', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'active')
ON DUPLICATE KEY UPDATE title = VALUES(title);

-- Update company job counts
UPDATE companies c
SET jobs_posted = (
    SELECT COUNT(*) 
    FROM jobs j 
    WHERE j.company_id = c.id 
    AND j.status = 'active'
);

-- Update category job counts
UPDATE categories cat
SET job_count = (
    SELECT COUNT(*) 
    FROM jobs j 
    WHERE j.category = cat.name 
    AND j.status = 'active'
);
