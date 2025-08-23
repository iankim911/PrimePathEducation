"""
Documentation Specialist Agent
"""

from .core import AgentCore
from typing import Dict, Any, List

class DocumentationAgent(AgentCore):
    """Agent specialized in documentation and knowledge management"""
    
    def __init__(self):
        super().__init__(
            name="Documentation Agent",
            expertise=[
                "document", "explain", "readme", "guide", "tutorial",
                "comment", "docstring", "annotation", "specification",
                "api", "reference", "manual", "help", "description"
            ]
        )
    
    def _perform_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze documentation needs and create documentation plans"""
        request = task.get("request", "")
        
        analysis = {
            "doc_type": self._identify_documentation_type(request),
            "scope": self._determine_scope(request),
            "audience": self._identify_audience(request)
        }
        
        return {
            "agent": self.name,
            "analysis": analysis,
            "documentation_plan": self._create_documentation_plan(analysis),
            "templates": self._generate_templates(analysis),
            "sections": self._identify_sections(analysis),
            "review_checklist": self._create_review_checklist()
        }
    
    def _identify_documentation_type(self, request: str) -> str:
        """Identify the type of documentation needed"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["api", "endpoint", "rest"]):
            return "api_documentation"
        elif any(word in request_lower for word in ["readme", "setup", "install"]):
            return "readme"
        elif any(word in request_lower for word in ["guide", "tutorial", "howto"]):
            return "user_guide"
        elif any(word in request_lower for word in ["code", "function", "class"]):
            return "code_documentation"
        elif any(word in request_lower for word in ["architecture", "design", "system"]):
            return "technical_documentation"
        else:
            return "general_documentation"
    
    def _determine_scope(self, request: str) -> str:
        """Determine the scope of documentation"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["entire", "whole", "complete", "full"]):
            return "comprehensive"
        elif any(word in request_lower for word in ["module", "component", "feature"]):
            return "component_level"
        elif any(word in request_lower for word in ["function", "method", "class"]):
            return "function_level"
        else:
            return "focused"
    
    def _identify_audience(self, request: str) -> str:
        """Identify the target audience"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["developer", "technical", "api"]):
            return "developers"
        elif any(word in request_lower for word in ["user", "admin", "teacher"]):
            return "end_users"
        elif any(word in request_lower for word in ["team", "contributor"]):
            return "contributors"
        else:
            return "general"
    
    def _create_documentation_plan(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a documentation plan"""
        plan = []
        doc_type = analysis.get("doc_type", "")
        
        # Phase 1: Information Gathering
        plan.append({
            "phase": "Information Gathering",
            "tasks": [
                "Review existing documentation",
                "Identify documentation gaps",
                "Interview stakeholders",
                "Collect code examples"
            ]
        })
        
        # Phase 2: Documentation Creation
        if doc_type == "api_documentation":
            plan.append({
                "phase": "API Documentation",
                "tasks": [
                    "Document endpoints",
                    "Provide request/response examples",
                    "Document authentication",
                    "Include error codes"
                ]
            })
        elif doc_type == "readme":
            plan.append({
                "phase": "README Creation",
                "tasks": [
                    "Write project description",
                    "Add installation instructions",
                    "Include usage examples",
                    "List dependencies"
                ]
            })
        elif doc_type == "user_guide":
            plan.append({
                "phase": "User Guide",
                "tasks": [
                    "Create getting started section",
                    "Write feature tutorials",
                    "Add troubleshooting guide",
                    "Include FAQ section"
                ]
            })
        
        # Phase 3: Review and Publish
        plan.append({
            "phase": "Review and Publish",
            "tasks": [
                "Technical review",
                "Grammar and style check",
                "Format documentation",
                "Publish to appropriate location"
            ]
        })
        
        return plan
    
    def _generate_templates(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate documentation templates"""
        doc_type = analysis.get("doc_type", "")
        templates = {}
        
        if doc_type == "api_documentation":
            templates["api_endpoint"] = """
## Endpoint: [ENDPOINT_NAME]

**URL:** `/api/[endpoint_path]`
**Method:** `GET|POST|PUT|DELETE`
**Authentication:** Required/Optional

### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| param1    | string | Yes | Description |

### Response
```json
{
  "status": "success",
  "data": {}
}
```

### Error Codes
| Code | Description |
|------|-------------|
| 400  | Bad Request |
| 401  | Unauthorized |
"""
        
        elif doc_type == "readme":
            templates["readme"] = """
# Project Name

Brief description of what this project does.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
# Example code
```

## Features

- Feature 1
- Feature 2

## Contributing

Please read CONTRIBUTING.md for details.

## License

This project is licensed under the MIT License.
"""
        
        elif doc_type == "code_documentation":
            templates["function_doc"] = '''"""
Brief description of the function.

Args:
    param1 (type): Description of param1.
    param2 (type): Description of param2.

Returns:
    type: Description of return value.

Raises:
    ExceptionType: Description of when this exception is raised.

Example:
    >>> function_name(param1, param2)
    expected_output
"""'''
        
        return templates
    
    def _identify_sections(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify documentation sections needed"""
        doc_type = analysis.get("doc_type", "")
        audience = analysis.get("audience", "")
        
        sections = []
        
        # Common sections
        sections.extend([
            "Overview",
            "Getting Started"
        ])
        
        # Type-specific sections
        if doc_type == "api_documentation":
            sections.extend([
                "Authentication",
                "Endpoints",
                "Request/Response Format",
                "Error Handling",
                "Rate Limiting"
            ])
        elif doc_type == "user_guide":
            sections.extend([
                "Installation",
                "Configuration",
                "Features",
                "Tutorials",
                "FAQ",
                "Troubleshooting"
            ])
        elif doc_type == "technical_documentation":
            sections.extend([
                "Architecture",
                "Design Decisions",
                "Data Models",
                "API Reference",
                "Deployment"
            ])
        
        # Audience-specific sections
        if audience == "developers":
            sections.extend([
                "Development Setup",
                "Testing",
                "Contributing Guidelines"
            ])
        elif audience == "end_users":
            sections.extend([
                "User Interface Guide",
                "Common Tasks",
                "Tips and Tricks"
            ])
        
        return sections
    
    def _create_review_checklist(self) -> List[str]:
        """Create a documentation review checklist"""
        return [
            "✓ Clear and concise language",
            "✓ Accurate technical information",
            "✓ Complete code examples",
            "✓ Proper formatting and structure",
            "✓ No spelling or grammar errors",
            "✓ All links working",
            "✓ Version information included",
            "✓ Contact information provided",
            "✓ License information clear",
            "✓ Screenshots/diagrams where helpful",
            "✓ Searchable and indexed",
            "✓ Mobile-friendly format"
        ]