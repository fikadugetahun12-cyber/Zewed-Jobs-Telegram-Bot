# database.py - MYSQL VERSION
import mysql.connector
from mysql.connector import pooling
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            # Load from PHP config or environment
            self.db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'zewedjobs_db'),
                'charset': 'utf8mb4',
                'use_unicode': True,
                'pool_name': 'telegram_pool',
                'pool_size': 5
            }
            
            # Create connection pool
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**self.db_config)
            logger.info("✅ Connected to MySQL database")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.get_connection()
    
    def sync_tables(self):
        """Sync with existing PHP tables or create needed ones"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if PHP jobs table exists
            cursor.execute("SHOW TABLES LIKE 'jobs'")
            if not cursor.fetchone():
                # Create jobs table compatible with PHP
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    company VARCHAR(255),
                    category VARCHAR(100),
                    job_type VARCHAR(50),
                    location VARCHAR(255),
                    salary VARCHAR(100),
                    description TEXT,
                    requirements TEXT,
                    employer_id INT,
                    contact_email VARCHAR(255),
                    contact_phone VARCHAR(50),
                    is_active TINYINT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    telegram_posted TINYINT DEFAULT 0,
                    telegram_message_id VARCHAR(100),
                    INDEX idx_category (category),
                    INDEX idx_is_active (is_active),
                    INDEX idx_created (created_at)
                )
                ''')
            
            # Create telegram_users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                phone VARCHAR(50),
                email VARCHAR(255),
                is_employer TINYINT DEFAULT 0,
                employer_company VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                settings JSON,
                INDEX idx_employer (is_employer)
            )
            ''')
            
            # Create telegram_applications table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_applications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_id INT,
                user_id BIGINT,
                full_name VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(50),
                resume_file_id VARCHAR(255),
                cover_letter TEXT,
                status ENUM('pending', 'reviewed', 'accepted', 'rejected') DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
                INDEX idx_status (status),
                INDEX idx_applied (applied_at)
            )
            ''')
            
            conn.commit()
            logger.info("✅ Database tables synchronized")
            
        except Exception as e:
            logger.error(f"❌ Table sync failed: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    # ==================== CRUD METHODS ====================
    
    def get_jobs_from_php(self, limit=50, offset=0):
        """Get jobs from PHP database"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT j.*, 
               u.name as employer_name,
               u.email as employer_email
        FROM jobs j
        LEFT JOIN users u ON j.employer_id = u.id
        WHERE j.is_active = 1
        ORDER BY j.created_at DESC
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, (limit, offset))
        jobs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return jobs
    
    def add_telegram_user(self, user_data):
        """Add/update Telegram user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO telegram_users 
        (user_id, username, first_name, last_name, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        username = VALUES(username),
        first_name = VALUES(first_name),
        last_name = VALUES(last_name),
        last_active = CURRENT_TIMESTAMP
        """
        
        cursor.execute(query, (
            user_data['user_id'],
            user_data.get('username'),
            user_data.get('first_name'),
            user_data.get('last_name'),
            datetime.now()
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def log_telegram_application(self, application):
        """Log application from Telegram"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO telegram_applications 
        (job_id, user_id, full_name, email, phone, cover_letter, applied_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            application['job_id'],
            application['user_id'],
            application['full_name'],
            application['email'],
            application['phone'],
            application.get('cover_letter', ''),
            datetime.now()
        ))
        
        application_id = cursor.lastrowid
        
        # Also add to PHP applications table if exists
        try:
            cursor.execute("SHOW TABLES LIKE 'applications'")
            if cursor.fetchone():
                php_query = """
                INSERT INTO applications 
                (job_id, applicant_name, applicant_email, applicant_phone, 
                 cover_letter, source, created_at)
                VALUES (%s, %s, %s, %s, %s, 'telegram_bot', %s)
                """
                cursor.execute(php_query, (
                    application['job_id'],
                    application['full_name'],
                    application['email'],
                    application['phone'],
                    application.get('cover_letter', ''),
                    datetime.now()
                ))
        except:
            pass  # PHP table might not exist
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return application_id
    
    def get_statistics(self):
        """Get combined stats from both systems"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        stats = {}
        
        # Total jobs from PHP
        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE is_active = 1")
        stats['active_jobs'] = cursor.fetchone()['count']
        
        # Total Telegram users
        cursor.execute("SELECT COUNT(*) as count FROM telegram_users")
        stats['telegram_users'] = cursor.fetchone()['count']
        
        # Total applications (both PHP and Telegram)
        total_apps = 0
        cursor.execute("SELECT COUNT(*) as count FROM telegram_applications")
        total_apps += cursor.fetchone()['count']
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM applications")
            php_apps = cursor.fetchone()
            if php_apps:
                total_apps += php_apps['count']
        except:
            pass
        
        stats['total_applications'] = total_apps
        
        cursor.close()
        conn.close()
        
        return stats

# Global database instance
db = Database()
db.sync_tables()
