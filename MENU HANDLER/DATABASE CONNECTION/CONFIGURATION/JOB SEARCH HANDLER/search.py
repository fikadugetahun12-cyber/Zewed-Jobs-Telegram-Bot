from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import db
from config import Config
import math

async def search_jobs(update: Update, context: CallbackContext):
    """Start job search"""
    user_id = update.effective_user.id
    
    # Check if user has profile
    cursor = db.get_cursor()
    cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (user_id,))
    if not cursor.fetchone():
        await update.message.reply_text(
            "⚠️ *Please create a profile first!*\n\n"
            "Use /profile to create your profile before searching for jobs.",
            parse_mode="Markdown"
        )
        cursor.close()
        return
    
    cursor.close()
    
    keyboard = [
        [
            InlineKeyboardButton("🔍 Search by Keyword", callback_data="search_keyword"),
            InlineKeyboardButton("📁 Browse Categories", callback_data="browse_categories")
        ],
        [
            InlineKeyboardButton("📍 Search by Location", callback_data="search_location"),
            InlineKeyboardButton("💰 Salary Range", callback_data="search_salary")
        ],
        [
            InlineKeyboardButton("🎯 Job Type", callback_data="search_type"),
            InlineKeyboardButton("🔥 Latest Jobs", callback_data="latest_jobs")
        ],
        [InlineKeyboardButton("⭐ Saved Jobs", callback_data="saved_jobs")]
    ]
    
    await update.message.reply_text(
        "🔍 *Job Search*\n\n"
        "How would you like to search for jobs?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def browse_categories(update: Update, context: CallbackContext):
    """Show job categories"""
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    row = []
    for i, category in enumerate(Config.JOB_CATEGORIES, 1):
        # Get count of jobs in this category
        cursor = db.get_cursor()
        cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE category = %s AND is_active = TRUE", (category,))
        count = cursor.fetchone()['count']
        cursor.close()
        
        row.append(InlineKeyboardButton(f"{category} ({count})", callback_data=f"category_{i}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_search")])
    
    await query.message.edit_text(
        "📁 *Browse Jobs by Category*\n\n"
        "Select a category to view available jobs:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_jobs_by_category(update: Update, context: CallbackContext, page=1, jobs_per_page=5):
    """Show jobs in a category with pagination"""
    query = update.callback_query
    await query.answer()
    
    cat_index = int(query.data.replace("category_", "")) - 1
    category = Config.JOB_CATEGORIES[cat_index]
    
    # Calculate offset
    offset = (page - 1) * jobs_per_page
    
    # Get jobs count
    cursor = db.get_cursor()
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM jobs 
        WHERE category = %s AND is_active = TRUE
    """, (category,))
    total_jobs = cursor.fetchone()['total']
    
    # Get jobs for current page
    cursor.execute("""
        SELECT j.*, u.username, u.full_name as company_contact
        FROM jobs j
        LEFT JOIN users u ON j.employer_id = u.telegram_id
        WHERE j.category = %s AND j.is_active = TRUE
        ORDER BY j.created_at DESC
        LIMIT %s OFFSET %s
    """, (category, jobs_per_page, offset))
    
    jobs = cursor.fetchall()
    cursor.close()
    
    if not jobs:
        await query.message.edit_text(
            f"📭 *No Jobs Found*\n\n"
            f"No active jobs in *{category}* category.\n\n"
            f"Try another category or check back later.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="browse_categories")]])
        )
        return
    
    # Create jobs list
    jobs_text = f"📁 *{category}*\n\n"
    jobs_text += f"📊 *{total_jobs}* jobs available\n\n"
    
    for i, job in enumerate(jobs, 1):
        job_type = Config.JOB_TYPES.get(job['job_type'], 'Full Time')
        jobs_text += f"{offset + i}. *{job['title']}*\n"
        jobs_text += f"   🏢 {job['company'] or 'Company not specified'}\n"
        jobs_text += f"   📍 {job['location'] or 'Location not specified'}\n"
        jobs_text += f"   💰 {job['salary_range'] or 'Salary negotiable'}\n"
        jobs_text += f"   ⏰ {job_type}\n"
        jobs_text += f"   📅 {job['created_at'].strftime('%b %d')}\n"
        jobs_text += f"   👁️ {job['views']} views | 📥 {job['applications']} applications\n\n"
    
    # Create pagination keyboard
    keyboard = []
    
    # Job details buttons for first job on page
    if jobs:
        first_job = jobs[0]
        keyboard.append([
            InlineKeyboardButton("📋 View Details", callback_data=f"view_job_{first_job['id']}"),
            InlineKeyboardButton("⭐ Save", callback_data=f"save_job_{first_job['id']}")
        ])
    
    # Pagination buttons
    nav_buttons = []
    total_pages = math.ceil(total_jobs / jobs_per_page)
    
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{category}_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"Page {page}/{total_pages}", callback_data="current_page"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{category}_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data="browse_categories")])
    
    await query.message.edit_text(
        jobs_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def view_job_details(update: Update, context: CallbackContext):
    """Show detailed job view"""
    query = update.callback_query
    await query.answer()
    
    job_id = int(query.data.replace("view_job_", ""))
    
    cursor = db.get_cursor()
    
    # Get job details
    cursor.execute("""
        SELECT j.*, u.username, u.full_name as company_contact, 
               u.phone, u.email, u.user_type
        FROM jobs j
        LEFT JOIN users u ON j.employer_id = u.telegram_id
        WHERE j.id = %s
    """, (job_id,))
    
    job = cursor.fetchone()
    
    if not job:
        await query.message.reply_text("Job not found or has been removed.")
        cursor.close()
        return
    
    # Increment view count
    cursor.execute("UPDATE jobs SET views = views + 1 WHERE id = %s", (job_id,))
    db.connection.commit()
    
    # Check if user has applied
    cursor.execute("""
        SELECT id FROM applications 
        WHERE job_id = %s AND applicant_id = %s
    """, (job_id, update.effective_user.id))
    
    has_applied = cursor.fetchone() is not None
    
    # Check if job is saved
    cursor.execute("""
        SELECT id FROM saved_jobs 
        WHERE job_id = %s AND user_id = %s
    """, (job_id, update.effective_user.id))
    
    is_saved = cursor.fetchone() is not None
    
    cursor.close()
    
    # Format job details
    job_text = f"""
📋 *JOB DETAILS*

*Title:* {job['title']}
*Company:* {job['company'] or 'Not specified'}
*Job ID:* #{job['id']}

*📍 Location:* {job['location'] or 'Not specified'}
*💰 Salary:* {job['salary_range'] or 'Negotiable'}
*⏰ Type:* {Config.JOB_TYPES.get(job['job_type'], 'Full Time')}
*📁 Category:* {job['category'] or 'General'}

*📝 Description:*
{job['description']}

*✅ Requirements:*
{job['requirements'] or 'Not specified'}

*📊 Statistics:*
👁️ {job['views']} views | 📥 {job['applications']} applications
📅 Posted: {job['created_at'].strftime('%B %d, %Y')}
📅 Expires: {job['expires_at'].strftime('%B %d, %Y') if job['expires_at'] else 'Never'}

*👤 Contact Information:*
"""
    
    if job['user_type'] == 'employer':
        if job['company_contact']:
            job_text += f"Contact: {job['company_contact']}\n"
        if job['username']:
            job_text += f"Telegram: @{job['username']}\n"
        if job['phone']:
            job_text += f"Phone: {job['phone']}\n"
        if job['email']:
            job_text += f"Email: {job['email']}\n"
    else:
        job_text += "Contact employer through application\n"
    
    # Create action buttons
    keyboard = []
    
    if not has_applied:
        keyboard.append([InlineKeyboardButton("📨 Apply Now", callback_data=f"apply_job_{job_id}")])
    else:
        keyboard.append([InlineKeyboardButton("✅ Applied", callback_data=f"applied_status_{job_id}")])
    
    if is_saved:
        keyboard.append([InlineKeyboardButton("⭐ Saved", callback_data=f"unsave_job_{job_id}")])
    else:
        keyboard.append([InlineKeyboardButton("⭐ Save Job", callback_data=f"save_job_{job_id}")])
    
    keyboard.append([
        InlineKeyboardButton("🔙 Back", callback_data=f"back_to_list_{job['category']}_1"),
        InlineKeyboardButton("📞 Report", callback_data=f"report_job_{job_id}")
    ])
    
    await query.message.edit_text(
        job_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
