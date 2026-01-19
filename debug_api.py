import requests
import json

url = "http://127.0.0.1:8000/init_session"
data = {
    "username": "debug_user",
    "grade_level": 10,
    "location": "New Hampshire",
    "learning_style": "Visual"
}

try:
    print(f"Sending: {json.dumps(data)}")
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
