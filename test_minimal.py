#!/usr/bin/env python3
import requests

url = "http://localhost:9000/feedback-minimal"
data = {"content_id": "test123", "rating": 5, "comment": "works"}

try:
    response = requests.post(url, json=data, timeout=3)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")