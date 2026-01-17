# Create requirements.txt
echo "python-telegram-bot==20.7
python-dotenv==1.0.0
Flask==3.0.0
requests==2.31.0" > requirements.txt

# Create Procfile
echo "web: python web_dashboard.py
worker: python bot.py" > Procfile

# Push to GitHub, then connect to Railway
