"""
Core Agent Base Class
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class AgentCore:
    """Base class for all autonomous agents"""
    
    def __init__(self, name: str, expertise: List[str]):
        self.name = name
        self.expertise = expertise
        self.status = "idle"
        self.current_task = None
        self.memory = []
        self.logger = logging.getLogger(f"Agent.{name}")
        
    def analyze(self, request: str) -> Dict[str, Any]:
        """Analyze a request and determine if this agent should handle it"""
        relevance_score = self._calculate_relevance(request)
        return {
            "agent": self.name,
            "relevance": relevance_score,
            "can_handle": relevance_score > 0.1,  # Lower threshold for better agent activation
            "expertise_match": self._match_expertise(request)
        }
    
    def _calculate_relevance(self, request: str) -> float:
        """Calculate how relevant this request is to the agent's expertise"""
        request_lower = request.lower()
        matched_keywords = 0
        
        for keyword in self.expertise:
            keyword_lower = keyword.lower()
            # Check if keyword appears in request
            if keyword_lower in request_lower:
                matched_keywords += 1
        
        # If any keywords match, calculate relevance
        if matched_keywords == 0:
            return 0
        
        # Simple relevance: if 1+ keywords match, agent is relevant
        # More matches = higher relevance
        if matched_keywords >= 3:
            return 0.9
        elif matched_keywords >= 2:
            return 0.7
        elif matched_keywords >= 1:
            return 0.5
        
        return 0
    
    def _match_expertise(self, request: str) -> List[str]:
        """Find which expertise areas match the request"""
        request_lower = request.lower()
        return [exp for exp in self.expertise if exp.lower() in request_lower]
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task assigned to this agent"""
        self.status = "working"
        self.current_task = task
        
        try:
            result = self._perform_task(task)
            self.memory.append({
                "timestamp": datetime.now().isoformat(),
                "task": task,
                "result": result
            })
            self.status = "completed"
            return result
        except Exception as e:
            self.status = "error"
            self.logger.error(f"Error executing task: {e}")
            return {"error": str(e), "agent": self.name}
        finally:
            self.current_task = None
    
    def _perform_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in subclasses to implement specific behavior"""
        raise NotImplementedError(f"{self.name} must implement _perform_task")
    
    def collaborate(self, other_agent: 'AgentCore', context: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with another agent on a task"""
        return {
            "collaboration": f"{self.name} <-> {other_agent.name}",
            "context": context,
            "status": "ready"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "status": self.status,
            "current_task": self.current_task,
            "expertise": self.expertise,
            "memory_size": len(self.memory)
        }