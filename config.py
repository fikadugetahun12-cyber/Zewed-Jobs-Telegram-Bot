# config.py - Configuration file

# Bot Token (Replace with yours or use environment variable)
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8282317478:AAGhFXcetc1heO_YELwE0IKylZd30jDUuXo")
ADMIN_IDS = [123456789]  # Add your Telegram ID here

# Database Configuration
DATABASE_NAME = "zewed_jobs.db"

# Job Categories
JOB_CATEGORIES = {
    "tech": "💻 Technology",
    "business": "📊 Business",
    "creative": "🎨 Creative", 
    "medical": "🏥 Medical",
    "engineering": "⚙️ Engineering",
    "education": "📚 Education"
}

# Job Types
JOB_TYPES = {
    "full": "Full-time",
    "part": "Part-time", 
    "remote": "Remote",
    "intern": "Internship",
    "contract": "Contract"
}
