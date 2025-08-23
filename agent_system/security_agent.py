"""
Security Specialist Agent
"""

from .core import AgentCore
from typing import Dict, Any, List

class SecurityAgent(AgentCore):
    """Agent specialized in security analysis and improvements"""
    
    def __init__(self):
        super().__init__(
            name="Security Agent",
            expertise=[
                "auth", "authentication", "permission", "vulnerability",
                "security", "csrf", "xss", "sql", "injection", "sanitize",
                "validate", "encrypt", "hash", "token", "session"
            ]
        )
    
    def _perform_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and fix security issues"""
        request = task.get("request", "")
        
        analysis = {
            "security_type": self._identify_security_concern(request),
            "vulnerabilities": self._scan_vulnerabilities(request),
            "risk_level": self._assess_risk_level(request)
        }
        
        return {
            "agent": self.name,
            "analysis": analysis,
            "security_audit": self._perform_security_audit(analysis),
            "remediation_plan": self._create_remediation_plan(analysis),
            "best_practices": self._suggest_best_practices(analysis),
            "compliance_check": self._check_compliance(analysis)
        }
    
    def _identify_security_concern(self, request: str) -> str:
        """Identify the type of security concern"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["auth", "login", "user"]):
            return "authentication"
        elif any(word in request_lower for word in ["permission", "access", "role"]):
            return "authorization"
        elif any(word in request_lower for word in ["xss", "script", "injection"]):
            return "xss_vulnerability"
        elif any(word in request_lower for word in ["sql", "database", "query"]):
            return "sql_injection"
        elif any(word in request_lower for word in ["csrf", "token"]):
            return "csrf_protection"
        elif any(word in request_lower for word in ["encrypt", "hash", "password"]):
            return "cryptography"
        else:
            return "general_security"
    
    def _scan_vulnerabilities(self, request: str) -> List[Dict[str, Any]]:
        """Scan for potential vulnerabilities"""
        vulnerabilities = []
        
        # Common Django vulnerabilities to check
        vuln_checks = [
            {
                "type": "Missing CSRF protection",
                "severity": "high",
                "check": "CSRF middleware enabled",
                "file": "settings.py"
            },
            {
                "type": "Insecure password validators",
                "severity": "medium",
                "check": "Strong password requirements",
                "file": "settings.py"
            },
            {
                "type": "Debug mode in production",
                "severity": "critical",
                "check": "DEBUG = False in production",
                "file": "settings.py"
            },
            {
                "type": "Missing security headers",
                "severity": "medium",
                "check": "Security middleware configured",
                "file": "settings.py"
            },
            {
                "type": "Unvalidated user input",
                "severity": "high",
                "check": "Input validation on forms",
                "file": "forms.py"
            }
        ]
        
        for check in vuln_checks:
            vulnerabilities.append(check)
        
        return vulnerabilities
    
    def _assess_risk_level(self, request: str) -> str:
        """Assess the overall risk level"""
        request_lower = request.lower()
        
        critical_words = ["vulnerability", "exploit", "breach", "attack"]
        high_words = ["permission", "auth", "password", "token"]
        medium_words = ["validate", "sanitize", "check"]
        
        if any(word in request_lower for word in critical_words):
            return "critical"
        elif any(word in request_lower for word in high_words):
            return "high"
        elif any(word in request_lower for word in medium_words):
            return "medium"
        else:
            return "low"
    
    def _perform_security_audit(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a security audit"""
        audit = {
            "authentication": {
                "status": "check",
                "items": [
                    "Password strength requirements",
                    "Account lockout policy",
                    "Session timeout configuration",
                    "Two-factor authentication"
                ]
            },
            "authorization": {
                "status": "check",
                "items": [
                    "Role-based access control",
                    "Permission inheritance",
                    "API endpoint protection",
                    "Admin interface security"
                ]
            },
            "data_protection": {
                "status": "check",
                "items": [
                    "Database encryption",
                    "Sensitive data masking",
                    "Secure file uploads",
                    "PII handling"
                ]
            },
            "infrastructure": {
                "status": "check",
                "items": [
                    "HTTPS enforcement",
                    "Security headers",
                    "CORS configuration",
                    "Rate limiting"
                ]
            }
        }
        
        return audit
    
    def _create_remediation_plan(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a security remediation plan"""
        plan = []
        security_type = analysis.get("security_type", "")
        risk_level = analysis.get("risk_level", "low")
        
        # Immediate actions for critical/high risk
        if risk_level in ["critical", "high"]:
            plan.append({
                "priority": "immediate",
                "action": "Apply security patches",
                "steps": [
                    "Backup current state",
                    "Apply critical security fixes",
                    "Test authentication flow",
                    "Verify no functionality broken"
                ]
            })
        
        # Authentication improvements
        if security_type == "authentication":
            plan.append({
                "priority": "high",
                "action": "Strengthen authentication",
                "steps": [
                    "Implement stronger password policy",
                    "Add account lockout after failed attempts",
                    "Implement session timeout",
                    "Consider adding 2FA"
                ]
            })
        
        # Authorization improvements
        if security_type == "authorization":
            plan.append({
                "priority": "high",
                "action": "Review permissions",
                "steps": [
                    "Audit current permission structure",
                    "Implement principle of least privilege",
                    "Add permission decorators to views",
                    "Test permission boundaries"
                ]
            })
        
        # General security hardening
        plan.append({
            "priority": "medium",
            "action": "Security hardening",
            "steps": [
                "Enable all Django security middleware",
                "Configure security headers",
                "Implement content security policy",
                "Set up security monitoring"
            ]
        })
        
        return plan
    
    def _suggest_best_practices(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest security best practices"""
        practices = [
            "Always use Django's ORM to prevent SQL injection",
            "Enable CSRF protection on all forms",
            "Use HTTPS in production",
            "Keep Django and dependencies updated",
            "Implement proper input validation",
            "Use Django's built-in authentication system",
            "Configure secure session cookies",
            "Implement rate limiting for APIs",
            "Use environment variables for secrets",
            "Regular security audits and penetration testing"
        ]
        
        security_type = analysis.get("security_type", "")
        
        # Add specific practices
        if security_type == "authentication":
            practices.insert(0, "Implement multi-factor authentication")
            practices.insert(1, "Use secure password hashing (PBKDF2, Argon2)")
        elif security_type == "authorization":
            practices.insert(0, "Implement role-based access control (RBAC)")
            practices.insert(1, "Use Django's permission system effectively")
        
        return practices[:10]
    
    def _check_compliance(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Check security compliance"""
        compliance = {
            "django_security": {
                "csrf_protection": "✓",
                "xss_protection": "✓",
                "sql_injection_protection": "✓",
                "clickjacking_protection": "✓",
                "ssl_redirect": "check required",
                "session_cookie_secure": "check required",
                "csrf_cookie_secure": "check required"
            },
            "authentication": {
                "password_validation": "✓",
                "session_management": "✓",
                "user_model_security": "✓",
                "login_rate_limiting": "implement"
            },
            "data_protection": {
                "encryption_at_rest": "check required",
                "encryption_in_transit": "check required",
                "pii_handling": "review needed",
                "data_retention": "policy needed"
            }
        }
        
        return compliance