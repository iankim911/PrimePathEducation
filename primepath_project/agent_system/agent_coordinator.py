"""
AUTONOMOUS AGENT COORDINATION SYSTEM
Core orchestrator for multi-agent collaboration in PrimePath
"""

import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================
# PART 1: COORDINATION LAYER
# ============================================

class AgentPriority(Enum):
    """Execution priority levels for agents"""
    IMMEDIATE = 1  # Must run first (e.g., validation)
    HIGH = 2       # Should run early (e.g., implementation)
    MEDIUM = 3     # Standard priority (e.g., review)
    LOW = 4        # Can run later (e.g., documentation)
    CLEANUP = 5    # Runs last (e.g., reporting)

@dataclass
class AgentContext:
    """Shared context passed between agents"""
    command: str
    timestamp: datetime = field(default_factory=datetime.now)
    files_changed: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def add_result(self, agent_name: str, result: Any):
        """Add agent result to context"""
        self.results[agent_name] = {
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
    
    def get_previous_results(self) -> Dict[str, Any]:
        """Get all previous agent results"""
        return self.results.copy()

class AgentCoordinator:
    """
    Central coordination layer for all agents
    Manages agent lifecycle, execution order, and result aggregation
    """
    
    def __init__(self):
        self.agents = {}
        self.execution_plans = {}
        self.active_context = None
        self.message_bus = MessageBus()
        
        # Register all agents
        self._register_agents()
        
        # Setup execution patterns
        self._setup_execution_patterns()
        
        logger.info("🧠 Agent Coordinator initialized")
    
    def _register_agents(self):
        """Register all available agents"""
        from .agents import (
            UIUXReviewAgent,
            ImplementationAgent,
            QATestAgent,
            PerformanceAgent,
            DocumentationAgent,
            SecurityAgent
        )
        
        self.agents = {
            'ui_ux': UIUXReviewAgent(),
            'implementation': ImplementationAgent(),
            'qa': QATestAgent(),
            'performance': PerformanceAgent(),
            'documentation': DocumentationAgent(),
            'security': SecurityAgent()
        }
        
        # Subscribe agents to message bus
        for name, agent in self.agents.items():
            agent.set_message_bus(self.message_bus)
            agent.name = name
    
    def _setup_execution_patterns(self):
        """Define common execution patterns"""
        self.execution_patterns = {
            'ui_fix': ['implementation', 'ui_ux', 'qa'],
            'feature_add': ['implementation', 'ui_ux', 'security', 'qa', 'documentation'],
            'bug_fix': ['implementation', 'qa', 'performance'],
            'refactor': ['implementation', 'qa', 'performance', 'documentation'],
            'review_only': ['ui_ux', 'performance', 'security']
        }
    
    async def process_command(self, command: str) -> AgentContext:
        """
        Main entry point - processes user command through all relevant agents
        """
        logger.info(f"📨 Processing command: {command}")
        
        # Create context
        context = AgentContext(command=command)
        self.active_context = context
        
        # Phase 1: Broadcast for self-assessment
        assessments = await self._gather_assessments(command)
        
        # Phase 2: Create execution plan
        execution_plan = self._create_execution_plan(assessments)
        
        # Phase 3: Execute plan with inter-agent communication
        await self._execute_plan(execution_plan, context)
        
        # Phase 4: Aggregate and report results
        final_report = self._generate_report(context)
        
        return context
    
    async def _gather_assessments(self, command: str) -> Dict[str, Any]:
        """
        All agents analyze the command in parallel
        """
        assessments = {}
        
        # Parallel assessment
        tasks = []
        for name, agent in self.agents.items():
            tasks.append(self._assess_agent(name, agent, command))
        
        results = await asyncio.gather(*tasks)
        
        for name, assessment in results:
            if assessment and assessment.get('can_help'):
                assessments[name] = assessment
        
        logger.info(f"📊 {len(assessments)} agents volunteered to help")
        return assessments
    
    async def _assess_agent(self, name: str, agent: Any, command: str):
        """Individual agent assessment"""
        try:
            assessment = await agent.analyze_relevance(command)
            return (name, assessment)
        except Exception as e:
            logger.error(f"Agent {name} assessment failed: {e}")
            return (name, None)
    
    def _create_execution_plan(self, assessments: Dict[str, Any]) -> List[Dict]:
        """
        Create optimized execution plan based on assessments
        """
        plan = []
        
        for agent_name, assessment in assessments.items():
            plan.append({
                'agent': agent_name,
                'priority': assessment.get('priority', AgentPriority.MEDIUM),
                'confidence': assessment.get('confidence', 50),
                'dependencies': assessment.get('dependencies', []),
                'capabilities': assessment.get('capabilities', [])
            })
        
        # Sort by priority and resolve dependencies
        plan = self._resolve_dependencies(plan)
        plan.sort(key=lambda x: (x['priority'].value, -x['confidence']))
        
        logger.info(f"📋 Execution plan created with {len(plan)} steps")
        return plan
    
    def _resolve_dependencies(self, plan: List[Dict]) -> List[Dict]:
        """
        Ensure agents that depend on others run in correct order
        """
        # Create dependency graph
        resolved = []
        unresolved = plan.copy()
        
        while unresolved:
            # Find agents with no unmet dependencies
            ready = []
            for item in unresolved:
                deps = item['dependencies']
                if all(d in [r['agent'] for r in resolved] for d in deps):
                    ready.append(item)
            
            if not ready:
                # Circular dependency or missing agent
                logger.warning("Circular dependency detected, breaking...")
                resolved.extend(unresolved)
                break
            
            # Add ready agents to resolved
            for item in ready:
                resolved.append(item)
                unresolved.remove(item)
        
        return resolved
    
    async def _execute_plan(self, plan: List[Dict], context: AgentContext):
        """
        Execute agents according to plan with communication
        """
        for step in plan:
            agent_name = step['agent']
            agent = self.agents[agent_name]
            
            logger.info(f"🤖 Executing {agent_name} agent...")
            
            # Broadcast execution start
            self.message_bus.publish(
                sender=agent_name,
                event=f"{agent_name}_started",
                data={'context': context}
            )
            
            try:
                # Execute agent
                result = await agent.execute(context)
                
                # Add result to context
                context.add_result(agent_name, result)
                
                # Broadcast completion
                self.message_bus.publish(
                    sender=agent_name,
                    event=f"{agent_name}_completed",
                    data={'result': result, 'context': context}
                )
                
                # Check if any agent wants to interrupt
                if self._check_interrupts(result):
                    logger.warning(f"⚠️ Execution interrupted by {agent_name}")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Agent {agent_name} failed: {e}")
                context.errors.append(f"{agent_name}: {str(e)}")
                
                # Broadcast failure
                self.message_bus.publish(
                    sender=agent_name,
                    event=f"{agent_name}_failed",
                    data={'error': str(e), 'context': context}
                )
    
    def _check_interrupts(self, result: Any) -> bool:
        """
        Check if result requires stopping execution
        """
        if isinstance(result, dict):
            return result.get('interrupt_execution', False)
        return False
    
    def _generate_report(self, context: AgentContext) -> Dict:
        """
        Generate comprehensive report from all agent results
        """
        report = {
            'command': context.command,
            'timestamp': context.timestamp.isoformat(),
            'agents_involved': list(context.results.keys()),
            'success': len(context.errors) == 0,
            'errors': context.errors,
            'suggestions': context.suggestions,
            'metrics': context.metrics,
            'detailed_results': context.results
        }
        
        return report

# ============================================
# PART 2: AGENT SELF-ASSESSMENT CAPABILITIES
# ============================================

class BaseAgent:
    """
    Base class for all autonomous agents with self-assessment
    """
    
    def __init__(self):
        self.name = None
        self.message_bus = None
        self.keywords = []
        self.patterns = []
        self.capabilities = []
        self.dependencies = []
        
    def set_message_bus(self, message_bus):
        """Connect to message bus for inter-agent communication"""
        self.message_bus = message_bus
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events from other agents"""
        # Override in subclasses
        pass
    
    async def analyze_relevance(self, command: str) -> Dict:
        """
        Self-assessment: Determine if this agent should help
        Returns confidence score and capabilities
        """
        relevance_score = 0
        matched_keywords = []
        matched_patterns = []
        
        # Check keywords
        command_lower = command.lower()
        for keyword in self.keywords:
            if keyword in command_lower:
                relevance_score += 20
                matched_keywords.append(keyword)
        
        # Check patterns
        for pattern in self.patterns:
            if re.search(pattern, command, re.IGNORECASE):
                relevance_score += 30
                matched_patterns.append(pattern)
        
        # Check context (recent changes, etc.)
        context_score = self._assess_context()
        relevance_score += context_score
        
        # Determine if we should help
        can_help = relevance_score >= 50
        
        return {
            'can_help': can_help,
            'confidence': min(relevance_score, 100),
            'matched_keywords': matched_keywords,
            'matched_patterns': matched_patterns,
            'capabilities': self.capabilities if can_help else [],
            'dependencies': self.dependencies,
            'priority': self._determine_priority(relevance_score)
        }
    
    def _assess_context(self) -> int:
        """
        Assess contextual relevance (override in subclasses)
        """
        return 0
    
    def _determine_priority(self, relevance_score: int) -> AgentPriority:
        """
        Determine execution priority based on relevance
        """
        if relevance_score >= 90:
            return AgentPriority.HIGH
        elif relevance_score >= 70:
            return AgentPriority.MEDIUM
        else:
            return AgentPriority.LOW
    
    async def execute(self, context: AgentContext) -> Dict:
        """
        Execute agent's main function (override in subclasses)
        """
        raise NotImplementedError
    
    def receive_message(self, message: Dict):
        """
        Handle messages from other agents
        """
        # Override in subclasses to handle specific messages
        pass

# ============================================
# PART 3: INTER-AGENT COMMUNICATION PROTOCOL
# ============================================

class MessageBus:
    """
    Central message bus for inter-agent communication
    Implements publish-subscribe pattern
    """
    
    def __init__(self):
        self.subscribers = {}
        self.message_history = []
        self.max_history = 1000
    
    def subscribe(self, agent_name: str, events: List[str]):
        """
        Agent subscribes to specific event types
        """
        for event in events:
            if event not in self.subscribers:
                self.subscribers[event] = []
            if agent_name not in self.subscribers[event]:
                self.subscribers[event].append(agent_name)
        
        logger.debug(f"📡 {agent_name} subscribed to {events}")
    
    def unsubscribe(self, agent_name: str, event: str):
        """
        Agent unsubscribes from an event
        """
        if event in self.subscribers:
            if agent_name in self.subscribers[event]:
                self.subscribers[event].remove(agent_name)
    
    def publish(self, sender: str, event: str, data: Any):
        """
        Agent publishes an event to the bus
        """
        message = {
            'id': len(self.message_history),
            'sender': sender,
            'event': event,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        # Notify subscribers
        if event in self.subscribers:
            for subscriber in self.subscribers[event]:
                self._deliver_message(subscriber, message)
        
        # Also check for wildcard subscribers
        if '*' in self.subscribers:
            for subscriber in self.subscribers['*']:
                if subscriber != sender:  # Don't send to self
                    self._deliver_message(subscriber, message)
        
        logger.debug(f"📬 {sender} published {event}")
    
    def _deliver_message(self, recipient: str, message: Dict):
        """
        Deliver message to specific agent
        """
        # In real implementation, this would call agent's receive_message
        # For now, just log it
        logger.debug(f"📨 Delivered to {recipient}: {message['event']}")
    
    def query_history(self, filter_func=None) -> List[Dict]:
        """
        Query message history with optional filter
        """
        if filter_func:
            return [m for m in self.message_history if filter_func(m)]
        return self.message_history.copy()

class AgentMessage:
    """
    Structured message format for inter-agent communication
    """
    
    def __init__(self, sender: str, recipient: str, message_type: str, content: Any):
        self.id = None
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.content = content
        self.timestamp = datetime.now()
        self.requires_response = False
        self.response_timeout = 30  # seconds
        
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'requires_response': self.requires_response
        }

# ============================================
# PART 4: AUTOMATIC TRIGGER MECHANISMS
# ============================================

class TriggerManager:
    """
    Manages automatic agent activation based on various triggers
    """
    
    def __init__(self, coordinator: AgentCoordinator):
        self.coordinator = coordinator
        self.triggers = []
        self.file_watchers = {}
        self.event_handlers = {}
        self.active = False
        
        self._setup_triggers()
    
    def _setup_triggers(self):
        """
        Define all automatic triggers
        """
        self.triggers = [
            FileTrigger(
                pattern="*.css",
                agents=['ui_ux', 'performance'],
                priority=AgentPriority.HIGH
            ),
            FileTrigger(
                pattern="*.html",
                agents=['ui_ux', 'qa'],
                priority=AgentPriority.HIGH
            ),
            FileTrigger(
                pattern="*.py",
                agents=['implementation', 'qa', 'security'],
                priority=AgentPriority.MEDIUM
            ),
            KeywordTrigger(
                keywords=['fix', 'bug', 'error', 'broken'],
                agents=['implementation', 'qa'],
                priority=AgentPriority.IMMEDIATE
            ),
            KeywordTrigger(
                keywords=['slow', 'performance', 'optimize'],
                agents=['performance', 'implementation'],
                priority=AgentPriority.HIGH
            ),
            KeywordTrigger(
                keywords=['ui', 'ux', 'design', 'layout', 'color'],
                agents=['ui_ux'],
                priority=AgentPriority.MEDIUM
            ),
            EventTrigger(
                event='deployment_requested',
                agents=['qa', 'security', 'performance'],
                priority=AgentPriority.IMMEDIATE
            )
        ]
    
    def start(self):
        """
        Start monitoring for triggers
        """
        self.active = True
        logger.info("🚀 Trigger Manager activated")
        
        # Start file watchers
        self._start_file_watchers()
        
        # Start event listeners
        self._start_event_listeners()
    
    def stop(self):
        """
        Stop all monitoring
        """
        self.active = False
        
        # Stop file watchers
        for watcher in self.file_watchers.values():
            watcher.stop()
        
        logger.info("🛑 Trigger Manager deactivated")
    
    def _start_file_watchers(self):
        """
        Start watching for file changes
        """
        # Implementation would use watchdog or similar
        pass
    
    def _start_event_listeners(self):
        """
        Start listening for system events
        """
        # Implementation would listen to git hooks, IDE events, etc.
        pass
    
    async def check_triggers(self, context: Dict) -> List[str]:
        """
        Check if any triggers match the current context
        Returns list of agents to activate
        """
        activated_agents = set()
        
        for trigger in self.triggers:
            if trigger.matches(context):
                activated_agents.update(trigger.agents)
        
        return list(activated_agents)

class Trigger:
    """
    Base class for all trigger types
    """
    
    def __init__(self, agents: List[str], priority: AgentPriority):
        self.agents = agents
        self.priority = priority
    
    def matches(self, context: Dict) -> bool:
        """
        Check if trigger conditions are met
        """
        raise NotImplementedError

class FileTrigger(Trigger):
    """
    Trigger based on file changes
    """
    
    def __init__(self, pattern: str, agents: List[str], priority: AgentPriority):
        super().__init__(agents, priority)
        self.pattern = pattern
    
    def matches(self, context: Dict) -> bool:
        if 'file_changed' in context:
            from fnmatch import fnmatch
            return fnmatch(context['file_changed'], self.pattern)
        return False

class KeywordTrigger(Trigger):
    """
    Trigger based on keywords in command
    """
    
    def __init__(self, keywords: List[str], agents: List[str], priority: AgentPriority):
        super().__init__(agents, priority)
        self.keywords = keywords
    
    def matches(self, context: Dict) -> bool:
        if 'command' in context:
            command_lower = context['command'].lower()
            return any(keyword in command_lower for keyword in self.keywords)
        return False

class EventTrigger(Trigger):
    """
    Trigger based on system events
    """
    
    def __init__(self, event: str, agents: List[str], priority: AgentPriority):
        super().__init__(agents, priority)
        self.event = event
    
    def matches(self, context: Dict) -> bool:
        return context.get('event') == self.event

# ============================================
# USAGE INTERFACE
# ============================================

class AutonomousAgentSystem:
    """
    Main interface for the autonomous agent system
    """
    
    def __init__(self):
        self.coordinator = AgentCoordinator()
        self.trigger_manager = TriggerManager(self.coordinator)
        self.active = False
    
    def start(self):
        """
        Activate the autonomous agent system
        """
        self.active = True
        self.trigger_manager.start()
        logger.info("✨ Autonomous Agent System ACTIVE")
        logger.info("All agents are now listening and ready to collaborate")
    
    def stop(self):
        """
        Deactivate the system
        """
        self.active = False
        self.trigger_manager.stop()
        logger.info("💤 Autonomous Agent System INACTIVE")
    
    async def process(self, command: str) -> Dict:
        """
        Process a user command through the autonomous system
        """
        if not self.active:
            logger.warning("System not active. Starting...")
            self.start()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 USER COMMAND: {command}")
        logger.info(f"{'='*60}\n")
        
        # All agents analyze and collaborate automatically
        context = await self.coordinator.process_command(command)
        
        # Generate user-friendly report
        report = self._format_report(context)
        
        return report
    
    def _format_report(self, context: AgentContext) -> Dict:
        """
        Format results for user consumption
        """
        report = {
            'summary': self._generate_summary(context),
            'actions_taken': self._list_actions(context),
            'issues_found': context.errors,
            'suggestions': context.suggestions,
            'metrics': context.metrics
        }
        
        # Print formatted output
        print("\n" + "="*60)
        print("📊 AUTONOMOUS AGENT REPORT")
        print("="*60)
        
        print(f"\n✨ Summary: {report['summary']}")
        
        if report['actions_taken']:
            print("\n📋 Actions Taken:")
            for action in report['actions_taken']:
                print(f"  ✓ {action}")
        
        if report['issues_found']:
            print("\n⚠️ Issues Found:")
            for issue in report['issues_found']:
                print(f"  • {issue}")
        
        if report['suggestions']:
            print("\n💡 Suggestions:")
            for suggestion in report['suggestions']:
                print(f"  • {suggestion}")
        
        print("\n" + "="*60)
        
        return report
    
    def _generate_summary(self, context: AgentContext) -> str:
        """
        Generate executive summary
        """
        num_agents = len(context.results)
        success = len(context.errors) == 0
        
        if success:
            return f"{num_agents} agents collaborated successfully to address your request"
        else:
            return f"{num_agents} agents encountered {len(context.errors)} issues while addressing your request"
    
    def _list_actions(self, context: AgentContext) -> List[str]:
        """
        List all actions taken by agents
        """
        actions = []
        for agent_name, result in context.results.items():
            if isinstance(result, dict) and 'result' in result:
                agent_result = result['result']
                if isinstance(agent_result, dict) and 'action' in agent_result:
                    actions.append(f"{agent_name}: {agent_result['action']}")
        return actions

# ============================================
# QUICK START FUNCTION
# ============================================

async def autonomous_command(command: str):
    """
    Quick function to process a command with autonomous agents
    """
    system = AutonomousAgentSystem()
    system.start()
    result = await system.process(command)
    return result

# Example usage
if __name__ == "__main__":
    # Test the system
    import asyncio
    
    async def test():
        # This would automatically trigger UI/UX, Implementation, and QA agents
        result = await autonomous_command("The curriculum column is too wide")
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())