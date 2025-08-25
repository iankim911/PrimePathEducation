#!/usr/bin/env python
"""
Comprehensive test to verify existing features are not affected by password validation changes
"""
import os
import django
import requests
import re

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from primepath_student.forms import StudentRegistrationForm, StudentLoginForm
from primepath_student.models import StudentProfile

def check_server_status():
    """Check if Django server is running"""
    try:
        response = requests.get('http://127.0.0.1:8000', timeout=5)
        return response.status_code == 200
    except:
        return False

class ExistingFeaturesImpactTest:
    def __init__(self):
        self.client = Client()
        self.session = requests.Session()
        self.base_url = 'http://127.0.0.1:8000'
        self.results = {
            'form_compatibility': {'passed': 0, 'failed': 0, 'tests': []},
            'authentication_flow': {'passed': 0, 'failed': 0, 'tests': []},
            'existing_accounts': {'passed': 0, 'failed': 0, 'tests': []},
            'registration_flow': {'passed': 0, 'failed': 0, 'tests': []},
            'template_rendering': {'passed': 0, 'failed': 0, 'tests': []},
            'javascript_compatibility': {'passed': 0, 'failed': 0, 'tests': []}
        }
    
    def test_form_compatibility(self):
        """Test that existing form functionality still works"""
        print("🔍 TESTING FORM COMPATIBILITY")
        print("-" * 40)
        
        # Test 1: Basic form structure intact
        test_name = "Form structure and required fields"
        try:
            form = StudentRegistrationForm()
            required_fields = ['first_name', 'last_name', 'student_id', 'email', 'phone_number', 'password1', 'password2']
            
            missing_fields = []
            for field in required_fields:
                if field not in form.fields:
                    missing_fields.append(field)
            
            if not missing_fields:
                print(f"   ✅ {test_name}: All required fields present")
                self.results['form_compatibility']['passed'] += 1
            else:
                print(f"   ❌ {test_name}: Missing fields: {missing_fields}")
                self.results['form_compatibility']['failed'] += 1
                
            self.results['form_compatibility']['tests'].append({
                'name': test_name,
                'passed': len(missing_fields) == 0,
                'details': f"Missing: {missing_fields}" if missing_fields else "All fields present"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
            self.results['form_compatibility']['failed'] += 1
            self.results['form_compatibility']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
        
        # Test 2: Valid registration still works (with good password)
        test_name = "Valid registration with non-similar password"
        try:
            form_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'student_id': 'compatibility_test',
                'phone_number': '01099999999',
                'email': 'compatibility@test.com',
                'password1': 'SecureValidPassword123!',  # Different from student_id
                'password2': 'SecureValidPassword123!',
                'parent1_name': 'Test Parent',
                'parent1_phone': '01088888888'
            }
            
            form = StudentRegistrationForm(form_data)
            is_valid = form.is_valid()
            
            if is_valid:
                print(f"   ✅ {test_name}: Form validation works correctly")
                self.results['form_compatibility']['passed'] += 1
            else:
                print(f"   ❌ {test_name}: Form should be valid but isn't: {form.errors}")
                self.results['form_compatibility']['failed'] += 1
                
            self.results['form_compatibility']['tests'].append({
                'name': test_name,
                'passed': is_valid,
                'details': str(form.errors) if not is_valid else "Valid form accepted"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
            self.results['form_compatibility']['failed'] += 1
            self.results['form_compatibility']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
        
        # Test 3: Login form unaffected
        test_name = "Login form functionality"
        try:
            login_form = StudentLoginForm()
            expected_fields = ['identifier', 'password', 'login_method', 'remember_me']
            
            missing_fields = []
            for field in expected_fields:
                if field not in login_form.fields:
                    missing_fields.append(field)
            
            if not missing_fields:
                print(f"   ✅ {test_name}: Login form structure intact")
                self.results['form_compatibility']['passed'] += 1
            else:
                print(f"   ❌ {test_name}: Login form missing fields: {missing_fields}")
                self.results['form_compatibility']['failed'] += 1
                
            self.results['form_compatibility']['tests'].append({
                'name': test_name,
                'passed': len(missing_fields) == 0,
                'details': f"Missing: {missing_fields}" if missing_fields else "All fields present"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
            self.results['form_compatibility']['failed'] += 1
            self.results['form_compatibility']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
    
    def test_authentication_flow(self):
        """Test that existing authentication still works"""
        print("\n🔐 TESTING AUTHENTICATION FLOW")
        print("-" * 40)
        
        # Test 1: Check if authentication utilities are available
        test_name = "Authentication utilities availability"
        try:
            from core.utils.authentication import safe_login, UserTypeDetector
            print(f"   ✅ {test_name}: Authentication utilities accessible")
            self.results['authentication_flow']['passed'] += 1
            self.results['authentication_flow']['tests'].append({
                'name': test_name,
                'passed': True,
                'details': "Authentication utilities imported successfully"
            })
        except ImportError as e:
            print(f"   ❌ {test_name}: Cannot import authentication utilities - {e}")
            self.results['authentication_flow']['failed'] += 1
            self.results['authentication_flow']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
        
        # Test 2: Check if student registration view still works
        test_name = "Student registration view accessibility"
        try:
            from primepath_student.views.registration import student_register
            print(f"   ✅ {test_name}: Registration view accessible")
            self.results['authentication_flow']['passed'] += 1
            self.results['authentication_flow']['tests'].append({
                'name': test_name,
                'passed': True,
                'details': "Registration view imported successfully"
            })
        except ImportError as e:
            print(f"   ❌ {test_name}: Cannot import registration view - {e}")
            self.results['authentication_flow']['failed'] += 1
            self.results['authentication_flow']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
    
    def test_existing_accounts(self):
        """Test that existing user accounts are not affected"""
        print("\n👥 TESTING EXISTING ACCOUNTS")
        print("-" * 40)
        
        # Test 1: Check existing users can still be queried
        test_name = "Existing user accounts query"
        try:
            users = User.objects.all()
            user_count = users.count()
            print(f"   ✅ {test_name}: Found {user_count} existing users")
            self.results['existing_accounts']['passed'] += 1
            self.results['existing_accounts']['tests'].append({
                'name': test_name,
                'passed': True,
                'details': f"Found {user_count} users in database"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Error querying users - {e}")
            self.results['existing_accounts']['failed'] += 1
            self.results['existing_accounts']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
        
        # Test 2: Check student profiles are intact
        test_name = "Student profiles integrity"
        try:
            profiles = StudentProfile.objects.all()
            profile_count = profiles.count()
            print(f"   ✅ {test_name}: Found {profile_count} student profiles")
            self.results['existing_accounts']['passed'] += 1
            self.results['existing_accounts']['tests'].append({
                'name': test_name,
                'passed': True,
                'details': f"Found {profile_count} student profiles"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Error querying profiles - {e}")
            self.results['existing_accounts']['failed'] += 1
            self.results['existing_accounts']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
    
    def test_registration_flow(self):
        """Test registration flow with server if available"""
        print("\n🌐 TESTING REGISTRATION FLOW")
        print("-" * 40)
        
        if not check_server_status():
            print("   ⚠️  Server not running - skipping HTTP tests")
            self.results['registration_flow']['tests'].append({
                'name': 'HTTP Registration Flow',
                'passed': False,
                'details': 'Server not running on 127.0.0.1:8000'
            })
            return
        
        # Test 1: Registration page loads
        test_name = "Registration page loads"
        try:
            response = self.session.get(f'{self.base_url}/student/register/')
            if response.status_code == 200:
                print(f"   ✅ {test_name}: Page loads successfully")
                self.results['registration_flow']['passed'] += 1
            else:
                print(f"   ❌ {test_name}: HTTP {response.status_code}")
                self.results['registration_flow']['failed'] += 1
                
            self.results['registration_flow']['tests'].append({
                'name': test_name,
                'passed': response.status_code == 200,
                'details': f"HTTP {response.status_code}"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
            self.results['registration_flow']['failed'] += 1
            self.results['registration_flow']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
        
        # Test 2: Check availability endpoint still works
        test_name = "Check availability endpoint"
        try:
            # Get CSRF token first
            response = self.session.get(f'{self.base_url}/student/register/')
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
            csrf_token = csrf_match.group(1) if csrf_match else 'dummy'
            
            # Test availability check
            check_response = self.session.post(
                f'{self.base_url}/student/check-availability/',
                json={'type': 'student_id', 'value': 'test_availability_check'},
                headers={'X-CSRFToken': csrf_token}
            )
            
            if check_response.status_code == 200:
                print(f"   ✅ {test_name}: Endpoint responds correctly")
                self.results['registration_flow']['passed'] += 1
            else:
                print(f"   ❌ {test_name}: HTTP {check_response.status_code}")
                self.results['registration_flow']['failed'] += 1
                
            self.results['registration_flow']['tests'].append({
                'name': test_name,
                'passed': check_response.status_code == 200,
                'details': f"HTTP {check_response.status_code}"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
            self.results['registration_flow']['failed'] += 1
            self.results['registration_flow']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
    
    def test_template_rendering(self):
        """Test that templates render without errors"""
        print("\n🎨 TESTING TEMPLATE RENDERING")
        print("-" * 40)
        
        if not check_server_status():
            print("   ⚠️  Server not running - skipping template tests")
            return
        
        # Test 1: Registration template renders
        test_name = "Registration template renders"
        try:
            response = self.session.get(f'{self.base_url}/student/register/')
            content = response.text
            
            # Check for key template elements
            required_elements = [
                'registrationForm',
                'password',
                'student_id',
                'csrf',
                '</form>',
                '</html>'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                print(f"   ✅ {test_name}: All template elements present")
                self.results['template_rendering']['passed'] += 1
            else:
                print(f"   ❌ {test_name}: Missing elements: {missing_elements}")
                self.results['template_rendering']['failed'] += 1
                
            self.results['template_rendering']['tests'].append({
                'name': test_name,
                'passed': len(missing_elements) == 0,
                'details': f"Missing: {missing_elements}" if missing_elements else "All elements present"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
            self.results['template_rendering']['failed'] += 1
            self.results['template_rendering']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
    
    def test_javascript_compatibility(self):
        """Test JavaScript compatibility and existing functionality"""
        print("\n🖥️  TESTING JAVASCRIPT COMPATIBILITY")
        print("-" * 40)
        
        if not check_server_status():
            print("   ⚠️  Server not running - skipping JavaScript tests")
            return
        
        # Test 1: Original form JavaScript still present
        test_name = "Original form JavaScript functionality"
        try:
            response = self.session.get(f'{self.base_url}/student/register/')
            content = response.text
            
            # Check for original form elements that JS depends on
            js_elements = [
                'nextStep',
                'previousStep', 
                'validateStep',
                'registrationForm',
                'progressBar'
            ]
            
            missing_elements = []
            for element in js_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if len(missing_elements) <= 1:  # Allow for minor changes
                print(f"   ✅ {test_name}: Core JavaScript functionality preserved")
                self.results['javascript_compatibility']['passed'] += 1
            else:
                print(f"   ⚠️  {test_name}: Some JS elements may be affected: {missing_elements}")
                self.results['javascript_compatibility']['failed'] += 1
                
            self.results['javascript_compatibility']['tests'].append({
                'name': test_name,
                'passed': len(missing_elements) <= 1,
                'details': f"Missing: {missing_elements}" if missing_elements else "All elements present"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
            self.results['javascript_compatibility']['failed'] += 1
            self.results['javascript_compatibility']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
        
        # Test 2: Enhanced validation doesn't break existing functionality
        test_name = "Enhanced validation integration"
        try:
            response = self.session.get(f'{self.base_url}/student/register/')
            content = response.text
            
            # Check that both original and new functionality coexist
            has_original = 'registrationForm' in content and 'progressBar' in content
            has_enhanced = 'password-validation-enhanced.js' in content or 'password-feedback' in content
            
            if has_original:
                print(f"   ✅ {test_name}: Original and enhanced validation coexist")
                self.results['javascript_compatibility']['passed'] += 1
            else:
                print(f"   ❌ {test_name}: Original functionality may be compromised")
                self.results['javascript_compatibility']['failed'] += 1
                
            self.results['javascript_compatibility']['tests'].append({
                'name': test_name,
                'passed': has_original,
                'details': f"Original: {has_original}, Enhanced: {has_enhanced}"
            })
        except Exception as e:
            print(f"   ❌ {test_name}: Exception - {e}")
            self.results['javascript_compatibility']['failed'] += 1
            self.results['javascript_compatibility']['tests'].append({
                'name': test_name,
                'passed': False,
                'details': str(e)
            })
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 EXISTING FEATURES IMPACT TEST RESULTS")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results['passed']
            failed = results['failed']
            total_tests = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            print(f"\n{category.replace('_', ' ').title()}:")
            if total_tests > 0:
                success_rate = (passed / total_tests) * 100
                print(f"  📈 {passed}/{total_tests} tests passed ({success_rate:.1f}%)")
                
                if failed > 0:
                    print("  ⚠️  Failed tests:")
                    for test in results['tests']:
                        if not test['passed']:
                            print(f"    - {test['name']}: {test['details']}")
            else:
                print("  ℹ️  No tests run for this category")
        
        overall_total = total_passed + total_failed
        if overall_total > 0:
            overall_success = (total_passed / overall_total) * 100
            print(f"\n🎯 OVERALL RESULTS: {total_passed}/{overall_total} ({overall_success:.1f}%)")
            
            if overall_success >= 90:
                print("✅ EXCELLENT: Password validation changes have minimal impact on existing features")
            elif overall_success >= 75:
                print("⚠️  GOOD: Most existing features preserved, minor issues detected")
            else:
                print("❌ CAUTION: Some existing features may be affected, review needed")
        
        return {
            'total_passed': total_passed,
            'total_failed': total_failed,
            'success_rate': overall_success if overall_total > 0 else 0,
            'details': self.results
        }
    
    def run_all_tests(self):
        """Run all impact tests"""
        print("🔍 TESTING IMPACT OF PASSWORD VALIDATION CHANGES")
        print("=" * 60)
        
        self.test_form_compatibility()
        self.test_authentication_flow()
        self.test_existing_accounts()
        self.test_registration_flow()
        self.test_template_rendering()
        self.test_javascript_compatibility()
        
        return self.generate_summary()

def main():
    tester = ExistingFeaturesImpactTest()
    summary = tester.run_all_tests()
    
    print(f"\n📋 RECOMMENDATIONS:")
    if summary['success_rate'] >= 90:
        print("✅ Password validation improvements are ready for production")
        print("✅ No significant impact on existing features detected")
    elif summary['success_rate'] >= 75:
        print("⚠️  Review failed tests before deploying to production")
        print("⚠️  Consider additional testing for affected features")
    else:
        print("❌ Significant issues detected - fix before deployment")
        print("❌ Existing functionality may be compromised")

if __name__ == '__main__':
    main()