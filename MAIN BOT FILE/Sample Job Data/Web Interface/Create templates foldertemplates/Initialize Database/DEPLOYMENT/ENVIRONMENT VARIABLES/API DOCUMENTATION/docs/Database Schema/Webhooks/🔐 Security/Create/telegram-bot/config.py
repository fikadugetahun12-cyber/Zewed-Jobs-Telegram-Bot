#!/usr/bin/env python3
"""
Configuration module for ZewedJobs Telegram Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Telegram Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASS = os.getenv('DB_PASS', '')
    DB_NAME = os.getenv('DB_NAME', 'zewedjobs_admin')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Web Dashboard
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'admin123')
    PORT = int(os.getenv('PORT', 5000))
    
    # API
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8080/api')
    API_KEY = os.getenv('API_KEY')
    
    # Job Alerts
    ALERT_CHECK_INTERVAL = int(os.getenv('ALERT_CHECK_INTERVAL', 3600))
    MAX_JOBS_PER_ALERT = int(os.getenv('MAX_JOBS_PER_ALERT', 5))
    
    # Features
    ENABLE_JOB_POSTING = os.getenv('ENABLE_JOB_POSTING', 'true').lower() == 'true'
    ENABLE_RESUME_UPLOAD = os.getenv('ENABLE_RESUME_UPLOAD', 'true').lower() == 'true'
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
    
    # Limits
    MAX_JOBS_PER_SEARCH = 20
    MAX_APPLICATIONS_PER_USER = 50
    MESSAGE_RATE_LIMIT = 30  # messages per second
    
    # URLs
    ADMIN_PANEL_URL = os.getenv('ADMIN_PANEL_URL', 'http://localhost:8080/admin')
    HELP_EMAIL = os.getenv('HELP_EMAIL', 'support@zewedjobs.com')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        
        if not cls.DB_HOST:
            errors.append("DB_HOST is required")
        
        if not cls.DB_NAME:
            errors.append("DB_NAME is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    @classmethod
    def get_database_url(cls):
        """Get database connection URL"""
        return f"mysql+mysqlconnector://{cls.DB_USER}:{cls.DB_PASS}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def to_dict(cls):
        """Return configuration as dictionary"""
        return {
            'bot_token': cls.BOT_TOKEN[:10] + '...' if cls.BOT_TOKEN else None,
            'admin_ids': cls.ADMIN_IDS,
            'db_host': cls.DB_HOST,
            'db_name': cls.DB_NAME,
            'webhook_url': cls.WEBHOOK_URL,
            'port': cls.PORT,
            'features': {
                'job_posting': cls.ENABLE_JOB_POSTING,
                'resume_upload': cls.ENABLE_RESUME_UPLOAD,
                'email_notifications': cls.ENABLE_EMAIL_NOTIFICATIONS
            }
        }

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️ Configuration warning: {e}")
    print("Some features may not work correctly.")
