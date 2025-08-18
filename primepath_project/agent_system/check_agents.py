#!/usr/bin/env python
"""
CHECK AUTONOMOUS AGENT STATUS
Quick script to verify agents are ready
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_system.integration import check_agent_status, process_with_agents

def main():
    print("\n" + "="*80)
    print("🤖 AUTONOMOUS AGENT SYSTEM STATUS CHECK")
    print("="*80)
    
    # Check if system is ready
    if check_agent_status():
        print("\n✅ System is READY for autonomous operation")
        print("\nTest command processing:")
        print("-"*40)
        
        # Test with a sample command
        test_command = "Check if the curriculum column width is appropriate"
        print(f"Test: '{test_command}'")
        
        result = process_with_agents(test_command)
        
        if result.get('command_processed'):
            print("\n✅ Agents successfully processed test command")
        else:
            print("\n⚠️ Agents did not process command")
    else:
        print("\n❌ System is NOT ready")
        print("Please check the error messages above")
    
    print("\n" + "="*80)
    print("Instructions for Claude:")
    print("-"*40)
    print("1. For EVERY user request, first run:")
    print("   python agent_system/integration.py 'user command here'")
    print("\n2. Agents will provide recommendations")
    print("\n3. Implement the recommendations")
    print("\n4. Agents will automatically review your work")
    print("="*80)

if __name__ == "__main__":
    main()