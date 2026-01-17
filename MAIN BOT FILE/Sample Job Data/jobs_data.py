# jobs_data.py - Sample job listings
import json
from datetime import datetime, timedelta

SAMPLE_JOBS = [
    {
        "title": "Senior Software Developer",
        "company": "Zewed Tech Solutions",
        "category": "tech",
        "job_type": "full",
        "location": "Addis Ababa, Ethiopia",
        "salary": "ETB 50,000 - 80,000/month",
        "description": "We're looking for an experienced software developer to join our growing team. You'll work on cutting-edge projects using Python, Django, and React.",
        "requirements": "• 3+ years experience with Python/Django\n• Strong knowledge of React.js\n• Experience with PostgreSQL\n• Bachelor's in Computer Science or related\n• Excellent problem-solving skills",
        "contact_email": "careers@zewedtech.com",
        "contact_phone": "+251 911 234 567"
    },
    {
        "title": "Marketing Manager",
        "company": "EthioGrowth Consulting",
        "category": "business",
        "job_type": "full",
        "location": "Addis Ababa",
        "salary": "ETB 40,000 - 60,000/month",
        "description": "Lead our marketing team and develop strategies to increase brand awareness and drive business growth.",
        "requirements": "• 5+ years marketing experience\n• Digital marketing expertise\n• Team management skills\n• Bachelor's in Marketing or related",
        "contact_email": "hr@ethiogrowth.com",
        "contact_phone": "+251 922 345 678"
    },
    {
        "title": "Graphic Designer",
        "company": "Creative Ethiopia",
        "category": "creative",
        "job_type": "remote",
        "location": "Remote",
        "salary": "ETB 30,000 - 45,000/month",
        "description": "Create stunning visual designs for digital and print media. Work with clients across various industries.",
        "requirements": "• Proficiency in Adobe Creative Suite\n• Portfolio of previous work\n• 2+ years design experience\n• Creative thinking and attention to detail",
        "contact_email": "design@creativeethiopia.com",
        "contact_phone": "+251 933 456 789"
    },
    {
        "title": "Data Analyst",
        "company": "Data Insights Ethiopia",
        "category": "tech",
        "job_type": "full",
        "location": "Addis Ababa",
        "salary": "ETB 45,000 - 65,000/month",
        "description": "Analyze large datasets to provide insights and support data-driven decision making.",
        "requirements": "• SQL and Python/R experience\n• Statistical analysis skills\n• Data visualization expertise\n• 2+ years in data analysis",
        "contact_email": "jobs@dataethiopia.com",
        "contact_phone": "+251 944 567 890"
    },
    {
        "title": "Medical Doctor",
        "company": "St. Mary Hospital",
        "category": "medical",
        "job_type": "full",
        "location": "Addis Ababa",
        "salary": "ETB 60,000 - 90,000/month",
        "description": "Provide medical care to patients in our modern healthcare facility.",
        "requirements": "• Medical degree and license\n• 3+ years clinical experience\n• Specialization preferred\n• Excellent bedside manner",
        "contact_email": "recruitment@stmaryhospital.com",
        "contact_phone": "+251 955 678 901"
    }
]

def populate_sample_jobs(db):
    """Populate database with sample jobs"""
    for job_data in SAMPLE_JOBS:
        # Add employer ID (use 1 as sample employer)
        job_data['employer_id'] = 1
        job_data['expires_at'] = datetime.now().timestamp() + 90*24*60*60  # 90 days
        db.add_job(job_data)
    
    print(f"✅ Added {len(SAMPLE_JOBS)} sample jobs to database")
