#!/usr/bin/env python3
"""
Setup script to import Gemini image generation tool using Python SDK
"""

import os
import sys
import base64
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_gemini_tool():
    """Setup Gemini tool using orchestrate CLI with proper authentication"""
    
    # Get credentials
    instance_url = os.getenv('WXO_INSTANCE')
    api_key_b64 = os.getenv('WXO_API_KEY')
    
    if not instance_url or not api_key_b64:
        print("[ERROR] WXO_INSTANCE and WXO_API_KEY must be set in .env")
        sys.exit(1)
    
    # Decode API key
    api_key = base64.b64decode(api_key_b64).decode('utf-8')
    
    # Set environment variable for orchestrate CLI
    os.environ['WXO_API_KEY_DECODED'] = api_key
    
    print("[INFO] Setting up Gemini image generation tool...")
    print("[INFO] Instance:", instance_url)
    
    # Commands to run
    commands = [
        # Add connection
        "orchestrate connections add -a gemini_api",
        
        # Configure for draft
        "orchestrate connections configure -a gemini_api --env draft --type team --kind api_key_auth",
        
        # Configure for live
        "orchestrate connections configure -a gemini_api --env live --type team --kind api_key_auth",
        
        # Set credentials for draft
        f"orchestrate connections set-credentials -a gemini_api --env draft --url 'https://generativelanguage.googleapis.com' --api-key '{os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')}'",
        
        # Set credentials for live
        f"orchestrate connections set-credentials -a gemini_api --env live --url 'https://generativelanguage.googleapis.com' --api-key '{os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')}'",
        
        # Import tool
        "orchestrate tools import --kind python --file superbob/tools/image_gen.py --requirements-file gemini_requirements.txt --app-id gemini_api"
    ]
    
    print("\n[INFO] Run these commands manually in your terminal:")
    print("=" * 80)
    for cmd in commands:
        print(cmd)
    print("=" * 80)
    
    print("\n[INFO] Or use bob_wxo_trigger.py which handles authentication automatically")

if __name__ == "__main__":
    setup_gemini_tool()
