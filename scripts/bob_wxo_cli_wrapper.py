#!/usr/bin/env python3
"""
Bob-shell WXO CLI Wrapper
Uses the orchestrate CLI commands that work correctly with authentication
"""

import subprocess
import json
import sys
import time
from typing import Dict, Any, Optional


class WXOCLIWrapper:
    """Wrapper around orchestrate CLI for reliable WXO operations"""
    
    def list_agents(self) -> Dict[str, Any]:
        """List all available agents using orchestrate CLI"""
        try:
            result = subprocess.run(
                ['orchestrate', 'agents', 'list'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {'error': result.stderr, 'success': False}
            
            # Parse the table output - look for lines with agent data
            lines = result.stdout.strip().split('\n')
            agents = []
            in_data = False
            
            for line in lines:
                # Start parsing after the header separator
                if line.startswith('┡'):
                    in_data = True
                    continue
                
                # Stop at the bottom border
                if line.startswith('└'):
                    break
                
                # Parse data rows
                if in_data and '│' in line:
                    # Split by │ and clean up
                    parts = [p.strip() for p in line.split('│')]
                    # Remove empty first and last elements from split
                    parts = [p for p in parts if p]
                    
                    if len(parts) >= 1 and parts[0]:
                        agents.append({
                            'name': parts[0],
                            'display_name': parts[1] if len(parts) > 1 else '',
                            'description': parts[2] if len(parts) > 2 else '',
                            'llm': parts[3] if len(parts) > 3 else ''
                        })
            
            return {
                'success': True,
                'agent_count': len(agents),
                'agents': agents
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def trigger_agent_via_mcp(self, agent_name: str, user_input: str) -> Dict[str, Any]:
        """
        Trigger an agent using the MCP server tools
        This uses the working MCP integration
        """
        try:
            # Create a Python script that uses the MCP tool
            script = f"""
import sys
import os
# Add project root to path
sys.path.insert(0, '/Users/thadchaisaenprasert/Desktop/work/SuperBob')
from superbob.tools.wxo_trigger import trigger_wxo_agent

result = trigger_wxo_agent('{agent_name}', '''{user_input}''')
import json
print(json.dumps(result))
"""
            
            result = subprocess.run(
                ['python3', '-c', script],
                capture_output=True,
                text=True,
                timeout=120,
                cwd='/Users/thadchaisaenprasert/Desktop/work/SuperBob'
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr,
                    'agent_name': agent_name
                }
            
            return json.loads(result.stdout)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent_name': agent_name
            }
    
    def export_agent(self, agent_name: str, output_path: str) -> Dict[str, Any]:
        """Export an agent using orchestrate CLI"""
        try:
            result = subprocess.run(
                ['orchestrate', 'agents', 'export', '-n', agent_name, '-o', output_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {'error': result.stderr, 'success': False}
            
            return {
                'success': True,
                'agent_name': agent_name,
                'output_path': output_path,
                'message': result.stdout
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("""
Usage:
  python bob_wxo_cli_wrapper.py list
  python bob_wxo_cli_wrapper.py trigger <agent_name> <message>
  python bob_wxo_cli_wrapper.py export <agent_name> <output_path>

Examples:
  python bob_wxo_cli_wrapper.py list
  python bob_wxo_cli_wrapper.py trigger SuperBob_2079Hm "Search for AI news"
  python bob_wxo_cli_wrapper.py export SuperBob_2079Hm ./agent.zip
""")
        sys.exit(1)
    
    try:
        wrapper = WXOCLIWrapper()
        command = sys.argv[1]
        
        if command == 'list':
            result = wrapper.list_agents()
            print(json.dumps(result, indent=2))
        
        elif command == 'trigger':
            if len(sys.argv) < 4:
                print("Error: trigger requires agent_name and message")
                sys.exit(1)
            
            agent_name = sys.argv[2]
            message = sys.argv[3]
            
            result = wrapper.trigger_agent_via_mcp(agent_name, message)
            print(json.dumps(result, indent=2))
        
        elif command == 'export':
            if len(sys.argv) < 4:
                print("Error: export requires agent_name and output_path")
                sys.exit(1)
            
            agent_name = sys.argv[2]
            output_path = sys.argv[3]
            
            result = wrapper.export_agent(agent_name, output_path)
            print(json.dumps(result, indent=2))
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(json.dumps({'error': str(e)}, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
