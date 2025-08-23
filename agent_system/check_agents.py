#!/usr/bin/env python3
"""
Agent System Status Checker
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_system.integration import check_agents, process_with_agents

def main():
    """Main entry point for checking agent status"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check Agent System Status")
    parser.add_argument("--process", type=str, help="Process a request through agents")
    parser.add_argument("--status", action="store_true", help="Show agent status")
    
    args = parser.parse_args()
    
    if args.process:
        # Process a request
        print(f"\nProcessing request: {args.process}")
        process_with_agents(args.process)
    else:
        # Default to showing status
        check_agents()
        print("\nAgent system is ready to process requests.")
        print("Use: python check_agents.py --process 'your request here'")

if __name__ == "__main__":
    main()