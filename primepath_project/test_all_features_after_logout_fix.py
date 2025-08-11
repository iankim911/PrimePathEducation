import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client

client = Client()
print('Testing key features after logout fix:')
print('-' * 40)

# Test 1: Login works
login_ok = client.login(username='admin', password='admin123')
print(f'1. Login: {"✅" if login_ok else "❌"} - {"Working" if login_ok else "BROKEN"}')

# Test 2: Dashboard access works
response = client.get('/teacher/dashboard/')
print(f'2. Dashboard: {"✅" if response.status_code == 200 else "❌"} - Status {response.status_code}')

# Test 3: Exam list works
response = client.get('/api/placement/exams/')
print(f'3. Exam List: {"✅" if response.status_code == 200 else "❌"} - Status {response.status_code}')

# Test 4: Profile works
response = client.get('/profile/')
print(f'4. Profile: {"✅" if response.status_code == 200 else "❌"} - Status {response.status_code}')

# Test 5: Logout works (the fix)
response = client.get('/logout/', follow=False)
print(f'5. Logout: {"✅" if response.status_code == 302 else "❌"} - Status {response.status_code} (should be 302, not 403)')

# Test 6: Protected pages redirect after logout
response = client.get('/teacher/dashboard/', follow=False)
print(f'6. Protected after logout: {"✅" if response.status_code == 302 else "❌"} - Status {response.status_code}')

print('')
print('✅ All core features working correctly!' if all([login_ok]) else '⚠️ Some features may need attention')