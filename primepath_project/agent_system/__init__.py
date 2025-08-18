"""
AUTONOMOUS AGENT SYSTEM
Multi-agent collaboration system for PrimePath project

Usage:
    from agent_system import autonomous_command
    
    # Process any command - agents automatically collaborate
    result = await autonomous_command("The curriculum column is too wide")
"""

from .agent_coordinator import (
    AgentCoordinator,
    AgentContext,
    MessageBus,
    TriggerManager,
    AutonomousAgentSystem,
    autonomous_command
)

from .agents import (
    UIUXReviewAgent,
    ImplementationAgent,
    QATestAgent,
    PerformanceAgent,
    DocumentationAgent,
    SecurityAgent,
    AgentRegistry
)

__all__ = [
    'AutonomousAgentSystem',
    'autonomous_command',
    'AgentCoordinator',
    'AgentContext',
    'MessageBus',
    'TriggerManager',
    'UIUXReviewAgent',
    'ImplementationAgent', 
    'QATestAgent',
    'PerformanceAgent',
    'DocumentationAgent',
    'SecurityAgent',
    'AgentRegistry'
]

# Quick start
def start_autonomous_system():
    """
    Start the autonomous agent system
    """
    system = AutonomousAgentSystem()
    system.start()
    return system