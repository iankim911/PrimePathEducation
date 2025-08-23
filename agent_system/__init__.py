"""
Autonomous Agent System for PrimePath Project
==============================================

This system provides intelligent, collaborative agents that automatically
analyze, plan, and execute solutions for various development tasks.
"""

from .core import AgentCore
from .integration import process_with_agents, AgentCoordinator
from .ui_agent import UIAgent
from .implementation_agent import ImplementationAgent
from .testing_agent import TestingAgent
from .performance_agent import PerformanceAgent
from .security_agent import SecurityAgent
from .documentation_agent import DocumentationAgent

__all__ = [
    'AgentCore',
    'process_with_agents',
    'AgentCoordinator',
    'UIAgent',
    'ImplementationAgent',
    'TestingAgent',
    'PerformanceAgent',
    'SecurityAgent',
    'DocumentationAgent'
]

# Version information
__version__ = '1.0.0'
__author__ = 'PrimePath Development Team'

print("✅ Agent System Module Loaded - All sub-agents ready for activation")