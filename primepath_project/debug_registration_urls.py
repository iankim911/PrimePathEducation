#!/usr/bin/env python3
"""
Debug script to understand why registration URLs are not loading
"""

import os
import sys

# Add the project path and parent directory
project_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project'
sys.path.insert(0, project_path)
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

def debug_registration_urls():
    print("=" * 80)
    print("DEBUGGING REGISTRATION URL LOADING")
    print("=" * 80)
    
    # Step 1: Check if the registration module can be imported
    try:
        import core.urls_registration
        print("✅ core.urls_registration module imports successfully")
        print(f"   Module path: {core.urls_registration.__file__}")
        
        # Check app_name
        if hasattr(core.urls_registration, 'app_name'):
            print(f"✅ app_name found: '{core.urls_registration.app_name}'")
        else:
            print("❌ app_name not found in registration URLs")
        
        # Check urlpatterns
        if hasattr(core.urls_registration, 'urlpatterns'):
            print(f"✅ urlpatterns found: {len(core.urls_registration.urlpatterns)} patterns")
            for pattern in core.urls_registration.urlpatterns:
                print(f"   - {pattern.pattern} (name: {getattr(pattern, 'name', 'unnamed')})")
        else:
            print("❌ urlpatterns not found in registration URLs")
        
    except ImportError as e:
        print(f"❌ Cannot import core.urls_registration: {e}")
        return False
    except Exception as e:
        print(f"❌ Error with core.urls_registration: {e}")
        return False
    
    # Step 2: Check if core.urls can be imported
    try:
        import core.urls
        print("✅ core.urls module imports successfully")
        
        # Check if registration patterns are included
        if hasattr(core.urls, 'urlpatterns'):
            print(f"✅ core.urls has {len(core.urls.urlpatterns)} patterns")
            
            # Look for include patterns
            include_patterns = []
            for pattern in core.urls.urlpatterns:
                if hasattr(pattern, 'url_patterns') or 'include' in str(type(pattern)):
                    include_patterns.append(pattern)
            
            print(f"🔍 Found {len(include_patterns)} include patterns in core.urls")
            for pattern in include_patterns:
                print(f"   - {pattern}")
        
    except ImportError as e:
        print(f"❌ Cannot import core.urls: {e}")
        return False
    except Exception as e:
        print(f"❌ Error with core.urls: {e}")
        return False
    
    # Step 3: Test URL resolution directly
    try:
        from django.urls import get_resolver
        from django.conf import settings
        
        print(f"\n🔍 Testing Django URL resolution...")
        resolver = get_resolver()
        print(f"✅ Got URL resolver")
        
        # Check available namespaces
        if hasattr(resolver, 'namespace_dict'):
            namespaces = list(resolver.namespace_dict.keys())
            print(f"🔍 Available namespaces: {namespaces}")
        elif hasattr(resolver, '_namespace_dict'):
            namespaces = list(resolver._namespace_dict.keys())
            print(f"🔍 Available namespaces: {namespaces}")
        else:
            print("⚠️ Cannot find namespace dict in resolver")
        
        # Try to resolve core URLs
        try:
            from django.urls import reverse
            
            # Test some core URLs
            test_urls = [
                'core:dashboard',
                'core:login',  
                'admin:index',
            ]
            
            print(f"\n🧪 Testing some known URLs:")
            for url_name in test_urls:
                try:
                    url = reverse(url_name)
                    print(f"✅ {url_name}: {url}")
                except Exception as e:
                    print(f"❌ {url_name}: {e}")
        
        except Exception as e:
            print(f"❌ Error testing URL reversal: {e}")
    
    except Exception as e:
        print(f"❌ Error getting URL resolver: {e}")
        return False
    
    # Step 4: Manual check of what's in the main URLConf
    try:
        print(f"\n🔍 Checking main URLConf...")
        from django.conf import settings
        print(f"✅ ROOT_URLCONF: {settings.ROOT_URLCONF}")
        
        # Import the main URLConf
        import importlib
        main_urls = importlib.import_module(settings.ROOT_URLCONF)
        
        print(f"✅ Main URLConf loaded, {len(main_urls.urlpatterns)} patterns")
        
        # Look for core patterns
        for i, pattern in enumerate(main_urls.urlpatterns):
            pattern_str = str(pattern)
            if 'core' in pattern_str.lower() or 'include' in pattern_str:
                print(f"   Pattern {i}: {pattern_str}")
    
    except Exception as e:
        print(f"❌ Error checking main URLConf: {e}")
    
    return True

if __name__ == "__main__":
    print("🔍 Starting Registration URL Debug...")
    debug_registration_urls()
    print("\n" + "=" * 80)