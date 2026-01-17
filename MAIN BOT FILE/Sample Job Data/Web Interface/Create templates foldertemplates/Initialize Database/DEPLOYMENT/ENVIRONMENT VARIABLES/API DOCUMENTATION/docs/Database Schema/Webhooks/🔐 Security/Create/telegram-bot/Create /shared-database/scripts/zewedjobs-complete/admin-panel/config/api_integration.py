# api_integration.py - Connect to PHP Admin Panel via API
import requests
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ZewedAPI:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
    
    def get_jobs(self, category: str = None, page: int = 1) -> List[Dict]:
        """Fetch jobs from PHP admin panel API"""
        try:
            params = {'page': page}
            if category:
                params['category'] = category
            
            response = self.session.get(
                f"{self.base_url}/api/jobs",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"API Error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch jobs: {e}")
            return []
    
    def submit_application(self, application_data: Dict) -> bool:
        """Submit application through PHP API"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/applications",
                json=application_data,
                timeout=10
            )
            
            return response.status_code == 201
            
        except Exception as e:
            logger.error(f"Failed to submit application: {e}")
            return False
    
    def get_job_details(self, job_id: int) -> Optional[Dict]:
        """Get specific job details"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/jobs/{job_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job details: {e}")
            return None

# Usage in your bot
api = ZewedAPI(
    base_url="https://your-zewedjobs.com/admin-panel",
    api_key="your_api_key_here"
)
