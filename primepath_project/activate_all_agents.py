#!/usr/bin/env python
"""
ACTIVATE ALL AGENT SUBSYSTEMS
This script properly initializes and tests all autonomous agent subsystems
"""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from agent_system import AutonomousAgentSystem

async def activate_all_agents():
    """Activate and test all agent subsystems"""
    
    print("=" * 80)
    print("🤖 ACTIVATING ALL AUTONOMOUS AGENT SUBSYSTEMS")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 80)
    
    # Initialize the system
    system = AutonomousAgentSystem()
    system.start()
    
    print("\n✅ Agent System Initialized")
    print("\nAvailable Agents:")
    
    # List all available agent types
    agent_types = [
        "UI/UX Review Agent",
        "Implementation Agent",
        "QA Test Agent",
        "Performance Agent",
        "Documentation Agent",
        "Security Agent"
    ]
    
    for agent_type in agent_types:
        print(f"  • {agent_type}: Ready")
    
    # Test commands for each subsystem
    test_scenarios = {
        "UI/UX Review": "Review the overall UI/UX design and layout",
        "Implementation": "Check for any implementation issues or bugs",
        "QA Testing": "Run comprehensive quality assurance tests",
        "Performance": "Analyze system performance and optimization opportunities",
        "Documentation": "Review and update documentation",
        "Security": "Perform security audit and permission checks"
    }
    
    print("\n" + "=" * 80)
    print("🧪 TESTING AGENT SUBSYSTEMS")
    print("=" * 80)
    
    results = {}
    for name, command in test_scenarios.items():
        print(f"\n📌 Testing: {name}")
        print(f"   Command: {command}")
        print("   " + "-" * 40)
        
        try:
            # Process through agent system
            result = await system.process(command)
            
            if result and 'agents' in result:
                active_agents = result['agents']
                print(f"   ✅ Activated {len(active_agents)} agent(s)")
                for agent in active_agents:
                    print(f"      - {agent.get('type', 'Unknown')}")
                results[name] = "SUCCESS"
            else:
                print(f"   ⚠️ No agents activated")
                results[name] = "NO_ACTIVATION"
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[name] = f"ERROR: {str(e)}"
    
    # Summary report
    print("\n" + "=" * 80)
    print("📊 ACTIVATION SUMMARY REPORT")
    print("=" * 80)
    
    success_count = sum(1 for v in results.values() if v == "SUCCESS")
    total_count = len(results)
    
    print(f"\nOverall Status: {success_count}/{total_count} subsystems activated successfully")
    print("\nDetailed Results:")
    for name, status in results.items():
        icon = "✅" if status == "SUCCESS" else "❌" if "ERROR" in status else "⚠️"
        print(f"  {icon} {name}: {status}")
    
    # Save status report
    status_file = Path(__file__).parent / "agent_system" / "activation_status.json"
    status_data = {
        "timestamp": datetime.now().isoformat(),
        "status": "ACTIVE" if success_count > 0 else "INACTIVE",
        "subsystems": results,
        "summary": {
            "total": total_count,
            "active": success_count,
            "inactive": total_count - success_count
        }
    }
    
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"\n📁 Status report saved to: {status_file}")
    
    print("\n" + "=" * 80)
    if success_count == total_count:
        print("🎉 ALL AGENT SUBSYSTEMS FULLY ACTIVATED AND OPERATIONAL!")
    elif success_count > 0:
        print(f"⚠️ PARTIAL ACTIVATION: {success_count}/{total_count} subsystems active")
    else:
        print("❌ ACTIVATION FAILED: No subsystems activated")
    print("=" * 80)
    
    return status_data

def main():
    """Main entry point"""
    try:
        # Run the async function
        result = asyncio.run(activate_all_agents())
        
        # Exit with appropriate code
        if result['summary']['active'] == result['summary']['total']:
            sys.exit(0)  # Full success
        elif result['summary']['active'] > 0:
            sys.exit(1)  # Partial success
        else:
            sys.exit(2)  # Complete failure
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Activation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error during activation: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()