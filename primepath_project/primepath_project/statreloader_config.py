"""
Django Server Configuration for StatReloader stability
Add this to your settings file or create as a separate module
"""

import os
import sys

# Disable auto-reload in development if having issues
if 'runserver' in sys.argv:
    # Option 1: Use StatReloader with increased checks
    DJANGO_AUTORELOAD_TYPE = 'stat'
    
    # Option 2: Disable autoreload completely (most stable)
    # os.environ['DJANGO_AUTORELOAD'] = 'false'
    
    # Option 3: Use WatchmanReloader if installed (best option)
    # DJANGO_AUTORELOAD_TYPE = 'watchman'

# Increase file watcher limits
if sys.platform == 'darwin':
    # macOS specific settings
    import resource
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (10240, 10240))
    except:
        pass

# Add to your settings.py:
# from . import statreloader_config  # noqa
