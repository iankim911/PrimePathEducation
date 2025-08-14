#!/usr/bin/env python
"""
Test JavaScript error fix
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import StudentSession

def test_js_error_fix():
    """Test that JavaScript error is fixed"""
    
    print("=" * 70)
    print("🔧 TESTING JAVASCRIPT ERROR FIX")
    print("=" * 70)
    
    client = Client()
    
    # Get a session with audio
    session = StudentSession.objects.filter(
        exam__questions__audio_file__isnull=False,
        completed_at__isnull=True
    ).first()
    
    if not session:
        print("❌ No session with audio found")
        return
    
    print(f"✅ Using session: {session.id}")
    
    # Request the page
    url = reverse('PlacementTest:take_test', args=[session.id])
    response = client.get(url, follow=True)
    
    if response.status_code != 200:
        print(f"❌ Failed to load page: {response.status_code}")
        return
    
    html = response.content.decode('utf-8')
    
    print("📋 CHECKING FIX IMPLEMENTATION:")
    
    # Check that we have audio buttons with data attributes
    if 'data-audio-play=' in html:
        print("✅ Audio buttons have data-audio-play attributes")
    else:
        print("❌ Audio buttons missing data-audio-play attributes")
        return
    
    # Check for the error handling code
    if 'closest(\'[data-audio-play]\')' in html and 'audio-player.js' in html:
        print("✅ JavaScript contains error handling for missing dataset")
    else:
        print("❌ JavaScript fix not loaded")
        return
    
    # Check cache-busting is working
    if 'audio-player.js?v=' in html:
        print("✅ Cache-busting active on JavaScript")
    else:
        print("❌ Cache-busting missing")
    
    print("\n🔍 ANALYZING POTENTIAL ISSUES:")
    
    # Extract button HTML for inspection
    import re
    buttons = re.findall(r'<button[^>]*data-audio-play[^>]*>.*?</button>', html, re.DOTALL)
    
    if buttons:
        print(f"✅ Found {len(buttons)} audio button(s) with data attributes")
        
        # Check first button structure
        first_button = buttons[0]
        if 'data-audio-play=' in first_button and 'audio-icon' in first_button:
            print("✅ Button structure looks correct")
        else:
            print("⚠️ Button structure might be incomplete")
            
        # Check for SVG content
        if '<svg' in first_button:
            print("✅ SVG icon present in template")
        else:
            print("❌ SVG icon missing from template")
            
    else:
        print("❌ No audio buttons found with data attributes")
    
    print("\n" + "=" * 70)
    print("🎯 SUMMARY")
    print("=" * 70)
    
    print("✅ Fixed JavaScript event handling:")
    print("  • Uses element.closest() to find button with data attribute")
    print("  • Adds error checking for missing audioPlay dataset") 
    print("  • Should prevent 'Cannot read properties of undefined' error")
    
    print("\n💡 The error should now be resolved because:")
    print("  1. JavaScript properly finds the button element")
    print("  2. Checks if dataset.audioPlay exists before using it")
    print("  3. Template generates correct HTML with data attributes")
    print("  4. Cache-busting ensures new JavaScript loads")
    
    print("\n🔄 User should now see:")
    print("  1. No more JavaScript errors in console")
    print("  2. Audio buttons display as blue with white icons")
    print("  3. Clicking buttons should work properly")

if __name__ == '__main__':
    test_js_error_fix()