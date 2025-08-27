#!/usr/bin/env python
"""
Phase 3: Migrate Batch 1 - Critical Templates
Date: August 27, 2025
Purpose: Migrate 5 core authentication templates to unified_base.html
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Batch 1 - Critical templates
BATCH_1_TEMPLATES = [
    'core/auth/login.html',
    'core/index.html', 
    'core/auth/profile.html',
    'core/auth/logout_confirm.html',
    'core/base_clean.html',
]

def create_backup(template_path):
    """Create a backup of the original template"""
    backup_dir = Path(f'migration_backups_{datetime.now().strftime("%Y%m%d_%H%M%S")}_batch1')
    backup_dir.mkdir(exist_ok=True)
    
    # Create subdirectories if needed
    backup_file = backup_dir / template_path
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy original file
    original_file = Path('templates') / template_path
    if original_file.exists():
        shutil.copy2(original_file, backup_file)
        print(f"✅ Backup created: {backup_file}")
    else:
        print(f"❌ Original not found: {original_file}")
    
    return backup_file

def migrate_core_auth_login():
    """Migrate core/auth/login.html to use unified_base.html"""
    template_path = 'templates/core/auth/login.html'
    
    # Create backup first
    create_backup('core/auth/login.html')
    
    # The new content - configure unified_base.html to be "clean"
    new_content = '''{% extends "unified_base.html" %}
{% load static %}

{# Configure unified_base to be clean (no header/navigation) #}
{% block module_name %}core{% endblock %}
{% block data_module %}core-auth{% endblock %}
{% block body_class %}login-page clean{% endblock %}

{# Hide header and navigation for clean login page #}
{% block header_wrapper %}{% endblock %}
{% block navigation_wrapper %}{% endblock %}

{% block title %}Teacher Login - PrimePath{% endblock %}

{% block extra_css %}
<style>
    /* Override unified_base body styles for clean login */
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        min-height: 100vh;
        margin: 0;
        padding: 0;
    }
    
    /* Clean login page - no container padding */
    .container {
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .main-content {
        min-height: 100vh !important;
    }
    
    /* Login Page Styles - Mobile Responsive */
    .login-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .login-card {
        background: white;
        border-radius: 10px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        padding: 40px;
        width: 100%;
        max-width: 420px;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .login-logo {
        width: 80px;
        height: 80px;
        margin: 0 auto 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 36px;
        font-weight: bold;
    }
    
    .login-title {
        font-size: 24px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
    }
    
    .login-subtitle {
        color: #666;
        font-size: 14px;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-label {
        display: block;
        margin-bottom: 8px;
        color: #333;
        font-weight: 500;
        font-size: 14px;
    }
    
    .form-input {
        width: 100%;
        padding: 12px 16px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 14px;
        transition: all 0.3s;
        box-sizing: border-box;
    }
    
    .form-input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .form-input.error {
        border-color: #f56565;
    }
    
    .form-checkbox-group {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .form-checkbox {
        width: 18px;
        height: 18px;
        margin-right: 8px;
        cursor: pointer;
    }
    
    .form-checkbox-label {
        color: #666;
        font-size: 14px;
        cursor: pointer;
        user-select: none;
    }
    
    .login-button {
        width: 100%;
        padding: 14px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        margin-top: 10px;
    }
    
    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .login-button:active {
        transform: translateY(0);
    }
    
    .login-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }
    
    .error-message {
        background: #fee;
        border: 1px solid #fcc;
        color: #c33;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 20px;
        font-size: 14px;
    }
    
    .success-message {
        background: #efe;
        border: 1px solid #cfc;
        color: #3c3;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 20px;
        font-size: 14px;
    }
    
    .login-footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }
    
    .login-footer-text {
        color: #666;
        font-size: 13px;
    }
    
    .login-footer-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    
    .login-footer-link:hover {
        text-decoration: underline;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 480px) {
        .login-card {
            padding: 30px 20px;
        }
        
        .login-title {
            font-size: 20px;
        }
        
        .form-input {
            padding: 10px 14px;
        }
        
        .login-button {
            padding: 12px;
            font-size: 15px;
        }
    }
    
    /* Loading spinner */
    .spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 0.8s linear infinite;
        margin-left: 8px;
        vertical-align: middle;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
{% endblock %}

{# Override content_wrapper to remove container padding #}
{% block content_wrapper %}
    {% block content %}
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <div class="login-logo">P</div>
                <h1 class="login-title">Teacher Login</h1>
                <p class="login-subtitle">Access your PrimePath dashboard</p>
            </div>
            
            {% if messages %}
                {% for message in messages %}
                    <div class="{% if message.tags == 'error' %}error-message{% else %}success-message{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
            
            <form method="post" action="{% url 'core:login' %}" id="loginForm">
                {% csrf_token %}
                
                {% if next %}
                    <input type="hidden" name="next" value="{{ next }}">
                {% endif %}
                
                <div class="form-group">
                    <label for="username" class="form-label">Username or Email</label>
                    <input 
                        type="text" 
                        id="username" 
                        name="username" 
                        class="form-input" 
                        required
                        autofocus
                        placeholder="Enter your username"
                        autocomplete="username"
                    >
                </div>
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <input 
                        type="password" 
                        id="password" 
                        name="password" 
                        class="form-input" 
                        required
                        placeholder="Enter your password"
                        autocomplete="current-password"
                    >
                </div>
                
                <div class="form-checkbox-group">
                    <input type="checkbox" id="remember_me" name="remember_me" class="form-checkbox">
                    <label for="remember_me" class="form-checkbox-label">Remember me for 2 weeks</label>
                </div>
                
                <button type="submit" class="login-button" id="loginButton">
                    Sign In
                </button>
            </form>
            
            
            <div class="login-footer">
                <p class="login-footer-text">
                    Don't have an account? 
                    <a href="#" class="login-footer-link" onclick="alert('Please contact your administrator to create an account.'); return false;">Contact Admin</a>
                </p>
                <p class="login-footer-text" style="margin-top: 10px;">
                    <a href="/" class="login-footer-link">← Back to Home</a>
                </p>
            </div>
        </div>
    </div>
    {% endblock %}
{% endblock %}

{% block extra_js %}
<script>
// Login form handler with comprehensive logging
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const button = document.getElementById('loginButton');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    // Template validation and navigation check
    const navigationCheck = {
        hasNavTabs: document.querySelector('.nav-tabs') !== null,
        hasNavMenu: document.querySelector('nav') !== null,
        hasPlacementTestLinks: document.querySelectorAll('a[href*="PlacementTest"]').length > 0,
        hasRoutineTestLinks: document.querySelectorAll('a[href*="RoutineTest"]').length > 0,
        baseTemplate: 'unified_base.html',  // Updated base template
        actualNavElements: [],
        timestamp: new Date().toISOString()
    };
    
    // Collect any navigation elements that shouldn't be here
    document.querySelectorAll('nav, .nav-tabs, .navigation, .menu').forEach(el => {
        navigationCheck.actualNavElements.push({
            tag: el.tagName,
            className: el.className,
            id: el.id || 'no-id',
            childCount: el.children.length
        });
    });
    
    // Critical check: This should be FALSE for login page
    if (navigationCheck.hasNavTabs || navigationCheck.hasPlacementTestLinks) {
        console.error('[AUTH_LOGIN_NAV_ERROR] ⚠️ Navigation elements detected on login page!', navigationCheck);
    } else {
        console.log('[AUTH_LOGIN_NAV_OK] ✅ No navigation elements found - Login page is correctly neutral');
    }
    
    // Enhanced console logging
    console.log('[AUTH_LOGIN_PAGE] Login page loaded', navigationCheck);
    console.log('[UNIFIED_BASE_MIGRATION] ✅ Successfully migrated to unified_base.html');
    
    const loginPageData = {
        action: 'page_loaded',
        has_next: '{{ next }}' !== '',
        next_url: '{{ next }}',
        referrer: document.referrer,
        came_from_logout: document.referrer.includes('/logout'),
        timestamp: new Date().toISOString(),
        baseTemplate: 'unified_base.html'
    };
    
    console.log('[AUTH_LOGIN_PAGE]', loginPageData);
    
    // Check if user just logged out
    if (document.referrer.includes('/logout')) {
        console.log('[AUTH_POST_LOGOUT]', {
            action: 'arrived_after_logout',
            message: 'User successfully logged out and redirected to login',
            timestamp: new Date().toISOString()
        });
    }
    
    // Check for logout success message
    const messages = document.querySelector('.messages');
    if (messages && messages.textContent.includes('logged out')) {
        console.log('[AUTH_LOGOUT_CONFIRMED]', {
            action: 'logout_success_message_displayed',
            timestamp: new Date().toISOString()
        });
    }
    
    // Form submission handler
    form.addEventListener('submit', function(e) {
        // Log submission attempt
        console.log('[AUTH_LOGIN_SUBMIT]', {
            action: 'form_submit',
            username: usernameInput.value,
            remember_me: document.getElementById('remember_me').checked,
            timestamp: new Date().toISOString()
        });
        
        // Disable button and show loading
        button.disabled = true;
        button.innerHTML = 'Signing In<span class="spinner"></span>';
        
        // Validate inputs
        let hasError = false;
        
        if (!usernameInput.value.trim()) {
            usernameInput.classList.add('error');
            hasError = true;
        } else {
            usernameInput.classList.remove('error');
        }
        
        if (!passwordInput.value) {
            passwordInput.classList.add('error');
            hasError = true;
        } else {
            passwordInput.classList.remove('error');
        }
        
        if (hasError) {
            e.preventDefault();
            button.disabled = false;
            button.innerHTML = 'Sign In';
            
            console.log('[AUTH_LOGIN_ERROR]', {
                action: 'validation_failed',
                username_empty: !usernameInput.value.trim(),
                password_empty: !passwordInput.value
            });
            return false;
        }
        
        // Log successful validation
        console.log('[AUTH_LOGIN_VALIDATED]', {
            action: 'validation_passed',
            submitting: true
        });
    });
    
    // Remove error states on input
    usernameInput.addEventListener('input', function() {
        this.classList.remove('error');
    });
    
    passwordInput.addEventListener('input', function() {
        this.classList.remove('error');
    });
    
    // Focus username field
    if (usernameInput) {
        usernameInput.focus();
    }
});
</script>
{% endblock %}'''
    
    # Write the new content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Migrated: {template_path}")

def migrate_core_index():
    """Migrate core/index.html to use unified_base.html"""
    template_path = 'templates/core/index.html'
    
    # First read the current content to understand it
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        print(f"📖 Current core/index.html content preview:")
        print(current_content[:200] + "..." if len(current_content) > 200 else current_content)
    except FileNotFoundError:
        print(f"❌ File not found: {template_path}")
        return False
    
    # Create backup
    create_backup('core/index.html')
    
    # Simple migration - update extends to use unified_base
    if '{% extends' in current_content:
        # Replace the extends line
        new_content = current_content.replace('{% extends "base.html" %}', '{% extends "unified_base.html" %}')
        new_content = new_content.replace('{% extends \'base.html\' %}', '{% extends "unified_base.html" %}')
        
        # Add module configuration blocks
        if '{% block module_name %}' not in new_content:
            new_content = new_content.replace('{% extends "unified_base.html" %}', 
                '{% extends "unified_base.html" %}\n\n{% block module_name %}core{% endblock %}\n{% block data_module %}core-home{% endblock %}')
    else:
        # Create new template if it doesn't extend anything
        new_content = '''{% extends "unified_base.html" %}
{% load static %}

{% block module_name %}core{% endblock %}
{% block data_module %}core-home{% endblock %}
{% block title %}PrimePath Assessment Platform{% endblock %}

{% block content %}
<div class="content">
    <h1>Welcome to PrimePath</h1>
    <p>Your comprehensive assessment and learning platform.</p>
    
    <div style="margin-top: 30px;">
        <h2>Available Modules</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h3>Placement Tests</h3>
                <p>Comprehensive placement assessment system</p>
                <a href="{% url 'placement_test:index' %}" class="btn">Access Placement Tests</a>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h3>Routine Tests</h3>
                <p>Regular assessment and progress tracking</p>
                <a href="{% url 'primepath_routinetest:index' %}" class="btn">Access Routine Tests</a>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h3>Student Portal</h3>
                <p>Student dashboard and exam interface</p>
                <a href="{% url 'primepath_student:dashboard' %}" class="btn">Student Portal</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Write the new content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Migrated: {template_path}")
    return True

def migrate_remaining_batch1():
    """Migrate the remaining 3 templates in Batch 1"""
    templates = [
        'core/auth/profile.html',
        'core/auth/logout_confirm.html',
        'core/base_clean.html'
    ]
    
    results = {'success': 0, 'failed': 0}
    
    for template in templates:
        try:
            # Check if file exists
            template_path = Path('templates') / template
            if not template_path.exists():
                print(f"📝 Creating new template: {template}")
                template_path.parent.mkdir(parents=True, exist_ok=True)
                
                if template == 'core/auth/profile.html':
                    content = '''{% extends "unified_base.html" %}
{% load static %}

{% block module_name %}core{% endblock %}
{% block data_module %}core-profile{% endblock %}
{% block title %}My Profile - PrimePath{% endblock %}

{% block content %}
<div class="content">
    <h1>My Profile</h1>
    <div class="profile-info">
        <p><strong>Username:</strong> {{ user.username }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <p><strong>Full Name:</strong> {{ user.get_full_name|default:"Not set" }}</p>
        <p><strong>Date Joined:</strong> {{ user.date_joined|date:"F j, Y" }}</p>
    </div>
    
    <div style="margin-top: 30px;">
        <a href="{% url 'core:dashboard' %}" class="btn">← Back to Dashboard</a>
        <a href="{% url 'core:logout' %}" class="btn" style="background-color: #dc3545; margin-left: 10px;">Logout</a>
    </div>
</div>
{% endblock %}'''
                
                elif template == 'core/auth/logout_confirm.html':
                    content = '''{% extends "unified_base.html" %}
{% load static %}

{# Configure unified_base to be clean (no header/navigation) #}
{% block module_name %}core{% endblock %}
{% block data_module %}core-logout{% endblock %}
{% block body_class %}logout-page clean{% endblock %}

{# Hide header and navigation for clean logout page #}
{% block header_wrapper %}{% endblock %}
{% block navigation_wrapper %}{% endblock %}

{% block title %}Logout - PrimePath{% endblock %}

{% block extra_css %}
<style>
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        min-height: 100vh;
        margin: 0;
        padding: 0;
    }
    
    .container {
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .main-content {
        min-height: 100vh !important;
    }
    
    .logout-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .logout-card {
        background: white;
        border-radius: 10px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        padding: 40px;
        width: 100%;
        max-width: 420px;
        text-align: center;
    }
    
    .logout-title {
        font-size: 24px;
        font-weight: 600;
        color: #333;
        margin-bottom: 20px;
    }
    
    .logout-message {
        color: #666;
        margin-bottom: 30px;
        line-height: 1.5;
    }
    
    .btn {
        display: inline-block;
        padding: 12px 24px;
        margin: 0 5px;
        border: none;
        border-radius: 6px;
        text-decoration: none;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .btn-secondary {
        background: #6c757d;
        color: white;
    }
    
    .btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
</style>
{% endblock %}

{% block content_wrapper %}
    {% block content %}
    <div class="logout-container">
        <div class="logout-card">
            <h1 class="logout-title">Logout Confirmation</h1>
            <p class="logout-message">
                Are you sure you want to logout? You will need to sign in again to access your account.
            </p>
            
            <form method="post" action="{% url 'core:logout' %}" style="display: inline;">
                {% csrf_token %}
                <button type="submit" class="btn btn-primary">Yes, Logout</button>
            </form>
            
            <a href="{% url 'core:dashboard' %}" class="btn btn-secondary">Cancel</a>
        </div>
    </div>
    {% endblock %}
{% endblock %}'''
                
                elif template == 'core/base_clean.html':
                    content = '''{% comment %}
LEGACY TEMPLATE - DEPRECATED
This template has been replaced by unified_base.html with clean configuration.
Kept for backward compatibility during migration period.
{% endcomment %}

{% extends "unified_base.html" %}

{# Configure unified_base to be clean (no header/navigation) #}
{% block module_name %}core{% endblock %}
{% block body_class %}clean-page{% endblock %}

{# Hide header and navigation for clean pages #}
{% block header_wrapper %}{% endblock %}
{% block navigation_wrapper %}{% endblock %}

{# Override content wrapper to remove default container styling #}
{% block content_wrapper %}
    {% block content %}{% endblock %}
{% endblock %}'''
                
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Created: {template}")
                results['success'] += 1
            else:
                # File exists, migrate it
                create_backup(template)
                
                with open(template_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                
                # Simple migration - replace extends
                if '{% extends' in current_content:
                    new_content = current_content.replace('{% extends "base.html" %}', '{% extends "unified_base.html" %}')
                    new_content = new_content.replace('{% extends \'base.html\' %}', '{% extends "unified_base.html" %}')
                    new_content = new_content.replace('{% extends "core/base_clean.html" %}', '{% extends "unified_base.html" %}')
                    
                    # Add module configuration
                    if '{% block module_name %}' not in new_content:
                        new_content = new_content.replace('{% extends "unified_base.html" %}', 
                            '{% extends "unified_base.html" %}\n\n{% block module_name %}core{% endblock %}')
                    
                    with open(template_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Migrated: {template}")
                    results['success'] += 1
                else:
                    print(f"⚠️  Skipped {template} - no extends directive found")
                    results['failed'] += 1
                    
        except Exception as e:
            print(f"❌ Failed to migrate {template}: {str(e)}")
            results['failed'] += 1
    
    return results

def run_batch1_migration():
    """Run the complete Batch 1 migration"""
    print("=" * 80)
    print("PHASE 3: BATCH 1 MIGRATION - CRITICAL TEMPLATES")
    print("=" * 80)
    print(f"Templates to migrate: {len(BATCH_1_TEMPLATES)}")
    
    results = {'success': 0, 'failed': 0}
    
    # Migrate core/auth/login.html
    try:
        migrate_core_auth_login()
        results['success'] += 1
    except Exception as e:
        print(f"❌ Failed to migrate core/auth/login.html: {str(e)}")
        results['failed'] += 1
    
    # Migrate core/index.html
    try:
        if migrate_core_index():
            results['success'] += 1
        else:
            results['failed'] += 1
    except Exception as e:
        print(f"❌ Failed to migrate core/index.html: {str(e)}")
        results['failed'] += 1
    
    # Migrate remaining templates
    print(f"\n" + "-" * 40)
    print("MIGRATING REMAINING BATCH 1 TEMPLATES")
    print("-" * 40)
    
    remaining_results = migrate_remaining_batch1()
    results['success'] += remaining_results['success']
    results['failed'] += remaining_results['failed']
    
    print(f"\n" + "=" * 80)
    print("BATCH 1 MIGRATION RESULTS")
    print("=" * 80)
    print(f"✅ Successful: {results['success']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"📊 Success Rate: {(results['success']/(results['success']+results['failed'])*100):.1f}%")
    
    return results

if __name__ == '__main__':
    results = run_batch1_migration()
    
    if results['failed'] == 0:
        print("\n🎉 Batch 1 partial migration completed successfully!")
        print("Next: Complete remaining templates in batch 1, then test")
    else:
        print(f"\n⚠️  {results['failed']} templates failed to migrate")
        print("Review errors before proceeding")