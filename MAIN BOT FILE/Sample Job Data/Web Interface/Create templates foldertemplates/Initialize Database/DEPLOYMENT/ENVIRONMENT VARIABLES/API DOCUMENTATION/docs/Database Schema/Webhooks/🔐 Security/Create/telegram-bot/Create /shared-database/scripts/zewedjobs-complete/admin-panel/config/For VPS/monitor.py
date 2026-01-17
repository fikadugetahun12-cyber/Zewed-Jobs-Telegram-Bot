# monitor.py - Health check and monitoring
import requests
import smtplib
from datetime import datetime

def check_services():
    services = {
        'telegram_bot': 'http://localhost:5000/api/telegram-stats',
        'php_admin': 'https://yourdomain.com/admin-panel/api/health',
        'database': 'check_mysql_connection'
    }
    
    for service, endpoint in services.items():
        try:
            if service == 'database':
                from database import db
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                status = 'UP'
                cursor.close()
                conn.close()
            else:
                response = requests.get(endpoint, timeout=5)
                status = 'UP' if response.status_code == 200 else 'DOWN'
            
            print(f"{service}: {status}")
            
        except Exception as e:
            print(f"{service}: DOWN - {e}")
            # Send alert email
            send_alert(service, str(e))

def send_alert(service, error):
    # Implement email/sms alert
    pass

if __name__ == '__main__':
    check_services()
