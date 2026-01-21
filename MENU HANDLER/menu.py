from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

def get_main_menu():
    """Create main menu keyboard"""
    return ReplyKeyboardMarkup([
        ["🔍 Browse Jobs", "📝 Post Job"],
        ["👤 My Profile", "📊 Statistics"],
        ["ℹ️ About", "⚙️ Settings"]
    ], resize_keyboard=True)

async def start(update: Update, context: CallbackContext):
    """Handle /start command"""
    user = update.effective_user
    welcome_text = f"""
👋 Welcome to *Zewed Jobs* {user.first_name}!

Find your dream job or hire the best talent!

*Available Commands:*
🔍 /jobs - Browse available jobs
📝 /post - Post a new job
👤 /profile - Manage your profile
⚙️ /settings - Bot settings

Or use the menu below:
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def handle_menu(update: Update, context: CallbackContext):
    """Handle menu button clicks"""
    text = update.message.text
    
    if text == "🔍 Browse Jobs":
        await update.message.reply_text("Loading available jobs...\n\n*Feature coming soon!*", parse_mode="Markdown")
    
    elif text == "📝 Post Job":
        await update.message.reply_text("To post a job:\n\n1. Job title\n2. Description\n3. Requirements\n4. Salary range\n\n*Use /post to start*", parse_mode="Markdown")
    
    elif text == "👤 My Profile":
        await update.message.reply_text("Profile features:\n\n• Edit resume\n• Saved jobs\n• Application history\n\n*Use /profile to manage*", parse_mode="Markdown")
    
    elif text == "📊 Statistics":
        await update.message.reply_text("📈 *Zewed Jobs Stats*\n\n• 500+ jobs posted\n• 2000+ candidates\n• 95% satisfaction rate\n\n*More stats coming soon!*", parse_mode="Markdown")
    
    elif text == "ℹ️ About":
        await update.message.reply_text("🤖 *Zewed Jobs Bot*\n\nConnecting employers with job seekers in Ethiopia!\n\nFeatures:\n• Job postings\n• Resume database\n• Direct applications\n• Notifications\n\n*Version 1.0*", parse_mode="Markdown")
    
    elif text == "⚙️ Settings":
        await update.message.reply_text("Settings:\n\n• Notification preferences\n• Profile visibility\n• Language\n• Contact info\n\n*Use /settings to configure*", parse_mode="Markdown")
