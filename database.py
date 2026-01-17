# database.py - SQLite Database Handler
import sqlite3
import json
from datetime import datetime
from config import DATABASE_NAME

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_employer BOOLEAN DEFAULT FALSE,
            company TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Jobs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            category TEXT NOT NULL,
            job_type TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            description TEXT NOT NULL,
            requirements TEXT,
            employer_id INTEGER,
            contact_email TEXT,
            contact_phone TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (employer_id) REFERENCES users (user_id)
        )
        ''')
        
        # Applications table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            user_id INTEGER,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            resume_file_id TEXT,
            cover_letter TEXT,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        # User interactions (for recommendations)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            job_id INTEGER,
            interaction_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()
    
    # User methods
    def add_user(self, user_id, username, first_name, last_name):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        self.conn.commit()
    
    def update_user_as_employer(self, user_id, company):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE users 
        SET is_employer = TRUE, company = ?
        WHERE user_id = ?
        ''', (company, user_id))
        self.conn.commit()
    
    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()
    
    # Job methods
    def add_job(self, job_data):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO jobs (title, company, category, job_type, location, 
                         salary, description, requirements, employer_id,
                         contact_email, contact_phone, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data['title'], job_data['company'], job_data['category'],
            job_data['job_type'], job_data.get('location', 'Remote'),
            job_data.get('salary', 'Negotiable'), job_data['description'],
            job_data.get('requirements', ''), job_data['employer_id'],
            job_data.get('contact_email', ''), job_data.get('contact_phone', ''),
            job_data.get('expires_at', datetime.now().timestamp() + 30*24*60*60)
        ))
        job_id = cursor.lastrowid
        self.conn.commit()
        return job_id
    
    def get_jobs(self, category=None, job_type=None, limit=50, offset=0):
        cursor = self.conn.cursor()
        query = "SELECT * FROM jobs WHERE is_active = TRUE"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if job_type:
            query += " AND job_type = ?"
            params.append(job_type)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def get_job_by_id(self, job_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ? AND is_active = TRUE', (job_id,))
        return cursor.fetchone()
    
    def search_jobs(self, keyword):
        cursor = self.conn.cursor()
        query = '''
        SELECT * FROM jobs 
        WHERE is_active = TRUE AND 
              (title LIKE ? OR description LIKE ? OR company LIKE ?)
        ORDER BY created_at DESC
        LIMIT 20
        '''
        search_term = f"%{keyword}%"
        cursor.execute(query, (search_term, search_term, search_term))
        return cursor.fetchall()
    
    def get_user_jobs(self, employer_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM jobs 
        WHERE employer_id = ? 
        ORDER BY created_at DESC
        ''', (employer_id,))
        return cursor.fetchall()
    
    # Application methods
    def add_application(self, application_data):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO applications (job_id, user_id, full_name, email, 
                                 phone, resume_file_id, cover_letter)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            application_data['job_id'], application_data['user_id'],
            application_data['full_name'], application_data['email'],
            application_data['phone'], application_data.get('resume_file_id', ''),
            application_data.get('cover_letter', '')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_job_applications(self, job_id, employer_id):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT a.*, u.username, u.first_name, u.last_name
        FROM applications a
        JOIN users u ON a.user_id = u.user_id
        JOIN jobs j ON a.job_id = j.id
        WHERE a.job_id = ? AND j.employer_id = ?
        ORDER BY a.applied_at DESC
        ''', (job_id, employer_id))
        return cursor.fetchall()
    
    # Statistics
    def get_stats(self):
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE is_active = TRUE')
        active_jobs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM applications')
        total_applications = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_employer = TRUE')
        total_employers = cursor.fetchone()[0]
        
        return {
            'total_users': total_users,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'total_employers': total_employers
        }
    
    def close(self):
        self.conn.close()

# Global database instance
db = Database()
