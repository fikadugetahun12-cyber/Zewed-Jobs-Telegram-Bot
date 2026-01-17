# web_dashboard.py - INTEGRATED DASHBOARD
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from database import db  # Shared MySQL database
import json

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'zewed-telegram-bot-secret')

@app.route('/')
def dashboard():
    """Main dashboard showing both Telegram and PHP data"""
    # Get statistics
    stats = db.get_statistics()
    
    # Get recent Telegram users
    telegram_users = db.get_recent_telegram_users(limit=10)
    
    # Get recent applications
    recent_apps = db.get_recent_applications(limit=10)
    
    return render_template('dashboard.html',
                         stats=stats,
                         telegram_users=telegram_users,
                         recent_apps=recent_apps)

@app.route('/api/telegram-stats')
def telegram_stats():
    """API endpoint for Telegram statistics"""
    stats = db.get_statistics()
    
    # Additional Telegram-specific stats
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Daily bot users
    cursor.execute("""
    SELECT DATE(created_at) as date, COUNT(*) as count 
    FROM telegram_users 
    WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
    GROUP BY DATE(created_at)
    ORDER BY date
    """)
    daily_users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'stats': stats,
        'daily_users': daily_users,
        'status': 'online'
    })

@app.route('/webhook/telegram/<token>', methods=['POST'])
def telegram_webhook(token):
    """Webhook endpoint for Telegram (if using webhook)"""
    if token != os.getenv('BOT_TOKEN'):
        return 'Unauthorized', 403
    
    update = request.get_json()
    # Process update...
    
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.getenv('WEB_DASHBOARD_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
