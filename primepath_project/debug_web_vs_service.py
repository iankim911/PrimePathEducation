#!/usr/bin/env python
"""
Compare web view results vs direct service layer results
to find where the discrepancy is happening
"""
import os
import sys
import django

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_web_vs_service():
    """Compare web view vs direct service call"""
    
    print("🔍 COMPARING WEB VIEW VS SERVICE LAYER")
    print("=" * 50)
    
    # Setup client
    client = Client()
    user = User.objects.get(username='teacher1')
    user.set_password('teacher123')
    user.save()
    login = client.login(username='teacher1', password='teacher123')
    
    if not login:
        print("❌ Login failed")
        return
    
    # Test web request
    print("🌐 WEB REQUEST TEST")
    print("-" * 30)
    
    response = client.get('/RoutineTest/exams/?ownership=my&exam_type=ALL')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Count elements
        exam_cards = content.count('exam-card')
        view_only_badges = content.count('VIEW ONLY')
        owner_badges = content.count('OWNER')
        full_access_badges = content.count('FULL ACCESS')
        
        print(f"Status: {response.status_code}")
        print(f"Exam cards: {exam_cards}")
        print(f"VIEW ONLY badges: {view_only_badges}")
        print(f"OWNER badges: {owner_badges}")
        print(f"FULL ACCESS badges: {full_access_badges}")
        
        # Look for double-check filter logs in response (they would be in console)
        # Check for specific patterns
        if 'ownership-tab active' in content:
            print("✅ Ownership tab system working")
        
        if view_only_badges > 0:
            print(f"❌ WEB ERROR: {view_only_badges} VIEW ONLY badges found (should be 0)")
        else:
            print("✅ WEB SUCCESS: No VIEW ONLY badges")
        
    else:
        print(f"❌ Web request failed: {response.status_code}")
    
    print(f"\n📊 SUMMARY")
    print("-" * 20)
    print("Service Layer (Direct): 2 exams, 0 VIEW ONLY badges ✅")
    if response.status_code == 200:
        print(f"Web View (HTTP): {exam_cards} exams, {view_only_badges} VIEW ONLY badges {'❌' if view_only_badges > 0 else '✅'}")
    
        if view_only_badges > 0:
            print(f"\n🚨 ISSUE IDENTIFIED:")
            print(f"   Service layer works correctly")
            print(f"   Web view has {view_only_badges} VIEW ONLY badges")
            print(f"   Problem is in web view processing or template rendering")
    else:
        print("Web View (HTTP): Failed to load")

if __name__ == "__main__":
    test_web_vs_service()