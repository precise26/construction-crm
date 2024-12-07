import requests
import json
from datetime import datetime

# API endpoint URL
API_URL = "http://127.0.0.1:8000/api/website-form"

def test_crm_api():
    # Test data
    test_data = {
        'name': 'Test User',
        'email': f'test{datetime.now().timestamp()}@example.com',  # Unique email each time
        'phone': '123-456-7890',
        'message': 'This is a test submission',
        'project_type': 'Test Project',
        'address': '123 Test St',
        'source': 'API Test'
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        # Make the request
        response = requests.post(API_URL, json=test_data, headers=headers)
        
        # Print response details
        print(f'Status Code: {response.status_code}')
        print('Response Headers:', json.dumps(dict(response.headers), indent=2))
        print('Response Body:', json.dumps(response.json(), indent=2))
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        return False

if __name__ == '__main__':
    print('Testing CRM API...')
    success = test_crm_api()
    print(f'\nTest {"successful" if success else "failed"}!')