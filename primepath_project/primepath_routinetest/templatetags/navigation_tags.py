"""
Navigation Template Tags for RoutineTest
Forces correct navigation rendering with Matrix tab
"""

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
import logging

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def render_routinetest_navigation(context):
    """
    Force renders the RoutineTest navigation with all tabs including Matrix
    This bypasses any caching issues and ensures correct display
    """
    request = context.get('request')
    user = context.get('user')
    is_head_teacher = context.get('is_head_teacher', False)
    
    # Get current URL name for active tab highlighting
    current_url_name = ''
    if request and hasattr(request, 'resolver_match') and request.resolver_match:
        current_url_name = request.resolver_match.url_name or ''
    
    # Log navigation rendering
    logger.info(f"[NAVIGATION_TAG] Rendering navigation for URL: {current_url_name}")
    print(f"[NAVIGATION_TAG] Force rendering navigation with Matrix tab")
    
    # Build navigation HTML
    nav_items = [
        {
            'url': reverse('RoutineTest:index'),
            'label': 'Dashboard',
            'data_nav': 'dashboard',
            'active': current_url_name == 'index'
        },
        {
            'url': reverse('RoutineTest:create_exam'),
            'label': 'Upload Exam',
            'data_nav': 'upload-exam',
            'active': current_url_name == 'create_exam'
        },
        {
            'url': reverse('RoutineTest:exam_list'),
            'label': 'Answer Keys',
            'data_nav': 'answer-keys',
            'active': current_url_name in ['exam_list', 'preview_exam', 'edit_exam']
        },
        {
            'url': reverse('RoutineTest:classes_exams_unified'),
            'label': '🎓 Classes & Exams',
            'data_nav': 'classes-exams',
            'active': current_url_name in ['classes_exams_unified', 'my_classes', 'schedule_matrix', 'matrix_cell_detail'],
            'special_style': 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; font-weight: bold !important; border: 2px solid #667eea !important; padding: 12px 20px !important;',
            'id': 'unified-tab-v7'
        },
        {
            'url': reverse('RoutineTest:session_list'),
            'label': 'Results & Analytics',
            'data_nav': 'results',
            'active': current_url_name == 'session_list'
        }
    ]
    
    # Add admin-only tabs
    if is_head_teacher:
        nav_items.append({
            'url': reverse('RoutineTest:curriculum_mapping'),
            'label': '🎯 Curriculum Mapping',
            'data_nav': 'curriculum',
            'active': current_url_name == 'curriculum_mapping',
            'special_style': 'background: linear-gradient(135deg, #1B5E20 0%, #0D4F1F 100%);',
            'admin_badge': True
        })
    
    # Build HTML
    html = ['<nav class="nav-tabs" id="routinetest-nav-forced" data-version="4.1">']
    html.append('<ul style="display: flex; justify-content: space-between; width: 100%;">')
    html.append('<div style="display: flex; flex: 1;">')
    
    for item in nav_items:
        li_attrs = ''
        if item.get('id'):
            li_attrs = f' id="{item["id"]}"'
        
        html.append(f'<li{li_attrs}>')
        
        # Build link attributes
        class_attr = 'active' if item['active'] else ''
        style_attr = item.get('special_style', '')
        
        html.append(f'''
            <a href="{item['url']}" 
               class="{class_attr}"
               data-nav="{item['data_nav']}"
               {"style='" + style_attr + "'" if style_attr else ''}>
               {item['label']}
               {'<span style="position: absolute; top: 5px; right: 5px; background: #FFD700; color: #1B5E20; font-size: 10px; padding: 2px 5px; border-radius: 3px; font-weight: bold;">ADMIN</span>' if item.get('admin_badge') else ''}
            </a>
        ''')
        html.append('</li>')
    
    html.append('</div>')
    
    # Add user section
    html.append('<div style="display: flex; margin-left: auto; align-items: stretch; flex-shrink: 0;">')
    
    if user and user.is_authenticated:
        username = user.get_full_name() or user.username
        html.append(f'''
            <li><a href="#" class="profile-link">👤 {username}</a></li>
            <li><a href="{reverse('core:logout')}" style="background-color: #e74c3c;">Logout</a></li>
        ''')
    else:
        html.append(f'''
            <li><a href="{reverse('PlacementTest:teacher_login')}" style="background-color: #00A65E;">Login</a></li>
        ''')
    
    html.append('</div>')
    html.append('</ul>')
    html.append('</nav>')
    
    # Add JavaScript to ensure visibility
    html.append('''
    <script>
    (function() {
        console.log('[NAVIGATION_TAG_V7] Force rendered navigation with unified Classes & Exams tab');
        const unifiedTab = document.getElementById('unified-tab-v7');
        if (unifiedTab) {
            unifiedTab.style.display = 'flex';
            unifiedTab.style.visibility = 'visible';
            console.log('✅ [NAVIGATION_TAG_V7] Unified Classes & Exams tab verified visible');
        }
        // Log all tabs for debugging
        const allTabs = document.querySelectorAll('.nav-tabs a');
        console.log('[NAVIGATION_TAG_V7] Total tabs:', allTabs.length);
        allTabs.forEach((tab, i) => {
            console.log(`  Tab ${i+1}: ${tab.textContent.trim()} -> ${tab.getAttribute('data-nav')}`);
        });
    })();
    </script>
    ''')
    
    return mark_safe(''.join(html))


@register.simple_tag
def matrix_tab_check():
    """
    Returns JavaScript to verify unified Classes & Exams tab visibility
    Version 7: Checks for unified tab instead of separate tabs
    """
    js = '''
    <script>
    (function() {
        const checkUnifiedTab = function() {
            const tabs = document.querySelectorAll('.nav-tabs a');
            let unifiedFound = false;
            
            tabs.forEach(tab => {
                if (tab.textContent.includes('Classes & Exams') || 
                    tab.getAttribute('data-nav') === 'classes-exams' ||
                    tab.href && tab.href.includes('classes-exams')) {
                    unifiedFound = true;
                    console.log('✅ [TAB_CHECK_V7] Unified Classes & Exams tab found:', {
                        text: tab.textContent,
                        href: tab.href,
                        visible: tab.offsetParent !== null,
                        dataNav: tab.getAttribute('data-nav')
                    });
                }
            });
            
            if (!unifiedFound) {
                console.error('❌ [TAB_CHECK_V7] Unified Classes & Exams tab NOT found in navigation!');
                
                // Try to create it
                const navContainer = document.querySelector('.nav-tabs ul > div');
                if (navContainer) {
                    const li = document.createElement('li');
                    li.id = 'unified-tab-v7-dynamic';
                    li.innerHTML = '<a href="/RoutineTest/classes-exams/" data-nav="classes-exams" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; font-weight: bold !important; border: 2px solid #667eea !important; padding: 12px 20px !important;">🎓 Classes & Exams</a>';
                    navContainer.appendChild(li);
                    console.log('🔧 [TAB_CHECK_V7] Unified Classes & Exams tab created dynamically');
                }
            }
            
            // Log navigation version
            console.log('[TAB_CHECK_V7] Navigation version check completed at', new Date().toISOString());
        };
        
        // Run checks
        checkUnifiedTab();
        setTimeout(checkUnifiedTab, 500);
        setTimeout(checkUnifiedTab, 1000);
    })();
    </script>
    '''
    return mark_safe(js)