"""
UI/UX Specialist Agent
"""

from .core import AgentCore
from typing import Dict, Any

class UIAgent(AgentCore):
    """Agent specialized in UI/UX issues and improvements"""
    
    def __init__(self):
        super().__init__(
            name="UI/UX Agent",
            expertise=[
                "wide", "narrow", "layout", "design", "color", "spacing",
                "responsive", "css", "styling", "bootstrap", "template",
                "ui", "ux", "interface", "display", "visual", "alignment",
                "grid", "flex", "padding", "margin", "height", "width"
            ]
        )
    
    def _perform_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and fix UI/UX issues"""
        request = task.get("request", "")
        
        # Analyze the UI issue
        analysis = {
            "type": self._identify_issue_type(request),
            "components": self._identify_components(request),
            "solutions": self._generate_solutions(request)
        }
        
        return {
            "agent": self.name,
            "analysis": analysis,
            "recommendations": self._get_recommendations(analysis),
            "priority": self._calculate_priority(request),
            "files_to_check": self._identify_files(request)
        }
    
    def _identify_issue_type(self, request: str) -> str:
        """Identify the type of UI issue"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["wide", "narrow", "width"]):
            return "width_issue"
        elif any(word in request_lower for word in ["spacing", "gap", "padding", "margin"]):
            return "spacing_issue"
        elif any(word in request_lower for word in ["layout", "grid", "flex"]):
            return "layout_issue"
        elif any(word in request_lower for word in ["color", "theme", "dark", "light"]):
            return "theme_issue"
        elif any(word in request_lower for word in ["responsive", "mobile", "tablet"]):
            return "responsive_issue"
        else:
            return "general_ui_issue"
    
    def _identify_components(self, request: str) -> list:
        """Identify which UI components are affected"""
        components = []
        request_lower = request.lower()
        
        component_keywords = {
            "curriculum": ["curriculum", "program", "level"],
            "table": ["table", "grid", "row", "column"],
            "button": ["button", "btn", "click"],
            "form": ["form", "input", "field"],
            "modal": ["modal", "dialog", "popup"],
            "navigation": ["nav", "menu", "sidebar"],
            "card": ["card", "panel", "container"]
        }
        
        for component, keywords in component_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                components.append(component)
        
        return components if components else ["general"]
    
    def _generate_solutions(self, request: str) -> list:
        """Generate potential solutions for the UI issue"""
        solutions = []
        request_lower = request.lower()
        
        if "wide" in request_lower or "narrow" in request_lower:
            solutions.extend([
                "Adjust Bootstrap column classes (col-md-*, col-lg-*)",
                "Modify max-width CSS property",
                "Update flexbox properties",
                "Check container constraints"
            ])
        
        if "spacing" in request_lower or "gap" in request_lower:
            solutions.extend([
                "Adjust padding/margin values",
                "Use Bootstrap spacing utilities",
                "Check for conflicting CSS rules",
                "Review parent container spacing"
            ])
        
        if "responsive" in request_lower:
            solutions.extend([
                "Add media queries for different screen sizes",
                "Use Bootstrap responsive utilities",
                "Test on multiple device sizes",
                "Implement flexible layouts"
            ])
        
        return solutions if solutions else ["Inspect element and analyze CSS"]
    
    def _get_recommendations(self, analysis: Dict[str, Any]) -> list:
        """Get specific recommendations based on analysis"""
        recommendations = []
        
        issue_type = analysis.get("type", "")
        
        if issue_type == "width_issue":
            recommendations.append("Check Bootstrap grid system usage")
            recommendations.append("Review CSS width properties")
            recommendations.append("Consider using responsive units (%, vw)")
        elif issue_type == "spacing_issue":
            recommendations.append("Use consistent spacing scale")
            recommendations.append("Apply Bootstrap spacing utilities")
            recommendations.append("Check for margin collapse issues")
        elif issue_type == "layout_issue":
            recommendations.append("Review flexbox/grid implementation")
            recommendations.append("Check parent container properties")
            recommendations.append("Validate HTML structure")
        
        return recommendations
    
    def _calculate_priority(self, request: str) -> str:
        """Calculate the priority of the UI issue"""
        request_lower = request.lower()
        
        high_priority_words = ["broken", "not working", "error", "bug", "critical"]
        medium_priority_words = ["fix", "issue", "problem", "wrong"]
        
        if any(word in request_lower for word in high_priority_words):
            return "high"
        elif any(word in request_lower for word in medium_priority_words):
            return "medium"
        else:
            return "low"
    
    def _identify_files(self, request: str) -> list:
        """Identify which files might need to be checked"""
        files = []
        request_lower = request.lower()
        
        # Template files
        if any(word in request_lower for word in ["template", "html", "display"]):
            files.extend([
                "templates/primepath_routinetest/*.html",
                "templates/core/*.html"
            ])
        
        # CSS files
        if any(word in request_lower for word in ["style", "css", "design", "color"]):
            files.extend([
                "static/css/*.css",
                "templates/*/includes/*.html"
            ])
        
        # Specific component files
        if "curriculum" in request_lower:
            files.append("templates/primepath_routinetest/classes_exams_unified.html")
        if "teacher" in request_lower:
            files.append("templates/primepath_routinetest/admin_teacher_management.html")
        
        return files if files else ["templates/**/*.html", "static/css/*.css"]