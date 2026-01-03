import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
import json

client = Client()
resp = client.get('/metal-rate/?state=karnataka')
try:
    data = json.loads(resp.content.decode('utf-8'))
    print(json.dumps(data, indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")
    print(f"Response: {resp.content.decode('utf-8', errors='replace')}")
