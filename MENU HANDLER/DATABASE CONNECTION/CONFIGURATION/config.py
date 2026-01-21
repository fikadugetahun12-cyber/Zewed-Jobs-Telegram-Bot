import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
    
    # Database
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    
    # Job categories
    JOB_CATEGORIES = [
        "💼 IT & Software",
        "🏥 Healthcare",
        "🏦 Finance & Banking",
        "📚 Education",
        "🎨 Design & Creative",
        "📊 Marketing & Sales",
        "🔧 Engineering",
        "👔 Management",
        "🍴 Hospitality",
        "🚚 Logistics",
        "⚖️ Legal",
        "🔬 Science & Research",
        "📱 Customer Service",
        "🏢 Administration",
        "🌾 Agriculture",
        "🏗️ Construction",
        "🎬 Media & Entertainment",
        "💄 Beauty & Fashion",
        "🚗 Automotive",
        "🏪 Retail"
    ]
    
    # Job types
    JOB_TYPES = {
        "full_time": "Full Time",
        "part_time": "Part Time",
        "contract": "Contract",
        "remote": "Remote",
        "internship": "Internship"
    }
