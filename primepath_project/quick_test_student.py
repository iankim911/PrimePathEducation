import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, '.')
django.setup()

from django.test import Client
from primepath_routinetest.models import StudentSession, Exam

# Quick test of student interface
client = Client()
response = client.get('/RoutineTest/start/')
print(f'Start page status: {response.status_code}')

# Try getting a session
exam = Exam.objects.filter(exam_type='REVIEW').first()
if exam:
    session = StudentSession.objects.create(
        exam=exam,
        student_name='Quick Test',
        phone='1234567890',
        grade=7
    )
    response = client.get(f'/RoutineTest/session/{session.id}/')
    print(f'Session page status: {response.status_code}')
    if response.status_code != 200:
        print('Error:', response.content[:500].decode('utf-8'))
    else:
        print('Session page works!')
        # Check content
        content = response.content.decode('utf-8')
        if 'timer' in content.lower():
            print('✅ Timer found')
        if 'submit' in content.lower():
            print('✅ Submit button found')
else:
    print('No exam found for testing')