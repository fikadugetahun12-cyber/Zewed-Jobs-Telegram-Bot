import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASS")
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("✅ Connected to MySQL database")
                self.create_tables()
                return True
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                full_name VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(255),
                user_type ENUM('job_seeker', 'employer') DEFAULT 'job_seeker',
                resume_text TEXT,
                experience_years INT DEFAULT 0,
                education_level VARCHAR(100),
                skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employer_id BIGINT NOT NULL,
                title VARCHAR(255) NOT NULL,
                company VARCHAR(255),
                description TEXT NOT NULL,
                requirements TEXT,
                salary_range VARCHAR(100),
                location VARCHAR(255),
                job_type ENUM('full_time', 'part_time', 'contract', 'remote', 'internship') DEFAULT 'full_time',
                category VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                views INT DEFAULT 0,
                applications INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at DATE,
                FOREIGN KEY (employer_id) REFERENCES users(telegram_id) ON DELETE CASCADE
            )
        """)
        
        # Applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_id INT NOT NULL,
                applicant_id BIGINT NOT NULL,
                cover_letter TEXT,
                status ENUM('pending', 'reviewed', 'accepted', 'rejected') DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
                FOREIGN KEY (applicant_id) REFERENCES users(telegram_id) ON DELETE CASCADE
            )
        """)
        
        # Saved jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_jobs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT NOT NULL,
                job_id INT NOT NULL,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
                UNIQUE KEY unique_save (user_id, job_id)
            )
        """)
        
        self.connection.commit()
        cursor.close()
        print("✅ Database tables created/verified")
    
    def get_cursor(self):
        """Get database cursor"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection.cursor(dictionary=True)
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database connection closed")

# Global database instance
db = Database()
