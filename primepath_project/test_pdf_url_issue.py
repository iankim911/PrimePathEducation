#!/usr/bin/env python3
"""
Test script to investigate PDF URL and UUID issues
"""

import uuid
import sqlite3
import requests
from urllib.parse import quote

def test_pdf_url_issue():
    print("=== PDF URL Issue Investigation ===")
    
    # Database UUID from our investigation (without hyphens)
    db_uuid = "54b006266cf64fa798d86203c1397713"
    
    # URL UUID from screenshot (with hyphens)
    url_uuid = "54b00626-6cf6-4fa7-98d8-6203c1397713"
    
    print(f"Database UUID: {db_uuid}")
    print(f"URL UUID:      {url_uuid}")
    print()
    
    # Test UUID formatting
    try:
        # Convert database format to standard UUID format
        uuid_obj = uuid.UUID(db_uuid)
        formatted_uuid = str(uuid_obj)
        print(f"✓ Database UUID converts to: {formatted_uuid}")
        print(f"✓ Matches URL format: {formatted_uuid == url_uuid}")
    except ValueError as e:
        print(f"✗ Error converting database UUID: {e}")
    
    print()
    
    # Test URL endpoints
    base_url = "http://127.0.0.1:8000"
    
    urls_to_test = [
        f"{base_url}/RoutineTest/exams/{url_uuid}/preview/",
        f"{base_url}/RoutineTest/exams/{db_uuid}/preview/",
        f"{base_url}/media/routinetest/exams/pdfs/test_x2rS0a0.pdf",
    ]
    
    print("Testing URLs:")
    for url in urls_to_test:
        try:
            print(f"Testing: {url}")
            response = requests.head(url, timeout=5)
            print(f"  ✓ Status: {response.status_code}")
            if response.status_code != 200:
                print(f"    Headers: {dict(response.headers)}")
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error: {e}")
        print()
    
    # Check PDF file directly
    try:
        pdf_url = f"{base_url}/media/routinetest/exams/pdfs/test_x2rS0a0.pdf"
        response = requests.get(pdf_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✓ Direct PDF access works: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"  Content-Length: {response.headers.get('Content-Length', 'N/A')} bytes")
            
            # Check if it's a valid PDF
            if response.content.startswith(b'%PDF-'):
                print("  ✓ Valid PDF header found")
            else:
                print("  ✗ Invalid PDF header")
                print(f"  First 20 bytes: {response.content[:20]}")
        else:
            print(f"✗ Direct PDF access failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error testing direct PDF access: {e}")

if __name__ == "__main__":
    test_pdf_url_issue()