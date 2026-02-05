#!/bin/bash
# Script to authenticate and import Gemini image generation tool to watsonx Orchestrate

cd /Users/thadchaisaenprasert/Desktop/work/SuperBob

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Decode the base64 API key
API_KEY=$(echo "$WXO_API_KEY" | base64 -d)

echo "=========================================="
echo "Gemini Image Tool Import to WXO"
echo "=========================================="
echo ""
echo "Step 1: Refreshing orchestrate CLI token..."
echo "$API_KEY" | orchestrate env activate remote

if [ $? -ne 0 ]; then
    echo "❌ Failed to refresh token"
    exit 1
fi

echo "✅ Token refreshed successfully"
echo ""

echo "Step 2: Creating gemini_api connection..."
orchestrate connections add -a gemini_api

echo ""
echo "Step 3: Configuring connection for draft environment..."
orchestrate connections configure -a gemini_api --env draft --type team --kind api_key_auth

echo ""
echo "Step 4: Configuring connection for live environment..."
orchestrate connections configure -a gemini_api --env live --type team --kind api_key_auth

echo ""
echo "Step 5: Setting credentials for draft environment..."
orchestrate connections set-credentials -a gemini_api --env draft \
  --url 'https://generativelanguage.googleapis.com' \
  --api-key "$GEMINI_API_KEY"

echo ""
echo "Step 6: Setting credentials for live environment..."
orchestrate connections set-credentials -a gemini_api --env live \
  --url 'https://generativelanguage.googleapis.com' \
  --api-key "$GEMINI_API_KEY"

echo ""
echo "Step 7: Importing Gemini image generation tool..."
orchestrate tools import --kind python \
  --file gemini_image_tool.py \
  --requirements-file gemini_requirements.txt \
  --app-id gemini_api

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS! Tool imported to WXO"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Add 'generate_image_gemini' to SuperBob agent tools list"
    echo "2. Re-import SuperBob agent"
    echo ""
else
    echo ""
    echo "❌ Failed to import tool"
    exit 1
fi
