#!/usr/bin/env python
"""
MAIN REQUEST PROCESSOR FOR CLAUDE
This file should be called FIRST for any user request

Usage in Claude:
    When user asks to fix/add/change anything:
    1. Run: python PROCESS_REQUEST.py "user's exact command"
    2. Follow the agent recommendations
    3. Implement the suggested changes
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for agent_system imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from agent_system.integration import process_with_agents
except ImportError:
    print("⚠️ Agent system not found. Creating fallback...")
    # Fallback if agent system doesn't exist yet
    def process_with_agents(command):
        return {
            "status": "fallback",
            "message": "Agent system initializing...",
            "command": command,
            "timestamp": datetime.now().isoformat()
        }

def main():
    if len(sys.argv) < 2:
        print("❌ Error: No command provided")
        print("Usage: python PROCESS_REQUEST.py 'user command here'")
        sys.exit(1)
    
    # Get the user's command
    user_command = " ".join(sys.argv[1:])
    
    print("\n" + "🤖"*20)
    print("AUTONOMOUS AGENT SYSTEM ACTIVATED")
    print("🤖"*20)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"Processing: {user_command}")
    print("-"*80)
    
    # Process through agents
    result = process_with_agents(user_command)
    
    # Save for reference
    output_file = "agent_recommendations.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📁 Recommendations saved to: {output_file}")
    
    # Provide clear instructions for Claude
    print("\n" + "="*80)
    print("📋 INSTRUCTIONS FOR CLAUDE:")
    print("="*80)
    
    # Handle new agent system format
    if result.get('action_items'):
        print("\n✅ IMPLEMENT THESE CHANGES:")
        for i, action in enumerate(result['action_items'], 1):
            print(f"   {i}. {action.get('action', 'No action')}")
            if 'command' in action:
                print(f"      Command: {action['command']}")
    
    # Legacy format support
    elif result.get('actions_to_take'):
        print("\n✅ IMPLEMENT THESE CHANGES:")
        for i, action in enumerate(result['actions_to_take'], 1):
            print(f"   {i}. {action}")
    
    if result.get('files_to_modify'):
        print("\n📁 FILES TO MODIFY:")
        for file in result['files_to_modify']:
            print(f"   • {file}")
    
    if result.get('warnings'):
        print("\n⚠️ WATCH OUT FOR:")
        for warning in result['warnings']:
            print(f"   • {warning}")
    
    print("\n" + "="*80)
    print("🎯 NEXT STEPS:")
    print("1. Implement the recommended changes")
    print("2. Agents will automatically review your work")
    print("3. Report back to user with results")
    print("="*80)
    
    return result

if __name__ == "__main__":
    main()