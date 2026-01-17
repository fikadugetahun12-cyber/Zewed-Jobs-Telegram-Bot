# bot.py - Main Telegram Bot
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler, ContextTypes
)
from config import BOT_TOKEN, ADMIN_IDS, JOB_CATEGORIES, JOB_TYPES
from database import db
import jobs_data

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CATEGORY, JOB_TYPE, TITLE, COMPANY, LOCATION, SALARY, DESCRIPTION, REQUIREMENTS, CONTACT = range(9)

# ==================== HELPER FUNCTIONS ====================
def format_job(job):
    """Format job details into readable message"""
    job_id, title, company, category, job_type, location, salary, description, requirements, employer_id, contact_email, contact_phone, is_active, created_at, expires_at = job
    
    # Format date
    created_date = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d') if created_at else 'N/A'
    
    # Get category and type names
    category_name = JOB_CATEGORIES.get(category, category.title())
    type_name = JOB_TYPES.get(job_type, job_type.title())
    
    message = f"""
📋 **{title}** 
🏢 **Company:** {company}
📍 **Location:** {location}
💰 **Salary:** {salary}
📁 **Category:** {category_name}
⏰ **Type:** {type_name}
📅 **Posted:** {created_date}

📝 **Description:**
{description}

📋 **Requirements:**
{requirements}

📞 **Contact:** {contact_email} | {contact_phone}
━━━━━━━━━━━━━━━━━━━━
🆔 Job ID: #{job_id}
    """
    return message

def main_menu_keyboard():
    """Main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("🔍 Browse Jobs", callback_data='browse_jobs')],
        [InlineKeyboardButton("🎯 Search Jobs", callback_data='search_jobs')],
        [InlineKeyboardButton("💼 Post a Job", callback_data='post_job')],
        [InlineKeyboardButton("📊 My Applications", callback_data='my_applications')],
        [InlineKeyboardButton("ℹ️ About / Help", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def categories_keyboard(action='browse'):
    """Categories selection keyboard"""
    keyboard = []
    row = []
    for i, (key, value) in enumerate(JOB_CATEGORIES.items()):
        row.append(InlineKeyboardButton(value, callback_data=f'{action}_category_{key}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)

def job_types_keyboard():
    """Job types selection keyboard"""
    keyboard = []
    row = []
    for i, (key, value) in enumerate(JOB_TYPES.items()):
        row.append(InlineKeyboardButton(value, callback_data=f'job_type_{key}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)

# ==================== COMMAND HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued"""
    user = update.effective_user
    
    # Add user to database
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    welcome_message = f"""
🌟 **Welcome to Zewed Jobs Bot, {user.first_name}!** 🌟

Find your dream job or post job opportunities with Ethiopia's leading job platform.

📊 **What you can do:**
• 🔍 Browse jobs by category
• 🎯 Search for specific jobs
• 💼 Post job listings (employers)
• 📝 Apply directly through Telegram
• 📊 Track your applications

👇 **Choose an option below to get started:**
    """
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=main_menu_keyboard(),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
📚 **Zewed Jobs Bot Help**

**Commands:**
/start - Start the bot
/jobs - Browse latest jobs
/search - Search for jobs
/post - Post a job (employers)
/profile - View your profile
/applications - Your job applications
/help - This help message
/about - About Zewed Jobs

**For Employers:**
1. Use /post to create a job listing
2. Fill in job details step by step
3. Your job will be visible to job seekers
4. Receive applications directly

**For Job Seekers:**
1. Browse jobs by category
2. Search for specific positions
3. Apply with your details
4. Track your applications

**Need Help?**
Contact support: support@zewed.com
Visit: www.zewedjobs.com
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About command"""
    about_text = """
🏢 **About Zewed Jobs**

Zewed Jobs is Ethiopia's leading job portal connecting talented professionals with top employers.

**Our Mission:**
To bridge the gap between employers and job seekers in Ethiopia through innovative technology.

**Features:**
✅ Verified job listings
✅ Direct employer connection
✅ Easy application process
✅ Real-time notifications
✅ Career resources

