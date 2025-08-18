"""
AUTONOMOUS AGENT INTEGRATION MODULE
This module provides the interface for Claude to automatically use agents
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_system import AutonomousAgentSystem, AgentRegistry

# Global system instance (singleton)
_agent_system = None

def get_agent_system() -> AutonomousAgentSystem:
    """Get or create the singleton agent system"""
    global _agent_system
    if _agent_system is None:
        _agent_system = AutonomousAgentSystem()
        _agent_system.start()
        print("🤖 Autonomous Agent System initialized and ready")
    return _agent_system

def process_with_agents(user_command: str) -> Dict[str, Any]:
    """
    Main entry point for Claude to process user commands through agents
    This function should be called for EVERY user request
    """
    print("\n" + "="*80)
    print("🤖 AUTONOMOUS AGENT SYSTEM PROCESSING")
    print("="*80)
    print(f"📨 User Command: {user_command}")
    print("-"*80)
    
    # Check if this command should trigger agents
    if should_use_agents(user_command):
        print("✅ Agents activated for this request")
        
        # Get the system
        system = get_agent_system()
        
        # Process through agents
        try:
            # Run async function in sync context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running (in Jupyter/Claude), create task
                task = asyncio.create_task(system.process(user_command))
                result = asyncio.run_coroutine_threadsafe(
                    system.process(user_command),
                    loop
                ).result()
            else:
                # Normal execution
                result = asyncio.run(system.process(user_command))
            
            # Format for Claude
            return format_for_claude(result)
            
        except Exception as e:
            print(f"❌ Error in agent processing: {e}")
            return {
                'error': str(e),
                'fallback': 'Manual processing required',
                'command': user_command
            }
    else:
        print("ℹ️ Command doesn't require agent collaboration")
        return {
            'action': 'manual',
            'reason': 'No agent keywords detected',
            'command': user_command
        }

def should_use_agents(command: str) -> bool:
    """
    Determine if agents should be activated for this command
    """
    # Always use agents for these keywords
    agent_triggers = [
        # UI/UX
        'ui', 'ux', 'design', 'layout', 'color', 'spacing', 'wide', 'narrow',
        'responsive', 'mobile', 'desktop', 'display', 'visual', 'theme',
        
        # Implementation
        'fix', 'add', 'change', 'update', 'implement', 'create', 'build',
        'bug', 'error', 'issue', 'problem', 'broken', 'wrong',
        
        # Features
        'feature', 'enhancement', 'improvement', 'new',
        
        # Testing
        'test', 'verify', 'check', 'ensure', 'quality', 'qa',
        
        # Performance
        'slow', 'fast', 'performance', 'optimize', 'speed',
        
        # General development
        'code', 'develop', 'refactor', 'clean'
    ]
    
    command_lower = command.lower()
    
    # Check if any trigger word is in the command
    for trigger in agent_triggers:
        if trigger in command_lower:
            return True
    
    return False

def format_for_claude(agent_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format agent results for Claude to understand and act upon
    """
    formatted = {
        'timestamp': datetime.now().isoformat(),
        'agents_involved': [],
        'actions_to_take': [],
        'code_changes': [],
        'warnings': [],
        'testing_required': [],
        'command_processed': True
    }
    
    # Extract key information from agent results
    if 'actions_taken' in agent_result:
        formatted['agents_involved'] = agent_result['actions_taken']
    
    if 'suggestions' in agent_result:
        formatted['actions_to_take'] = agent_result['suggestions']
    
    if 'issues_found' in agent_result:
        formatted['warnings'] = agent_result['issues_found']
    
    # Add specific implementation details
    if 'detailed_results' in agent_result:
        for agent_name, result in agent_result['detailed_results'].items():
            if 'implementation' in agent_name and 'result' in result:
                impl_result = result['result']
                if 'changes_made' in impl_result:
                    formatted['code_changes'].extend(impl_result['changes_made'])
                if 'files_modified' in impl_result:
                    formatted['files_to_modify'] = impl_result['files_modified']
            
            elif 'qa' in agent_name and 'result' in result:
                qa_result = result['result']
                if 'tests_run' in qa_result:
                    formatted['testing_required'].append({
                        'type': 'automated',
                        'tests': qa_result['tests_run'],
                        'passed': qa_result.get('tests_passed', 0)
                    })
    
    # Print summary for Claude
    print("\n" + "="*80)
    print("📋 AGENT RECOMMENDATIONS FOR CLAUDE:")
    print("="*80)
    
    if formatted['actions_to_take']:
        print("\n🎯 Actions to implement:")
        for i, action in enumerate(formatted['actions_to_take'], 1):
            print(f"  {i}. {action}")
    
    if formatted['code_changes']:
        print("\n💻 Code changes required:")
        for change in formatted['code_changes']:
            if isinstance(change, dict):
                print(f"  • {change.get('type', 'change')}: {change.get('description', change)}")
            else:
                print(f"  • {change}")
    
    if formatted['warnings']:
        print("\n⚠️ Warnings:")
        for warning in formatted['warnings']:
            print(f"  • {warning}")
    
    print("\n" + "="*80)
    
    return formatted

def check_agent_status():
    """
    Check if agents are ready and working
    """
    print("🔍 Checking Autonomous Agent System...")
    
    try:
        system = get_agent_system()
        
        print("✅ Agent system is active")
        print("\nAvailable agents:")
        
        for agent_type, info in AgentRegistry.get_all_agents().items():
            print(f"  • {info['name']}: Ready")
        
        print("\n✅ All agents are ready to collaborate!")
        return True
        
    except Exception as e:
        print(f"❌ Agent system error: {e}")
        return False

def quick_process(command: str):
    """
    Quick synchronous wrapper for command line usage
    """
    result = process_with_agents(command)
    
    # Save result to file for Claude to read
    output_file = os.path.join(
        os.path.dirname(__file__),
        'last_agent_result.json'
    )
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📁 Full results saved to: {output_file}")
    
    return result

# ============================================
# COMMAND LINE INTERFACE
# ============================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Process command from command line
        command = " ".join(sys.argv[1:])
        quick_process(command)
    else:
        # Interactive mode
        print("🤖 Autonomous Agent System - Interactive Mode")
        print("Type 'exit' to quit")
        print("-"*50)
        
        while True:
            command = input("\n> ").strip()
            
            if command.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            if command:
                process_with_agents(command)
            else:
                print("Please enter a command")