#!/usr/bin/env python3
"""
Import Gemini image generation tool to watsonx Orchestrate using Python SDK
"""

import os
import sys
import base64
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def import_gemini_tool():
    """Import Gemini tool using orchestrate Python SDK"""
    
    try:
        from ibm_watsonx_orchestrate import APIClient, ConnectionType
        from ibm_watsonx_orchestrate.types import (
            CreateConnectionOptions,
            ConfigureConnectionsOptions,
            SetCredentialsConnectionOptions,
            ImportToolKitOptions
        )
    except ImportError:
        print("❌ Error: ibm-watsonx-orchestrate package not installed")
        print("Install with: pip install ibm-watsonx-orchestrate")
        sys.exit(1)
    
    # Get credentials from .env
    instance_url = os.getenv('WXO_INSTANCE')
    api_key_b64 = os.getenv('WXO_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not all([instance_url, api_key_b64, gemini_api_key]):
        print("❌ Error: Missing required environment variables in .env")
        print("Required: WXO_INSTANCE, WXO_API_KEY, GEMINI_API_KEY")
        sys.exit(1)
    
    # Decode WXO API key
    api_key = base64.b64decode(api_key_b64).decode('utf-8')
    
    print("=" * 60)
    print("Gemini Image Tool Import to WXO")
    print("=" * 60)
    print(f"Instance: {instance_url}")
    print(f"Gemini API Key: {gemini_api_key[:20]}...")
    print()
    
    # Initialize API client
    print("Step 1: Initializing WXO API client...")
    client = APIClient(
        base_url=instance_url,
        api_key=api_key,
        auth_type='mcsp'
    )
    print("✅ Client initialized")
    print()
    
    # Create connection
    print("Step 2: Creating gemini_api connection...")
    try:
        client.connections.create(
            CreateConnectionOptions(app_id='gemini_api')
        )
        print("✅ Connection created")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("⚠️  Connection already exists, continuing...")
        else:
            print(f"❌ Error creating connection: {e}")
            sys.exit(1)
    print()
    
    # Configure for draft environment
    print("Step 3: Configuring connection for draft environment...")
    try:
        client.connections.configure(
            ConfigureConnectionsOptions(
                app_id='gemini_api',
                env='draft',
                type='team',
                kind='api_key_auth'
            )
        )
        print("✅ Draft environment configured")
    except Exception as e:
        print(f"⚠️  Draft config: {e}")
    print()
    
    # Configure for live environment
    print("Step 4: Configuring connection for live environment...")
    try:
        client.connections.configure(
            ConfigureConnectionsOptions(
                app_id='gemini_api',
                env='live',
                type='team',
                kind='api_key_auth'
            )
        )
        print("✅ Live environment configured")
    except Exception as e:
        print(f"⚠️  Live config: {e}")
    print()
    
    # Set credentials for draft
    print("Step 5: Setting credentials for draft environment...")
    try:
        client.connections.set_credentials(
            SetCredentialsConnectionOptions(
                app_id='gemini_api',
                env='draft',
                url='https://generativelanguage.googleapis.com',
                api_key=gemini_api_key
            )
        )
        print("✅ Draft credentials set")
    except Exception as e:
        print(f"❌ Error setting draft credentials: {e}")
    print()
    
    # Set credentials for live
    print("Step 6: Setting credentials for live environment...")
    try:
        client.connections.set_credentials(
            SetCredentialsConnectionOptions(
                app_id='gemini_api',
                env='live',
                url='https://generativelanguage.googleapis.com',
                api_key=gemini_api_key
            )
        )
        print("✅ Live credentials set")
    except Exception as e:
        print(f"❌ Error setting live credentials: {e}")
    print()
    
    # Import tool
    print("Step 7: Importing Gemini image generation tool...")
    try:
        tool_path = Path(__file__).parents[1] / 'superbob' / 'tools' / 'image_gen.py'
        requirements_path = Path(__file__).parents[1] / 'gemini_requirements.txt'
        
        client.tools.import_tool(
            kind='python',
            path=str(tool_path),
            app_id='gemini_api',
            requirements_filepath=str(requirements_path)
        )
        print("✅ Tool imported successfully!")
    except Exception as e:
        print(f"❌ Error importing tool: {e}")
        sys.exit(1)
    print()
    
    print("=" * 60)
    print("✅ SUCCESS! Gemini tool imported to WXO")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Add 'generate_image_gemini' to SuperBob agent tools list")
    print("2. Re-import SuperBob agent")
    print()

if __name__ == "__main__":
    import_gemini_tool()
