"""
Watsonx Orchestrate Agent Trigger Tool
Allows triggering and interacting with watsonx Orchestrate agents
Uses WXO SDK internal APIs available in the agent execution environment
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Dict, Any, Optional, List


@tool(
    name="trigger_wxo_agent",
    display_name="Trigger WXO Agent",
    description="Trigger a watsonx Orchestrate agent by name and send it a message. Returns the agent's response. Use this to delegate tasks to specialized agents in your watsonx Orchestrate environment."
)
def trigger_wxo_agent(agent_name: str, user_input: str, wait_for_response: bool = True, timeout: int = 60) -> Dict[str, Any]:
    """
    Trigger a watsonx Orchestrate agent and get its response.
    
    Args:
        agent_name: The name of the agent to trigger (e.g., 'SuperBob_2079Hm')
        user_input: The message/input to send to the agent
        wait_for_response: Whether to wait for the agent's response (default: True)
        timeout: Maximum time to wait for response in seconds (default: 60)
    
    Returns:
        Dictionary containing the agent's response and run information
    """
    try:
        # Import WXO SDK components available in agent execution environment
        from ibm_watsonx_orchestrate.helpers.config_helper import get_active_config
        from ibm_watsonx_orchestrate.client.orchestrate_api_client import OrchestrateAPIClient
        import time
        
        # Get the active configuration
        config = get_active_config()
        
        # Create orchestrate client
        client = OrchestrateAPIClient(config.url, authenticator=config.authenticator)
        
        # Start the agent run
        run_data = client.create_run(agent_name=agent_name, user_input=user_input)
        run_id = run_data.get('id')
        
        if not wait_for_response:
            return {
                'success': True,
                'agent_name': agent_name,
                'run_id': run_id,
                'status': 'started',
                'message': f'Agent {agent_name} started successfully'
            }
        
        # Poll for the response
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_data = client.get_run_status(run_id)
            run_status = status_data.get('status')
            
            if run_status == 'completed':
                output = status_data.get('output', {})
                return {
                    'success': True,
                    'agent_name': agent_name,
                    'run_id': run_id,
                    'status': 'completed',
                    'response': output.get('text', ''),
                    'full_output': output
                }
            elif run_status == 'failed':
                return {
                    'success': False,
                    'agent_name': agent_name,
                    'run_id': run_id,
                    'status': 'failed',
                    'error': status_data.get('error', 'Agent run failed')
                }
            
            # Wait before polling again
            time.sleep(2)
        
        return {
            'success': False,
            'agent_name': agent_name,
            'run_id': run_id,
            'status': 'timeout',
            'error': f'Agent did not complete within {timeout} seconds'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Agent trigger error: {str(e)}',
            'agent_name': agent_name
        }


@tool(
    name="list_wxo_agents",
    display_name="List WXO Agents",
    description="List all available agents in your watsonx Orchestrate environment. Returns agent names, descriptions, and capabilities."
)
def list_wxo_agents() -> Dict[str, Any]:
    """
    List all available watsonx Orchestrate agents using the SDK.
    
    Returns:
        Dictionary containing list of agents with their details
    """
    try:
        # Import WXO SDK components available in agent execution environment
        from ibm_watsonx_orchestrate.helpers.config_helper import get_active_config
        from ibm_watsonx_orchestrate.client.agents_api_client import AgentsAPIClient
        
        # Get the active configuration
        config = get_active_config()
        
        # Create agents client
        client = AgentsAPIClient(config.url, authenticator=config.authenticator)
        
        # Get list of agents
        agents_data = client.list_agents()
        
        # Extract native agents
        native_agents = agents_data.get('native', [])
        
        # Format agent information
        agents = []
        for agent in native_agents:
            agents.append({
                'name': agent.get('name'),
                'display_name': agent.get('display_name'),
                'description': agent.get('description'),
                'llm': agent.get('llm'),
                'style': agent.get('style'),
                'tools': agent.get('tools', []),
                'knowledge_base': agent.get('knowledge_base', [])
            })
        
        return {
            'success': True,
            'agent_count': len(agents),
            'agents': agents
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'List agents error: {str(e)}'
        }


@tool(
    name="get_wxo_agent_status",
    display_name="Get WXO Agent Run Status",
    description="Check the status of a running agent by its run ID. Use this to monitor long-running agent tasks."
)
def get_wxo_agent_status(run_id: str) -> Dict[str, Any]:
    """
    Get the status of a watsonx Orchestrate agent run.
    
    Args:
        run_id: The ID of the agent run to check
    
    Returns:
        Dictionary containing the run status and output if completed
    """
    try:
        # Import WXO SDK components available in agent execution environment
        from ibm_watsonx_orchestrate.helpers.config_helper import get_active_config
        from ibm_watsonx_orchestrate.client.orchestrate_api_client import OrchestrateAPIClient
        
        # Get the active configuration
        config = get_active_config()
        
        # Create orchestrate client
        client = OrchestrateAPIClient(config.url, authenticator=config.authenticator)
        
        # Get run status
        status_data = client.get_run_status(run_id)
        
        return {
            'success': True,
            'run_id': run_id,
            'status': status_data.get('status'),
            'agent_name': status_data.get('agent', {}).get('name'),
            'output': status_data.get('output', {}),
            'created_at': status_data.get('created_at'),
            'updated_at': status_data.get('updated_at')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Status check error: {str(e)}',
            'run_id': run_id
        }
