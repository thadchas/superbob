#!/bin/bash
# Script to refresh orchestrate CLI token and setup Gemini connection

cd /Users/thadchaisaenprasert/Desktop/work/SuperBob

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# The API key is base64 encoded in .env, decode it
API_KEY_DECODED=$(echo "$WXO_API_KEY" | base64 -d)

echo "[INFO] Refreshing orchestrate CLI token..."
echo "$API_KEY_DECODED" | orchestrate env activate remote

echo "[INFO] Creating Gemini API connection..."
orchestrate connections add -a gemini_api

echo "[INFO] Configuring connection for draft environment..."
orchestrate connections configure -a gemini_api --env draft --type team --kind api_key_auth

echo "[INFO] Configuring connection for live environment..."
orchestrate connections configure -a gemini_api --env live --type team --kind api_key_auth

echo "[INFO] Setting credentials for draft environment..."
orchestrate connections set-credentials -a gemini_api --env draft --url 'https://generativelanguage.googleapis.com' --api-key "$GEMINI_API_KEY"

# Configure for live
echo "Setting credentials for live environment..."
orchestrate connections set-credentials -a gemini_api --env live --url 'https://generativelanguage.googleapis.com' --api-key "$GEMINI_API_KEY"

echo "[INFO] Importing Gemini image generation tool..."
orchestrate tools import --kind python \
  --file gemini_image_tool.py \
  --requirements-file gemini_requirements.txt \
  --app-id gemini_api

echo "[INFO] Setup complete!"