**Contact:**
📧 Email: info@zewedjobs.com
🌐 Website: www.zewedjobs.com
📱 Telegram: @zewed_jobs_bot

**Follow us:**
📘 Facebook: /zewedjobs
🐦 Twitter: @zewedjobs
📸 Instagram: @zewedjobs
    """
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Browse jobs command"""
    await update.message.reply_text(
        "📁 **Select Job Category:**",
        reply_markup=categories_keyboard('browse'),
        parse_mode='Markdown'
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search jobs command"""
    await update.message.reply_text(
        "🔍 **Enter job title, company, or keyword to search:**\n\n"
        "Example: 'software developer', 'marketing', 'Addis Ababa'",
        parse_mode='Markdown'
    )
    return 'SEARCHING'

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search query"""
    keyword = update.message.text
    jobs = db.search_jobs(keyword)
    
    if jobs:
        message = f"🔍 **Found {len(jobs)} jobs for '{keyword}':**\n\n"
        
        # Show first 5 jobs with buttons
        for i, job in enumerate(jobs[:5], 1):
            job_id, title, company, _, _, location, salary, _, _, _, _, _, _, _, _ = job
            message += f"{i}. **{title}** at {company}\n"
            message += f"   📍 {location} | 💰 {salary}\n"
            message += f"   👉 View: /view_{job_id}\n\n"
        
        if len(jobs) > 5:
            message += f"... and {len(jobs) - 5} more jobs. Use /jobs to browse all categories."
        
        keyboard = [
            [InlineKeyboardButton("🔍 Search Again", callback_data='search_jobs')],
            [InlineKeyboardButton("📁 Browse Categories", callback_data='browse_jobs')]
        ]
        
        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ No jobs found for '{keyword}'.\n"
            "Try different keywords or browse categories.",
            reply_markup=categories_keyboard('browse')
        )
    
    return ConversationHandler.END

# ==================== CALLBACK QUERY HANDLERS ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'main_menu':
        await query.edit_message_text(
            "🏠 **Main Menu:**",
            reply_markup=main_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    elif data == 'browse_jobs':
        await query.edit_message_text(
            "📁 **Select Job Category:**",
            reply_markup=categories_keyboard('browse'),
            parse_mode='Markdown'
        )
    
    elif data.startswith('browse_category_'):
        category = data.split('_')[-1]
        jobs = db.get_jobs(category=category, limit=10)
        
        if jobs:
            message = f"📋 **{JOB_CATEGORIES.get(category, category.title())} Jobs**\n\n"
            
            for i, job in enumerate(jobs, 1):
                job_id, title, company, _, _, location, salary, _, _, _, _, _, _, _, _ = job
                message += f"{i}. **{title}** at {company}\n"
                message += f"   📍 {location} | 💰 {salary}\n"
                message += f"   👉 /view_{job_id}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Categories", callback_data='browse_jobs')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]
            ]
            
            await query.edit_message_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                f"❌ No jobs found in {JOB_CATEGORIES.get(category, category.title())} category.\n"
                "Check back later or browse other categories.",
                reply_markup=categories_keyboard('browse')
            )
    
    elif data == 'search_jobs':
        await query.edit_message_text(
            "🔍 **Enter job title, company, or keyword to search:**\n\n"
            "Example: 'software developer', 'marketing', 'Addis Ababa'",
            parse_mode='Markdown'
        )
    
    elif data == 'post_job':
        user = query.from_user
        user_data = db.get_user(user.id)
        
        if user_data and user_data[4]:  # Check if is_employer
            await query.edit_message_text(
                "💼 **Post a New Job**\n\n"
                "Let's create your job listing step by step.\n\n"
                "📝 **First, select job category:**",
                reply_markup=categories_keyboard('post'),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "⚠️ **Employer Registration Required**\n\n"
                "To post jobs, you need to register as an employer.\n\n"
                "Please contact support@zewedjobs.com with:\n"
                "• Your company name\n• Business license (if any)\n• Contact information\n\n"
                "Or use /help for more information.",
                reply_markup=main_menu_keyboard(),
                parse_mode='Markdown'
            )
    
    elif data.startswith('post_category_'):
        category = data.split('_')[-1]
        context.user_data['job_category'] = category
        
        await query.edit_message_text(
            f"✅ Category: {JOB_CATEGORIES.get(category, category.title())}\n\n"
            "⏰ **Now select job type:**",
            reply_markup=job_types_keyboard(),
            parse_mode='Markdown'
        )
    
    elif data.startswith('job_type_'):
        job_type = data.split('_')[-1]
        context.user_data['job_type'] = job_type
        
        await query.edit_message_text(
            f"✅ Type: {JOB_TYPES.get(job_type, job_type.title())}\n\n"
            "📝 **Now enter job title:**\n\n"
            "Example: 'Senior Software Developer'",
            parse_mode='Markdown'
        )
    
    elif data == 'help':
        await help_command(update, context)
    
    elif data == 'my_applications':
        user = query.from_user
        # Get user applications logic here
        await query.edit_message_text(
            "📊 **My Applications**\n\n"
            "Feature coming soon!\n"
            "You'll be able to track all your job applications here.",
            reply_markup=main_menu_keyboard(),
            parse_mode='Markdown'
        )

