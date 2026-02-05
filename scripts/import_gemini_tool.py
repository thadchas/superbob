#!/usr/bin/env python3
"""
Script to import Gemini image generation tool to watsonx Orchestrate
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from ibm_watsonx_orchestrate import APIClient
from ibm_watsonx_orchestrate.helpers import EnvironmentType

# Load environment variables
load_dotenv()

def import_tool():
    """Import the Gemini image generation tool"""
    
    # Get credentials from environment
    instance_url = os.getenv('WXO_INSTANCE')
    api_key = os.getenv('WXO_API_KEY')
    
    if not instance_url or not api_key:
        print("[ERROR] WXO_INSTANCE and WXO_API_KEY must be set in .env file")
        sys.exit(1)
    
    # Initialize API client
    client = APIClient(
        instance_url=instance_url,
        api_key=api_key,
        environment_type=EnvironmentType.REMOTE
    )
    
    print("[INFO] Importing Gemini image generation tool...")
    
    # Import the tool
    tool_file = Path(__file__).parents[1] / 'superbob' / 'tools' / 'image_gen.py'
    requirements_file = Path(__file__).parents[1] / 'gemini_requirements.txt'
    
    try:
        # Note: This requires the tool to be imported via CLI or API
        # For now, we'll document the manual steps
        print(f"[INFO] Tool file: {tool_file}")
        print(f"[INFO] Requirements file: {requirements_file}")
        print("\n[INFO] To import this tool, you need to:")
        print("1. First, refresh your orchestrate CLI token:")
        print("   orchestrate env activate remote")
        print("   (Enter your WXO API key when prompted)")
        print("\n2. Create the connection:")
        print("   orchestrate connections add -a gemini_api")
        print("\n3. Configure the connection for both environments:")
        print("   orchestrate connections configure -a gemini_api --env draft --type team --kind api_key_auth")
        print("   orchestrate connections configure -a gemini_api --env live --type team --kind api_key_auth")
        print("\n4. Set the API key credentials:")
        print("   orchestrate connections set-credentials -a gemini_api --env draft --url 'https://generativelanguage.googleapis.com' --api-key 'AIzaSyAOVCtSOiUTMtpxid2jxaSH-nFDntFQKWU'")
        print("   orchestrate connections set-credentials -a gemini_api --env live --url 'https://generativelanguage.googleapis.com' --api-key 'AIzaSyAOVCtSOiUTMtpxid2jxaSH-nFDntFQKWU'")
        print("\n5. Import the tool:")
        print(f"   orchestrate tools import --kind python --file {tool_file} --requirements-file {requirements_file} --app-id gemini_api")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    import_tool()
