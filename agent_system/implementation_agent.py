"""
Implementation Specialist Agent
"""

from .core import AgentCore
from typing import Dict, Any

class ImplementationAgent(AgentCore):
    """Agent specialized in implementing features and fixing bugs"""
    
    def __init__(self):
        super().__init__(
            name="Implementation Agent",
            expertise=[
                "fix", "add", "change", "update", "implement", "bug", "error",
                "feature", "function", "method", "class", "module", "code",
                "python", "django", "javascript", "database", "model", "view"
            ]
        )
    
    def _perform_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and implement features or fixes"""
        request = task.get("request", "")
        
        analysis = {
            "type": self._identify_task_type(request),
            "scope": self._determine_scope(request),
            "components": self._identify_components(request),
            "approach": self._determine_approach(request)
        }
        
        return {
            "agent": self.name,
            "analysis": analysis,
            "implementation_plan": self._create_implementation_plan(analysis),
            "files_affected": self._identify_affected_files(request),
            "testing_required": self._determine_testing_needs(analysis),
            "risk_assessment": self._assess_risk(analysis)
        }
    
    def _identify_task_type(self, request: str) -> str:
        """Identify the type of implementation task"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["bug", "error", "fix", "broken"]):
            return "bug_fix"
        elif any(word in request_lower for word in ["add", "new", "create", "implement"]):
            return "new_feature"
        elif any(word in request_lower for word in ["update", "change", "modify", "refactor"]):
            return "modification"
        elif any(word in request_lower for word in ["remove", "delete", "clean"]):
            return "removal"
        else:
            return "general_implementation"
    
    def _determine_scope(self, request: str) -> str:
        """Determine the scope of the implementation"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["system", "entire", "all", "whole"]):
            return "system_wide"
        elif any(word in request_lower for word in ["module", "component", "section"]):
            return "module_level"
        elif any(word in request_lower for word in ["function", "method", "class"]):
            return "function_level"
        else:
            return "localized"
    
    def _identify_components(self, request: str) -> list:
        """Identify which system components are involved"""
        components = []
        request_lower = request.lower()
        
        component_map = {
            "database": ["database", "model", "migration", "schema"],
            "views": ["view", "controller", "endpoint", "api"],
            "templates": ["template", "html", "frontend"],
            "authentication": ["auth", "login", "permission", "user"],
            "routing": ["url", "route", "path"],
            "forms": ["form", "validation", "input"],
            "api": ["api", "rest", "json", "serializer"]
        }
        
        for component, keywords in component_map.items():
            if any(keyword in request_lower for keyword in keywords):
                components.append(component)
        
        return components if components else ["general"]
    
    def _determine_approach(self, request: str) -> Dict[str, Any]:
        """Determine the implementation approach"""
        task_type = self._identify_task_type(request)
        
        approaches = {
            "bug_fix": {
                "strategy": "diagnose_and_fix",
                "steps": [
                    "Reproduce the issue",
                    "Identify root cause",
                    "Implement fix",
                    "Test fix",
                    "Verify no regressions"
                ]
            },
            "new_feature": {
                "strategy": "incremental_development",
                "steps": [
                    "Design feature architecture",
                    "Create models/schemas if needed",
                    "Implement backend logic",
                    "Create frontend interface",
                    "Integrate and test"
                ]
            },
            "modification": {
                "strategy": "refactor_safely",
                "steps": [
                    "Understand current implementation",
                    "Plan changes",
                    "Create tests if missing",
                    "Implement changes",
                    "Verify functionality"
                ]
            }
        }
        
        return approaches.get(task_type, {
            "strategy": "analyze_and_implement",
            "steps": ["Analyze", "Plan", "Implement", "Test"]
        })
    
    def _create_implementation_plan(self, analysis: Dict[str, Any]) -> list:
        """Create a detailed implementation plan"""
        plan = []
        task_type = analysis.get("type", "")
        scope = analysis.get("scope", "")
        
        # Add git checkpoint
        plan.append({
            "step": "Create git checkpoint",
            "command": "git add -A && git commit -m 'CHECKPOINT: Before implementation'",
            "priority": "critical"
        })
        
        # Type-specific steps
        if task_type == "bug_fix":
            plan.extend([
                {"step": "Locate error source", "priority": "high"},
                {"step": "Create minimal test case", "priority": "medium"},
                {"step": "Implement fix", "priority": "high"},
                {"step": "Test fix thoroughly", "priority": "critical"}
            ])
        elif task_type == "new_feature":
            plan.extend([
                {"step": "Create database migrations if needed", "priority": "high"},
                {"step": "Implement models", "priority": "high"},
                {"step": "Create views/endpoints", "priority": "high"},
                {"step": "Build UI components", "priority": "medium"},
                {"step": "Add validation", "priority": "medium"}
            ])
        
        # Add testing step
        plan.append({
            "step": "Run comprehensive tests",
            "command": "python manage.py test",
            "priority": "critical"
        })
        
        return plan
    
    def _identify_affected_files(self, request: str) -> list:
        """Identify files that will be affected"""
        files = []
        request_lower = request.lower()
        
        # Core Django files
        if "model" in request_lower:
            files.append("*/models.py")
        if "view" in request_lower:
            files.append("*/views.py")
        if "url" in request_lower or "route" in request_lower:
            files.append("*/urls.py")
        if "template" in request_lower:
            files.append("templates/**/*.html")
        if "form" in request_lower:
            files.append("*/forms.py")
        
        # Specific modules
        if "teacher" in request_lower:
            files.extend([
                "primepath_routinetest/views/admin_teacher_management.py",
                "primepath_routinetest/models/teacher.py"
            ])
        if "exam" in request_lower:
            files.extend([
                "placement_test/models.py",
                "placement_test/views.py"
            ])
        
        return files if files else ["**/*.py", "templates/**/*.html"]
    
    def _determine_testing_needs(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what testing is required"""
        task_type = analysis.get("type", "")
        scope = analysis.get("scope", "")
        
        testing = {
            "unit_tests": task_type in ["bug_fix", "new_feature"],
            "integration_tests": scope in ["system_wide", "module_level"],
            "ui_tests": "templates" in analysis.get("components", []),
            "regression_tests": task_type == "bug_fix",
            "performance_tests": scope == "system_wide"
        }
        
        return {
            "required": [k for k, v in testing.items() if v],
            "priority": "critical" if task_type == "bug_fix" else "high"
        }
    
    def _assess_risk(self, analysis: Dict[str, Any]) -> str:
        """Assess the risk level of the implementation"""
        scope = analysis.get("scope", "")
        components = analysis.get("components", [])
        
        if scope == "system_wide":
            return "high"
        elif "database" in components or "authentication" in components:
            return "medium-high"
        elif scope == "module_level":
            return "medium"
        else:
            return "low"