# ==================== JOB POSTING CONVERSATION ====================
async def post_job_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start job posting conversation"""
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    if not user_data or not user_data[4]:  # Check if is_employer
        await update.message.reply_text(
            "⚠️ You need to be registered as an employer to post jobs.\n"
            "Contact support@zewedjobs.com for employer registration.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "💼 **Post a New Job**\n\n"
        "Let's create your job listing step by step.\n\n"
        "📝 **First, select job category:**",
        reply_markup=categories_keyboard('post'),
        parse_mode='Markdown'
    )
    return CATEGORY

async def receive_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive job category"""
    query = update.callback_query
    await query.answer()
    
    category = query.data.split('_')[-1]
    context.user_data['category'] = category
    
    await query.edit_message_text(
        f"✅ Category: {JOB_CATEGORIES.get(category, category.title())}\n\n"
        "⏰ **Now select job type:**",
        reply_markup=job_types_keyboard()
    )
    return JOB_TYPE

async def receive_job_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive job type"""
    query = update.callback_query
    await query.answer()
    
    job_type = query.data.split('_')[-1]
    context.user_data['job_type'] = job_type
    
    await query.edit_message_text(
        f"✅ Type: {JOB_TYPES.get(job_type, job_type.title())}\n\n"
        "📝 **Now enter job title:**\n\n"
        "Example: 'Senior Software Developer'"
    )
    return TITLE

async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive job title"""
    context.user_data['title'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Title: {update.message.text}\n\n"
        "🏢 **Now enter company name:**\n\n"
        "Example: 'Zewed Tech Solutions'"
    )
    return COMPANY

async def receive_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive company name"""
    context.user_data['company'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Company: {update.message.text}\n\n"
        "📍 **Now enter job location:**\n\n"
        "Example: 'Addis Ababa, Ethiopia' or 'Remote'"
    )
    return LOCATION

async def receive_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive job location"""
    context.user_data['location'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Location: {update.message.text}\n\n"
        "💰 **Now enter salary/compensation:**\n\n"
        "Example: '$1000-1500/month', 'Negotiable', 'As per company scale'"
    )
    return SALARY

async def receive_salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive salary"""
    context.user_data['salary'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Salary: {update.message.text}\n\n"
        "📝 **Now enter job description:**\n\n"
        "Describe the role, responsibilities, and what makes it exciting!"
    )
    return DESCRIPTION

async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive job description"""
    context.user_data['description'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Description saved!\n\n"
        "📋 **Now enter job requirements:**\n\n"
        "List required skills, experience, education, etc."
    )
    return REQUIREMENTS

