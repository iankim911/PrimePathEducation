"""
Matrix Tab Injection Middleware
Ensures Matrix tab is always present in RoutineTest pages
"""

import re
from django.utils.deprecation import MiddlewareMixin


class MatrixTabInjectionMiddleware(MiddlewareMixin):
    """
    Middleware that injects Matrix tab into navigation if missing
    This is a failsafe to ensure the tab is always visible
    """
    
    def process_response(self, request, response):
        """Process response and inject Matrix tab if needed"""
        
        # Only process RoutineTest pages
        if not request.path.startswith('/RoutineTest/'):
            return response
        
        # Only process HTML responses
        if response.get('Content-Type', '').startswith('text/html'):
            try:
                content = response.content.decode('utf-8')
                
                # Check if navigation exists and Matrix tab is missing
                if 'nav-tabs' in content and 'schedule-matrix' not in content:
                    # Find where to inject (after My Classes & Access)
                    pattern = r'(<a[^>]*>My Classes[^<]*</a>\s*</li>)'
                    
                    matrix_tab_html = '''
                    </li>
                    <!-- INJECTED BY MIDDLEWARE -->
                    <li id="matrix-tab-injected" style="display: flex !important;">
                        <a href="/RoutineTest/schedule-matrix/" 
                           data-nav="exam-assignments"
                           style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%) !important; 
                                  color: white !important; 
                                  font-weight: bold !important; 
                                  border: 2px solid #E65100 !important; 
                                  padding: 12px 20px !important;
                                  display: block !important;">
                           📊 Exam Assignments
                        </a>
                    </li>
                    <li>'''
                    
                    # Try to inject after My Classes
                    new_content = re.sub(pattern, r'\1' + matrix_tab_html, content)
                    
                    if new_content == content:
                        # If pattern didn't match, try simpler injection
                        # Find the Results & Analytics tab
                        pattern2 = r'(<li[^>]*>\s*<a[^>]*>Results[^<]*</a>)'
                        
                        matrix_before_results = '''<li id="matrix-tab-injected" style="display: flex !important;">
                        <a href="/RoutineTest/schedule-matrix/" 
                           data-nav="exam-assignments"
                           style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%) !important; 
                                  color: white !important; 
                                  font-weight: bold !important; 
                                  border: 2px solid #E65100 !important; 
                                  padding: 12px 20px !important;
                                  display: block !important;">
                           📊 Exam Assignments
                        </a>
                    </li>
                    '''
                        
                        new_content = re.sub(pattern2, matrix_before_results + r'\1', content)
                    
                    # Add console log to indicate injection
                    if new_content != content:
                        injection_script = '''
<script>
console.log('%c[MIDDLEWARE] Matrix tab injected into navigation', 'background: #4CAF50; color: white; padding: 3px;');
</script>
</body>'''
                        new_content = new_content.replace('</body>', injection_script)
                        
                        response.content = new_content.encode('utf-8')
                        response['Content-Length'] = len(response.content)
                        
                        print(f"[MATRIX_TAB_MIDDLEWARE] Injected Matrix tab into {request.path}")
                
            except Exception as e:
                # Don't break the response if injection fails
                print(f"[MATRIX_TAB_MIDDLEWARE] Error: {e}")
        
        return response