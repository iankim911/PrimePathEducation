import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client

# Test session creation with debug
client = Client()
session_data = {
    'student_name': 'Test Student',
    'grade': '5',
    'academic_rank': 'TOP_50',
    'parent_phone': '010-1234-5678',
    'school_name': 'Test School'
}

print('Testing session creation with data:', json.dumps(session_data, indent=2))
response = client.post('/api/placement/start/', session_data)
print(f'Response status: {response.status_code}')
if response.status_code != 302:
    print(f'Response content: {response.content.decode()[:500]}')
else:
    print(f'Redirect to: {response.url}')