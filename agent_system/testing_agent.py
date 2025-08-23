"""
Testing Specialist Agent
"""

from .core import AgentCore
from typing import Dict, Any, List

class TestingAgent(AgentCore):
    """Agent specialized in testing and quality assurance"""
    
    def __init__(self):
        super().__init__(
            name="Testing Agent",
            expertise=[
                "test", "verify", "check", "ensure", "quality", "qa",
                "unit", "integration", "regression", "validation",
                "assert", "mock", "fixture", "coverage", "debug"
            ]
        )
    
    def _perform_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze testing requirements and create test plans"""
        request = task.get("request", "")
        
        analysis = {
            "test_type": self._identify_test_type(request),
            "coverage_areas": self._identify_coverage_areas(request),
            "test_strategy": self._determine_test_strategy(request)
        }
        
        return {
            "agent": self.name,
            "analysis": analysis,
            "test_plan": self._create_test_plan(analysis),
            "test_cases": self._generate_test_cases(request),
            "commands": self._generate_test_commands(analysis),
            "validation_checklist": self._create_validation_checklist(request)
        }
    
    def _identify_test_type(self, request: str) -> List[str]:
        """Identify types of testing needed"""
        request_lower = request.lower()
        test_types = []
        
        test_keywords = {
            "unit": ["unit", "function", "method", "class"],
            "integration": ["integration", "module", "component", "system"],
            "regression": ["regression", "previous", "existing", "break"],
            "ui": ["ui", "interface", "frontend", "display", "template"],
            "api": ["api", "endpoint", "rest", "json"],
            "performance": ["performance", "speed", "slow", "optimize"],
            "security": ["security", "auth", "permission", "vulnerability"]
        }
        
        for test_type, keywords in test_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                test_types.append(test_type)
        
        return test_types if test_types else ["comprehensive"]
    
    def _identify_coverage_areas(self, request: str) -> List[str]:
        """Identify which areas need test coverage"""
        areas = []
        request_lower = request.lower()
        
        area_keywords = {
            "models": ["model", "database", "schema"],
            "views": ["view", "controller", "endpoint"],
            "forms": ["form", "validation", "input"],
            "templates": ["template", "html", "render"],
            "authentication": ["auth", "login", "permission"],
            "api": ["api", "serializer", "rest"],
            "javascript": ["javascript", "js", "frontend"]
        }
        
        for area, keywords in area_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                areas.append(area)
        
        return areas if areas else ["all"]
    
    def _determine_test_strategy(self, request: str) -> Dict[str, Any]:
        """Determine the testing strategy"""
        test_types = self._identify_test_type(request)
        
        strategy = {
            "approach": "bottom_up" if "unit" in test_types else "top_down",
            "priority_order": [],
            "parallel_execution": len(test_types) > 2,
            "continuous": "regression" in test_types
        }
        
        # Set priority order
        if "security" in test_types:
            strategy["priority_order"].append("security")
        if "api" in test_types:
            strategy["priority_order"].append("api")
        if "unit" in test_types:
            strategy["priority_order"].append("unit")
        if "integration" in test_types:
            strategy["priority_order"].append("integration")
        if "ui" in test_types:
            strategy["priority_order"].append("ui")
        
        return strategy
    
    def _create_test_plan(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a comprehensive test plan"""
        plan = []
        test_types = analysis.get("test_type", [])
        
        # Setup phase
        plan.append({
            "phase": "Setup",
            "steps": [
                "Create test database backup",
                "Set up test fixtures",
                "Clear test cache"
            ]
        })
        
        # Test execution phases
        if "unit" in test_types:
            plan.append({
                "phase": "Unit Testing",
                "steps": [
                    "Test individual functions",
                    "Test class methods",
                    "Verify return values",
                    "Check error handling"
                ]
            })
        
        if "integration" in test_types:
            plan.append({
                "phase": "Integration Testing",
                "steps": [
                    "Test module interactions",
                    "Verify data flow",
                    "Check API contracts",
                    "Test database operations"
                ]
            })
        
        if "ui" in test_types:
            plan.append({
                "phase": "UI Testing",
                "steps": [
                    "Test page rendering",
                    "Verify user interactions",
                    "Check responsive design",
                    "Validate forms"
                ]
            })
        
        # Validation phase
        plan.append({
            "phase": "Validation",
            "steps": [
                "Run full test suite",
                "Generate coverage report",
                "Check for regressions",
                "Document results"
            ]
        })
        
        return plan
    
    def _generate_test_cases(self, request: str) -> List[Dict[str, Any]]:
        """Generate specific test cases"""
        test_cases = []
        request_lower = request.lower()
        
        # Basic test case template
        base_case = {
            "name": "",
            "description": "",
            "setup": [],
            "execution": [],
            "assertions": [],
            "teardown": []
        }
        
        # Generate context-specific test cases
        if "teacher" in request_lower:
            test_case = base_case.copy()
            test_case.update({
                "name": "test_teacher_management",
                "description": "Test teacher creation and permissions",
                "setup": ["Create test user", "Create test school"],
                "execution": ["Create teacher", "Assign permissions"],
                "assertions": ["Teacher exists", "Permissions correct"]
            })
            test_cases.append(test_case)
        
        if "exam" in request_lower:
            test_case = base_case.copy()
            test_case.update({
                "name": "test_exam_functionality",
                "description": "Test exam creation and submission",
                "setup": ["Create test exam", "Create test questions"],
                "execution": ["Submit answers", "Calculate score"],
                "assertions": ["Score calculated", "Results saved"]
            })
            test_cases.append(test_case)
        
        # Add generic test case if no specific ones
        if not test_cases:
            test_case = base_case.copy()
            test_case.update({
                "name": "test_basic_functionality",
                "description": "Test core functionality",
                "setup": ["Initialize test environment"],
                "execution": ["Execute main function"],
                "assertions": ["Expected output received"]
            })
            test_cases.append(test_case)
        
        return test_cases
    
    def _generate_test_commands(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate test commands to run"""
        commands = []
        test_types = analysis.get("test_type", [])
        coverage_areas = analysis.get("coverage_areas", [])
        
        # Basic Django test command
        commands.append({
            "description": "Run all tests",
            "command": "python manage.py test --settings=primepath_project.settings_sqlite"
        })
        
        # Specific test commands
        if "models" in coverage_areas:
            commands.append({
                "description": "Test models",
                "command": "python manage.py test --pattern='test_models.py'"
            })
        
        if "views" in coverage_areas:
            commands.append({
                "description": "Test views",
                "command": "python manage.py test --pattern='test_views.py'"
            })
        
        if "api" in test_types:
            commands.append({
                "description": "Test API endpoints",
                "command": "python manage.py test api"
            })
        
        # Coverage command
        commands.append({
            "description": "Generate coverage report",
            "command": "coverage run --source='.' manage.py test && coverage report"
        })
        
        return commands
    
    def _create_validation_checklist(self, request: str) -> List[str]:
        """Create a validation checklist"""
        checklist = [
            "✓ All tests passing",
            "✓ No new errors in console",
            "✓ Database migrations successful",
            "✓ UI renders correctly",
            "✓ Forms validate properly",
            "✓ Authentication works",
            "✓ No performance degradation",
            "✓ Security checks passed"
        ]
        
        request_lower = request.lower()
        
        # Add specific checks based on request
        if "teacher" in request_lower:
            checklist.append("✓ Teacher management functions work")
        if "exam" in request_lower:
            checklist.append("✓ Exam creation and submission work")
        if "ui" in request_lower or "template" in request_lower:
            checklist.append("✓ Templates render without errors")
        
        return checklist