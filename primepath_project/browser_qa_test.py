#!/usr/bin/env python3
"""
Browser-based QA Testing for PrimePath
Using requests to simulate browser interactions
"""

import requests
import json
from datetime import datetime

class BrowserQATest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.session = requests.Session()
        self.results = []
        
    def test_homepage(self):
        """Test homepage loads"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.results.append({"test": "Homepage", "status": "PASS", "details": "Loaded successfully"})
                # Check for key elements
                if "PrimePath" in response.text:
                    self.results.append({"test": "Homepage Content", "status": "PASS", "details": "PrimePath branding found"})
                return True
            else:
                self.results.append({"test": "Homepage", "status": "FAIL", "details": f"Status: {response.status_code}"})
                return False
        except Exception as e:
            self.results.append({"test": "Homepage", "status": "FAIL", "details": str(e)})
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        endpoints = [
            ("/api/PlacementTest/exams/", "Exams API"),
            ("/api/PlacementTest/sessions/", "Sessions API"),
            ("/api/PlacementTest/exams/check-version/", "Version Check API"),
        ]
        
        for url, name in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                if response.status_code in [200, 201]:
                    self.results.append({"test": name, "status": "PASS", "details": f"Status: {response.status_code}"})
                else:
                    self.results.append({"test": name, "status": "WARNING", "details": f"Status: {response.status_code}"})
            except Exception as e:
                self.results.append({"test": name, "status": "FAIL", "details": str(e)})
    
    def test_exam_creation_page(self):
        """Test exam creation page"""
        try:
            response = self.session.get(f"{self.base_url}/api/PlacementTest/exams/create/")
            if response.status_code == 200:
                self.results.append({"test": "Exam Creation Page", "status": "PASS", "details": "Page loads"})
                
                # Check for form elements
                if "form" in response.text.lower() or "exam" in response.text.lower():
                    self.results.append({"test": "Exam Form Elements", "status": "PASS", "details": "Form elements found"})
            else:
                self.results.append({"test": "Exam Creation Page", "status": "FAIL", "details": f"Status: {response.status_code}"})
        except Exception as e:
            self.results.append({"test": "Exam Creation Page", "status": "FAIL", "details": str(e)})
    
    def test_student_interface(self):
        """Test student test interface"""
        try:
            # First get a session ID from the database
            response = self.session.get(f"{self.base_url}/api/PlacementTest/sessions/")
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    session_id = data[0].get('id')
                    if session_id:
                        # Try to access student test page
                        test_url = f"{self.base_url}/PlacementTest/test/{session_id}/"
                        response = self.session.get(test_url)
                        if response.status_code == 200:
                            self.results.append({"test": "Student Test Interface", "status": "PASS", "details": "Test page loads"})
                        else:
                            self.results.append({"test": "Student Test Interface", "status": "WARNING", "details": f"Status: {response.status_code}"})
                else:
                    self.results.append({"test": "Student Test Interface", "status": "SKIP", "details": "No sessions available"})
        except Exception as e:
            self.results.append({"test": "Student Test Interface", "status": "FAIL", "details": str(e)})
    
    def generate_report(self):
        """Generate QA report"""
        print("\n" + "="*60)
        print("BROWSER QA TEST RESULTS")
        print("="*60)
        
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        warnings = sum(1 for r in self.results if r['status'] == 'WARNING')
        
        print(f"\n📊 Summary:")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️  Warnings: {warnings}")
        
        print("\n📋 Detailed Results:")
        for result in self.results:
            icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            print(f"  {icon} {result['test']}: {result['details']}")
        
        # Save to file
        with open('browser_qa_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {'passed': passed, 'failed': failed, 'warnings': warnings},
                'results': self.results
            }, f, indent=2)
        
        print("\n📄 Results saved to browser_qa_results.json")
    
    def run_all_tests(self):
        """Run all browser tests"""
        print("🌐 Starting Browser QA Tests...")
        
        self.test_homepage()
        self.test_api_endpoints()
        self.test_exam_creation_page()
        self.test_student_interface()
        
        self.generate_report()

if __name__ == "__main__":
    tester = BrowserQATest()
    tester.run_all_tests()