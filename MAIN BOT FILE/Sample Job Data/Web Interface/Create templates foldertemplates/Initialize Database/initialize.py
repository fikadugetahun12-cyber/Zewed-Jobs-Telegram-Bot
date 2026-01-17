# initialize.py
from database import db
from jobs_data import populate_sample_jobs

print("📊 Initializing Zewed Jobs Database...")
print("✅ Database tables created")

# Add sample jobs
populate_sample_jobs(db)
print("✅ Sample jobs added")

# Show stats
stats = db.get_stats()
print(f"\n📈 Initial Stats:")
print(f"   👥 Users: {stats['total_users']}")
print(f"   💼 Jobs: {stats['active_jobs']}")
print(f"   📝 Applications: {stats['total_applications']}")
print(f"   🏢 Employers: {stats['total_employers']}")

print("\n🚀 Setup complete! Run 'python bot.py' to start the bot.")
