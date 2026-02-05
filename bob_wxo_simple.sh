#!/bin/bash
# Simple Bob-shell wrapper for WXO operations using MCP tools

case "$1" in
  list)
    # List agents using MCP
    python3 -c "
import sys
sys.path.insert(0, '/Users/thadchaisaenprasert/Desktop/work/SuperBob')
from wxo_agent_trigger_tool import list_wxo_agents
import json
result = list_wxo_agents()
print(json.dumps(result, indent=2))
"
    ;;
  
  trigger)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: $0 trigger <agent_name> <message>"
      exit 1
    fi
    # Trigger agent using MCP
    python3 -c "
import sys
sys.path.insert(0, '/Users/thadchaisaenprasert/Desktop/work/SuperBob')
from wxo_agent_trigger_tool import trigger_wxo_agent
import json
result = trigger_wxo_agent('$2', '''$3''')
print(json.dumps(result, indent=2))
"
    ;;
  
  status)
    if [ -z "$2" ]; then
      echo "Usage: $0 status <run_id>"
      exit 1
    fi
    # Check status using MCP
    python3 -c "
import sys
sys.path.insert(0, '/Users/thadchaisaenprasert/Desktop/work/SuperBob')
from wxo_agent_trigger_tool import get_wxo_agent_status
import json
result = get_wxo_agent_status('$2')
print(json.dumps(result, indent=2))
"
    ;;
  
  *)
    echo "Usage: $0 {list|trigger|status}"
    echo ""
    echo "Commands:"
    echo "  list                          - List all WXO agents"
    echo "  trigger <agent> <message>     - Trigger an agent with a message"
    echo "  status <run_id>               - Check status of a run"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 trigger SuperBob_2079Hm 'Search for AI news'"
    echo "  $0 status abc123-run-id"
    exit 1
    ;;
esac