async def receive_requirements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive job requirements"""
    context.user_data['requirements'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Requirements saved!\n\n"
        "📧 **Finally, enter contact email for applications:**\n\n"
        "Example: 'careers@yourcompany.com'"
    )
    return CONTACT

async def receive_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive contact email and save job"""
    context.user_data['contact_email'] = update.message.text
    context.user_data['contact_phone'] = context.user_data.get('contact_phone', '')
    
    # Add employer ID
    context.user_data['employer_id'] = update.effective_user.id
    
    # Save job to database
    job_id = db.add_job(context.user_data)
    
    # Prepare confirmation message
    confirmation = f"""
🎉 **Job Posted Successfully!** 🎉

📋 **{context.user_data['title']}**
🏢 {context.user_data['company']}
📍 {context.user_data['location']}
💰 {context.user_data['salary']}

Your job is now live and visible to job seekers.
Job ID: #{job_id}

**Next steps:**
1. Share job link: https://t.me/zewed_jobs_bot?start=job_{job_id}
2. Check applications in your dashboard
3. Contact qualified candidates

**To manage this job:**
• View applications: /applications_{job_id}
• Edit job: /edit_{job_id}
• Close job: /close_{job_id}

Thank you for using Zewed Jobs!
    """
    
    await update.message.reply_text(
        confirmation,
        parse_mode='Markdown',
        reply_markup=main_menu_keyboard()
    )
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        "❌ Job posting cancelled.",
        reply_markup=main_menu_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ==================== VIEW JOB HANDLER ====================
async def view_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view job command"""
    try:
        # Extract job ID from command like /view_123
        command = update.message.text
        job_id = int(command.split('_')[1])
        
        job = db.get_job_by_id(job_id)
        
        if job:
            # Format job details
            message = format_job(job)
            
            # Create apply button
            keyboard = [
                [
                    InlineKeyboardButton("📝 Apply Now", callback_data=f'apply_{job_id}'),
                    InlineKeyboardButton("💾 Save Job", callback_data=f'save_{job_id}')
                ],
                [InlineKeyboardButton("🔍 More Jobs", callback_data='browse_jobs')]
            ]
            
            await update.message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Job not found or has been removed.",
                reply_markup=main_menu_keyboard()
            )
    except (IndexError, ValueError):
        await update.message.reply_text(
            "⚠️ Invalid job ID. Please use a valid job link.",
            reply_markup=main_menu_keyboard()
        )

# ==================== ADMIN COMMANDS ====================
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin statistics"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Access denied.")
        return
    
    stats = db.get_stats()
    
    stats_message = f"""
📊 **Admin Statistics**

👥 **Users:** {stats['total_users']}
💼 **Active Jobs:** {stats['active_jobs']}
📝 **Applications:** {stats['total_applications']}
🏢 **Employers:** {stats['total_employers']}

**Quick Actions:**
/announce - Send announcement to all users
/export_jobs - Export all jobs data
/export_users - Export users data
    """
    
    await update.message.reply_text(stats_message, parse_mode='Markdown')

# ==================== MAIN FUNCTION ====================
def main():
    """Start the bot"""
    # Create Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add conversation handler for job posting
    post_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('post', post_job_start)],
        states={
            CATEGORY: [CallbackQueryHandler(receive_category, pattern='^post_category_')],
            JOB_TYPE: [CallbackQueryHandler(receive_job_type, pattern='^job_type_')],
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_company)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_location)],
            SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_salary)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            REQUIREMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_requirements)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_contact)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add search conversation handler
    search_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('search', search)],
        states={
            'SEARCHING': [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('about', about))
    application.add_handler(CommandHandler('jobs', jobs))
    application.add_handler(CommandHandler('admin', admin_stats))
    application.add_handler(MessageHandler(filters.Regex(r'^/view_\d+$'), view_job))
    
    # Add conversation handlers
    application.add_handler(post_conv_handler)
    application.add_handler(search_conv_handler)
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Add message handler for unknown commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_command))
    
    # Start the Bot
    print("🤖 Zewed Jobs Bot is starting...")
    print("📊 Database initialized...")
    print("🚀 Bot is running. Press Ctrl+C to stop.")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
