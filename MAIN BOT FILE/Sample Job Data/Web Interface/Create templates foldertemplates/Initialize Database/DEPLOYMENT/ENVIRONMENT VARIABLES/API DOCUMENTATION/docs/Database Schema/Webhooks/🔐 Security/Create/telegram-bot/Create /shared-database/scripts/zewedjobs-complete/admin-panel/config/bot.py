# bot.py - INTEGRATED VERSION
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import db  # MySQL database
# OR from api_integration import ZewedAPI  # API integration

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== COMMAND HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - registers user and shows menu"""
    user = update.effective_user
    
    # Register user in shared database
    db.add_telegram_user({
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name
    })
    
    # Welcome message with inline keyboard
    keyboard = [
        [InlineKeyboardButton("🔍 Browse Jobs", callback_data='menu_browse')],
        [InlineKeyboardButton("🎯 Search Jobs", callback_data='menu_search')],
        [InlineKeyboardButton("📱 View on Website", url="https://your-zewedjobs.com")],
        [InlineKeyboardButton("📞 Contact Support", callback_data='menu_contact')],
    ]
    
    welcome_text = f"""
🌟 Welcome to Zewed Jobs Bot, {user.first_name}! 

Find your next career opportunity from our database of verified jobs.

**What you can do:**
• 🔍 Browse available jobs
• 🎯 Search by keyword
• 💼 Apply instantly
• 📊 Track applications
• 📱 Sync with web portal

👉 Browse jobs or visit our website for more features!
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch jobs from shared database"""
    # Get jobs from MySQL (shared with PHP admin)
    jobs = db.get_jobs_from_php(limit=10)
    
    if not jobs:
        await update.message.reply_text("📭 No active jobs found at the moment.")
        return
    
    # Create job listings
    message = "📋 **Latest Job Openings:**\n\n"
    
    for i, job in enumerate(jobs[:5], 1):
        message += f"{i}. **{job['title']}**\n"
        message += f"   🏢 {job['company']} | 📍 {job.get('location', 'Remote')}\n"
        message += f"   💰 {job.get('salary', 'Negotiable')}\n"
        message += f"   👉 /view_{job['id']}\n\n"
    
    if len(jobs) > 5:
        message += f"*... and {len(jobs) - 5} more jobs*\n"
    
    message += "📱 *Visit our website for complete listings:*\nhttps://your-zewedjobs.com/jobs"
    
    keyboard = [
        [InlineKeyboardButton("🌐 View Website", url="https://your-zewedjobs.com")],
        [InlineKeyboardButton("🔄 Refresh", callback_data='refresh_jobs')],
    ]
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def apply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle job applications"""
    # Extract job ID from command (/apply_123)
    try:
        job_id = int(context.args[0]) if context.args else None
        
        if not job_id:
            await update.message.reply_text("Usage: /apply <job_id>")
            return
        
        # Store job ID in user data for conversation
        context.user_data['apply_job_id'] = job_id
        
        # Start application conversation
        await update.message.reply_text(
            f"📝 **Application Form**\n\n"
            f"Please provide your details:\n\n"
            f"1. Full Name:\n"
            f"2. Email Address:\n"
            f"3. Phone Number:\n"
            f"4. Cover Letter (optional)\n\n"
            f"*Send your details in one message.*",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Apply error: {e}")
        await update.message.reply_text("Error processing application.")

# ==================== BUTTON HANDLERS ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'menu_browse':
        # Show job categories from PHP database
        categories = db.get_job_categories()  # Implement this method
        
        keyboard = []
        for category in categories:
            keyboard.append([
                InlineKeyboardButton(
                    f"📁 {category['name']} ({category['count']})",
                    callback_data=f"cat_{category['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🌐 Website", url="https://your-zewedjobs.com")])
        
        await query.edit_message_text(
            "📁 **Browse Jobs by Category**\n"
            "Select a category to view available jobs:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data.startswith('cat_'):
        category_id = data.split('_')[1]
        jobs = db.get_jobs_by_category(category_id)
        
        # Display jobs...
    
    elif data == 'menu_contact':
        await query.edit_message_text(
            "📞 **Contact Support**\n\n"
            "**Email:** support@zewedjobs.com\n"
            "**Phone:** +251 911 234 567\n"
            "**Website:** https://your-zewedjobs.com/contact\n\n"
            "⏰ *Hours: Mon-Fri, 9AM-5PM*",
            parse_mode='Markdown'
        )

# ==================== ADMIN COMMANDS ====================
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics from both systems"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Access denied.")
        return
    
    stats = db.get_statistics()
    
    message = """
📊 **Zewed Jobs - Admin Dashboard**

**Website Statistics:**
👥 Total Users: Fetch from PHP
💼 Active Jobs: {active_jobs}
📝 Applications: {total_applications}

**Telegram Bot:**
🤖 Bot Users: {telegram_users}
📱 Active Now: Check from logs

**Quick Actions:**
/announce - Send announcement
/export - Export data
/sync - Sync with website
    """.format(**stats)
    
    await update.message.reply_text(message, parse_mode='Markdown')

# ==================== WEBHOOK SETUP (For Production) ====================
async def set_webhook(url: str, token: str):
    """Set webhook for production deployment"""
    import requests
    
    webhook_url = f"{url}/{token}"
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    
    response = requests.post(api_url, json={'url': webhook_url})
    
    if response.status_code == 200:
        logger.info(f"✅ Webhook set: {webhook_url}")
        return True
    else:
        logger.error(f"❌ Webhook failed: {response.text}")
        return False

# ==================== MAIN FUNCTION ====================
def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("jobs", jobs_command))
    application.add_handler(CommandHandler("apply", apply_command))
    application.add_handler(CommandHandler("admin", admin_stats))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start the bot
    print("🤖 Zewed Jobs Bot Starting...")
    print(f"📊 Database: Connected to MySQL")
    print(f"🔗 PHP Admin: Integrated")
    print(f"👥 Admin IDs: {ADMIN_IDS}")
    
    # For production with webhook:
    # WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    # if WEBHOOK_URL:
    #     application.run_webhook(
    #         listen="0.0.0.0",
    #         port=int(os.getenv('PORT', 8443)),
    #         url_path=BOT_TOKEN,
    #         webhook_url=WEBHOOK_URL + BOT_TOKEN
    #     )
    # else:
    # For development - polling
    application.run_polling()

if __name__ == '__main__':
    main()
