"""
Agent Integration and Coordination Module
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .ui_agent import UIAgent
from .implementation_agent import ImplementationAgent
from .testing_agent import TestingAgent
from .performance_agent import PerformanceAgent
from .security_agent import SecurityAgent
from .documentation_agent import DocumentationAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentCoordinator")

class AgentCoordinator:
    """Coordinates multiple agents to handle complex requests"""
    
    def __init__(self):
        self.agents = {
            "ui": UIAgent(),
            "implementation": ImplementationAgent(),
            "testing": TestingAgent(),
            "performance": PerformanceAgent(),
            "security": SecurityAgent(),
            "documentation": DocumentationAgent()
        }
        self.active_agents = []
        self.results = []
        self.recommendations_file = Path("/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/agent_recommendations.json")
        
    def analyze_request(self, request: str) -> Dict[str, Any]:
        """Analyze request and determine which agents should handle it"""
        logger.info(f"Analyzing request: {request[:100]}...")
        
        agent_scores = {}
        relevant_agents = []
        
        for name, agent in self.agents.items():
            analysis = agent.analyze(request)
            agent_scores[name] = analysis["relevance"]
            
            if analysis["can_handle"]:
                relevant_agents.append({
                    "name": name,
                    "agent": agent,
                    "relevance": analysis["relevance"],
                    "expertise_match": analysis["expertise_match"]
                })
        
        # Sort by relevance
        relevant_agents.sort(key=lambda x: x["relevance"], reverse=True)
        
        return {
            "request": request,
            "agent_scores": agent_scores,
            "selected_agents": [a["name"] for a in relevant_agents],
            "primary_agent": relevant_agents[0]["name"] if relevant_agents else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def coordinate_agents(self, request: str) -> Dict[str, Any]:
        """Coordinate multiple agents to handle a request"""
        analysis = self.analyze_request(request)
        
        if not analysis["selected_agents"]:
            logger.warning("No agents selected for request")
            return {
                "status": "no_agents",
                "message": "No specialized agents matched this request",
                "fallback": "manual_processing"
            }
        
        # Activate selected agents
        results = {}
        for agent_name in analysis["selected_agents"]:
            agent = self.agents[agent_name]
            logger.info(f"Activating {agent_name} agent...")
            
            try:
                task = {"request": request, "context": analysis}
                result = agent.execute(task)
                results[agent_name] = result
                self.active_agents.append(agent_name)
            except Exception as e:
                logger.error(f"Error with {agent_name} agent: {e}")
                results[agent_name] = {"error": str(e)}
        
        # Generate consolidated recommendations
        recommendations = self._consolidate_results(results, analysis)
        
        # Save recommendations to file
        self._save_recommendations(recommendations)
        
        return recommendations
    
    def _consolidate_results(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate results from multiple agents"""
        consolidated = {
            "timestamp": datetime.now().isoformat(),
            "request": analysis["request"],
            "agents_involved": list(results.keys()),
            "primary_agent": analysis["primary_agent"],
            "consolidated_recommendations": [],
            "action_items": [],
            "priority": "normal"
        }
        
        # Determine overall priority
        high_priority = False
        for agent_name, result in results.items():
            if isinstance(result, dict):
                if result.get("priority") == "high" or result.get("risk_assessment") == "high":
                    high_priority = True
                    break
        
        consolidated["priority"] = "high" if high_priority else "normal"
        
        # Collect recommendations from each agent
        for agent_name, result in results.items():
            if isinstance(result, dict) and "error" not in result:
                agent_recommendations = []
                
                # Extract recommendations based on agent type
                if agent_name == "ui" and "recommendations" in result:
                    agent_recommendations = result["recommendations"]
                elif agent_name == "implementation" and "implementation_plan" in result:
                    for step in result["implementation_plan"]:
                        agent_recommendations.append(step.get("step", ""))
                elif agent_name == "testing" and "test_plan" in result:
                    for phase in result["test_plan"]:
                        agent_recommendations.append(f"{phase['phase']}: {', '.join(phase.get('steps', []))}")
                elif agent_name == "performance" and "recommendations" in result:
                    agent_recommendations = result["recommendations"]
                elif agent_name == "security" and "best_practices" in result:
                    agent_recommendations = result["best_practices"][:5]
                elif agent_name == "documentation" and "documentation_plan" in result:
                    for phase in result["documentation_plan"]:
                        agent_recommendations.append(f"{phase['phase']}")
                
                # Add to consolidated recommendations
                for rec in agent_recommendations:
                    if rec:
                        consolidated["consolidated_recommendations"].append({
                            "agent": agent_name,
                            "recommendation": rec
                        })
        
        # Create action items
        consolidated["action_items"] = self._create_action_items(results, analysis)
        
        return consolidated
    
    def _create_action_items(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create prioritized action items from agent results"""
        action_items = []
        
        # Always start with a git checkpoint
        action_items.append({
            "priority": 1,
            "action": "Create git checkpoint",
            "command": "git add -A && git commit -m 'CHECKPOINT: Before agent-recommended changes'",
            "agent": "system"
        })
        
        # Add agent-specific actions
        for agent_name, result in results.items():
            if isinstance(result, dict) and "error" not in result:
                if agent_name == "implementation" and "files_affected" in result:
                    action_items.append({
                        "priority": 2,
                        "action": f"Review affected files",
                        "files": result["files_affected"],
                        "agent": agent_name
                    })
                
                if agent_name == "testing" and "commands" in result:
                    for cmd in result["commands"][:2]:  # Top 2 test commands
                        action_items.append({
                            "priority": 3,
                            "action": cmd["description"],
                            "command": cmd["command"],
                            "agent": agent_name
                        })
                
                if agent_name == "security" and "remediation_plan" in result:
                    for item in result["remediation_plan"][:1]:  # Top priority only
                        if item.get("priority") == "immediate":
                            action_items.append({
                                "priority": 0,  # Highest priority
                                "action": item["action"],
                                "steps": item["steps"],
                                "agent": agent_name
                            })
        
        # Sort by priority
        action_items.sort(key=lambda x: x["priority"])
        
        return action_items
    
    def _save_recommendations(self, recommendations: Dict[str, Any]):
        """Save recommendations to file for processing"""
        try:
            with open(self.recommendations_file, 'w') as f:
                json.dump(recommendations, f, indent=2)
            logger.info(f"Recommendations saved to {self.recommendations_file}")
        except Exception as e:
            logger.error(f"Failed to save recommendations: {e}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            "coordinator": "active",
            "agents": {},
            "active_agents": self.active_agents,
            "timestamp": datetime.now().isoformat()
        }
        
        for name, agent in self.agents.items():
            status["agents"][name] = agent.get_status()
        
        return status


def process_with_agents(request: str) -> Dict[str, Any]:
    """Main entry point for processing requests with agents"""
    coordinator = AgentCoordinator()
    
    logger.info("=" * 60)
    logger.info("AUTONOMOUS AGENT SYSTEM ACTIVATED")
    logger.info("=" * 60)
    
    # Process the request
    results = coordinator.coordinate_agents(request)
    
    # Display results
    print("\n" + "=" * 60)
    print("AGENT SYSTEM RECOMMENDATIONS")
    print("=" * 60)
    print(f"Request: {request}")
    print(f"Priority: {results.get('priority', 'normal').upper()}")
    print(f"Agents Involved: {', '.join(results.get('agents_involved', []))}")
    print("\nAction Items:")
    for i, item in enumerate(results.get('action_items', [])[:5], 1):
        print(f"  {i}. {item.get('action', 'No action')}")
        if 'command' in item:
            print(f"     Command: {item['command']}")
    
    print("\nTop Recommendations:")
    for rec in results.get('consolidated_recommendations', [])[:5]:
        print(f"  - [{rec['agent']}] {rec['recommendation']}")
    
    print("\n" + "=" * 60)
    print(f"Full recommendations saved to: agent_recommendations.json")
    print("=" * 60)
    
    return results


def check_agents():
    """Check the status of all agents"""
    coordinator = AgentCoordinator()
    status = coordinator.get_agent_status()
    
    print("\n" + "=" * 60)
    print("AGENT SYSTEM STATUS CHECK")
    print("=" * 60)
    print(f"Coordinator: {status['coordinator']}")
    print(f"Timestamp: {status['timestamp']}")
    print("\nAgent Status:")
    for name, agent_status in status['agents'].items():
        print(f"  {name.upper()} Agent:")
        print(f"    Status: {agent_status['status']}")
        print(f"    Expertise Areas: {len(agent_status['expertise'])}")
        print(f"    Memory Size: {agent_status['memory_size']}")
    print("=" * 60)
    
    return status