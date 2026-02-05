#!/usr/bin/env python3
"""
Bob-shell WXO Agent Trigger Tool
Direct API integration for triggering watsonx Orchestrate agents from Bob-shell
Usage: python -m superbob.cli <command> [options]
"""

import requests
import json
import subprocess
import time
import sys
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


CREDENTIALS_PATH = Path.home() / '.cache' / 'orchestrate' / 'credentials.yaml'


class WXOAgentTrigger:
    """Direct API client for watsonx Orchestrate agents"""

    def __init__(self):
        self.api_endpoint = os.environ.get('WXO_INSTANCE')
        if not self.api_endpoint:
            raise ValueError("WXO_INSTANCE environment variable must be set")

        self.token = self._load_mcsp_token()
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def _load_mcsp_token(self) -> str:
        """Load MCSP token from orchestrate credentials cache."""
        if not CREDENTIALS_PATH.exists():
            raise ValueError(
                f"Credentials file not found at {CREDENTIALS_PATH}. "
                "Run 'orchestrate env activate remote' first."
            )

        with open(CREDENTIALS_PATH) as f:
            creds = yaml.safe_load(f)

        env_name = os.environ.get('WXO_ENVIRONMENT', 'remote')
        auth = creds.get('auth', {})
        env_auth = auth.get(env_name, {})

        if not env_auth:
            raise ValueError(
                f"No credentials found for environment '{env_name}'. "
                "Run 'orchestrate env activate {env_name}' first."
            )

        token = env_auth.get('wxo_mcsp_token')
        if not token:
            raise ValueError(
                f"No wxo_mcsp_token found for environment '{env_name}'."
            )

        expiry = env_auth.get('wxo_mcsp_token_expiry', 0)
        if time.time() > expiry:
            token = self._refresh_token(env_name)
            if not token:
                raise ValueError(
                    "MCSP token has expired and auto-refresh failed. "
                    "Run 'orchestrate env activate remote' manually."
                )
            return token

        return token

    def _refresh_token(self, env_name: str) -> Optional[str]:
        """Attempt to refresh the MCSP token using the API key from env."""
        api_key = os.environ.get('WXO_API_KEY')
        if not api_key:
            return None

        print(f"[INFO] MCSP token expired, refreshing for environment '{env_name}'...",
              file=sys.stderr)

        try:
            result = subprocess.run(
                ['orchestrate', 'env', 'activate', env_name],
                input=api_key + '\n',
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                print(f"[WARN] Token refresh failed: {result.stderr.strip()}",
                      file=sys.stderr)
                return None

            # Re-read the refreshed credentials
            with open(CREDENTIALS_PATH) as f:
                creds = yaml.safe_load(f)

            token = creds.get('auth', {}).get(env_name, {}).get('wxo_mcsp_token')
            if token:
                print("[INFO] Token refreshed successfully.", file=sys.stderr)
            return token

        except Exception as e:
            print(f"[WARN] Token refresh error: {e}", file=sys.stderr)
            return None

    def list_agents(self) -> Dict[str, Any]:
        """List all available agents"""
        try:
            url = f"{self.api_endpoint}/v1/orchestrate/agents"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            agents = response.json()
            return {
                'success': True,
                'agent_count': len(agents),
                'agents': [
                    {'name': a.get('name'), 'id': a.get('id'), 'description': a.get('description', '')[:100]}
                    for a in agents
                ]
            }
        except requests.exceptions.HTTPError as e:
            return {'success': False, 'error': str(e), 'status_code': e.response.status_code}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _resolve_agent_id(self, agent_name: str) -> str:
        """Resolve agent name to UUID. If already a UUID, return as-is."""
        # If it looks like a URL or UUID, attempt to use it
        if len(agent_name) == 36 and agent_name.count('-') == 4:
            return agent_name

        url = f"{self.api_endpoint}/v1/orchestrate/agents"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()

        for agent in response.json():
            if agent.get('name') == agent_name:
                return agent['id']

        raise ValueError(f"Agent '{agent_name}' not found")

    def trigger_agent(self, agent_name: str, user_input: str, wait: bool = True, timeout: int = 120) -> Dict[str, Any]:
        """Trigger an agent and optionally wait for response."""
        try:
            agent_id = self._resolve_agent_id(agent_name)
        except Exception as e:
            return {'success': False, 'error': str(e), 'agent_name': agent_name}

        if wait:
            return self._trigger_sync(agent_id, agent_name, user_input, timeout)
        else:
            return self._trigger_async(agent_id, agent_name, user_input)

    def _trigger_sync(self, agent_id: str, agent_name: str, user_input: str, timeout: int) -> Dict[str, Any]:
        """Trigger agent using the chat/completions endpoint (synchronous)."""
        try:
            url = f"{self.api_endpoint}/v1/orchestrate/{agent_id}/chat/completions"
            payload = {
                'messages': [{'role': 'user', 'content': user_input}],
                'stream': False
            }

            response = requests.post(url, json=payload, headers=self.headers, timeout=timeout)
            response.raise_for_status()

            data = response.json()
            choices = data.get('choices', [])
            reply = choices[0]['message']['content'] if choices else ''

            return {
                'success': True,
                'agent_name': agent_name,
                'status': 'completed',
                'response': reply,
                'full_output': data
            }
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': e.response.status_code,
                'body': e.response.text,
                'agent_name': agent_name
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'agent_name': agent_name}

    def _trigger_async(self, agent_id: str, agent_name: str, user_input: str) -> Dict[str, Any]:
        """Trigger agent using the runs endpoint (async, returns run IDs)."""
        try:
            url = f"{self.api_endpoint}/v1/orchestrate/runs"
            payload = {
                'message': {'role': 'user', 'content': user_input},
                'agent_id': agent_id
            }

            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()

            run_data = response.json()
            return {
                'success': True,
                'agent_name': agent_name,
                'status': 'started',
                'thread_id': run_data.get('thread_id'),
                'run_id': run_data.get('run_id'),
                'task_id': run_data.get('task_id'),
                'message_id': run_data.get('message_id')
            }
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': e.response.status_code,
                'body': e.response.text,
                'agent_name': agent_name
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'agent_name': agent_name}

    def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """Get status of a specific run"""
        try:
            url = f"{self.api_endpoint}/v1/orchestrate/runs/{run_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': e.response.status_code,
                'run_id': run_id
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'run_id': run_id}


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("""
Usage:
  python -m superbob.cli list
  python -m superbob.cli trigger <agent_name> <message> [--no-wait] [--timeout=120]
  python -m superbob.cli status <run_id>

Examples:
  python -m superbob.cli list
  python -m superbob.cli trigger SuperBob_2079Hm "Search for AI news"
  python -m superbob.cli trigger SuperBob_2079Hm "Generate image" --no-wait
  python -m superbob.cli status abc123-run-id
""")
        sys.exit(1)

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    try:
        client = WXOAgentTrigger()
        command = sys.argv[1]

        if command == 'list':
            result = client.list_agents()
            print(json.dumps(result, indent=2))

        elif command == 'trigger':
            if len(sys.argv) < 4:
                print("Error: trigger requires agent_name and message")
                sys.exit(1)

            agent_name = sys.argv[2]
            message = sys.argv[3]
            wait = '--no-wait' not in sys.argv
            timeout = 120

            for arg in sys.argv:
                if arg.startswith('--timeout='):
                    timeout = int(arg.split('=')[1])

            result = client.trigger_agent(agent_name, message, wait, timeout)
            print(json.dumps(result, indent=2))

        elif command == 'status':
            if len(sys.argv) < 3:
                print("Error: status requires run_id")
                sys.exit(1)

            run_id = sys.argv[2]
            result = client.get_run_status(run_id)
            print(json.dumps(result, indent=2))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(json.dumps({'error': str(e)}, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
