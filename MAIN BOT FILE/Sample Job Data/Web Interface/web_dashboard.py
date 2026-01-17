# web_dashboard.py - Web dashboard for job management
from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime
from config import DATABASE_NAME

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    """Main dashboard"""
    conn = get_db_connection()
    
    # Get statistics
    stats = conn.execute('''
        SELECT 
            (SELECT COUNT(*) FROM users) as total_users,
            (SELECT COUNT(*) FROM jobs WHERE is_active = 1) as active_jobs,
            (SELECT COUNT(*) FROM applications) as total_applications,
            (SELECT COUNT(*) FROM users WHERE is_employer = 1) as total_employers
    ''').fetchone()
    
    # Get recent jobs
    recent_jobs = conn.execute('''
        SELECT j.*, u.username 
        FROM jobs j 
        LEFT JOIN users u ON j.employer_id = u.user_id
        WHERE j.is_active = 1 
        ORDER BY j.created_at DESC 
        LIMIT 10
    ''').fetchall()
    
    # Get recent applications
    recent_applications = conn.execute('''
        SELECT a.*, j.title as job_title, u.username
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON a.user_id = u.user_id
        ORDER BY a.applied_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                         stats=dict(stats),
                         recent_jobs=recent_jobs,
                         recent_applications=recent_applications)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    conn = get_db_connection()
    
    # Daily applications for the last 7 days
    daily_apps = conn.execute('''
        SELECT DATE(applied_at) as date, COUNT(*) as count
        FROM applications
        WHERE applied_at >= DATE('now', '-7 days')
        GROUP BY DATE(applied_at)
        ORDER BY date
    ''').fetchall()
    
    # Job categories distribution
    categories = conn.execute('''
        SELECT category, COUNT(*) as count
        FROM jobs
        WHERE is_active = 1
        GROUP BY category
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'daily_applications': [dict(row) for row in daily_apps],
        'categories': [dict(row) for row in categories]
    })

@app.route('/jobs')
def jobs_list():
    """List all jobs"""
    conn = get_db_connection()
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    jobs = conn.execute('''
        SELECT j.*, u.username as employer_username
        FROM jobs j
        LEFT JOIN users u ON j.employer_id = u.user_id
        WHERE j.is_active = 1
        ORDER BY j.created_at DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    
    total_jobs = conn.execute('SELECT COUNT(*) FROM jobs WHERE is_active = 1').fetchone()[0]
    
    conn.close()
    
    return render_template('jobs.html',
                         jobs=jobs,
                         page=page,
                         per_page=per_page,
                         total_jobs=total_jobs)

@app.route('/applications/<int:job_id>')
def job_applications(job_id):
    """View applications for a specific job"""
    conn = get_db_connection()
    
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    applications = conn.execute('''
        SELECT a.*, u.username, u.first_name, u.last_name
        FROM applications a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.job_id = ?
        ORDER BY a.applied_at DESC
    ''', (job_id,)).fetchall()
    
    conn.close()
    
    return render_template('applications.html',
                         job=dict(job),
                         applications=applications)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
