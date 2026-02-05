# Gemini Image Generation Tool - Import Instructions

## ✅ Tool Status
- **gemini_image_tool.py** - Ready and tested locally
- **gemini_requirements.txt** - Dependencies specified
- **Test Result** - Successfully generated image using Imagen 4.0

## 🔧 Issue Identified
The watsonx Orchestrate MCP server and CLI tools require interactive authentication, which causes timeouts in automated contexts.

## 📋 Manual Import Steps (RECOMMENDED)

### Step 1: Authenticate CLI
Open a terminal and run:
```bash
cd /Users/thadchaisaenprasert/Desktop/work/SuperBob
orchestrate env activate remote
```
When prompted, paste your WXO API key (decode from .env):
```bash
echo "azE6dXNyXzg3YjcxYTlkLWY3N2MtMzI2NC1iNTlhLWQ2NjI4ZjVhZGE4NDphQkFtYkVtMFpIYUdwUUU4Wmc5Q1U2TDY0dmVGRU44SWNJQ0ZmZ0FCR1dZPTp4a1Fz" | base64 -d
```

### Step 2: Create Connection
```bash
orchestrate connections add -a gemini_api
```

### Step 3: Configure Environments
```bash
orchestrate connections configure -a gemini_api --env draft --type team --kind api_key_auth
orchestrate connections configure -a gemini_api --env live --type team --kind api_key_auth
```

### Step 4: Set Credentials
```bash
orchestrate connections set-credentials -a gemini_api --env draft --url 'https://generativelanguage.googleapis.com' --api-key 'YOUR_GEMINI_API_KEY'
# AND
orchestrate connections set-credentials -a gemini_api --env live --url 'https://generativelanguage.googleapis.com' --api-key 'YOUR_GEMINI_API_KEY'
```

### Step 5: Import Tool
```bash
orchestrate tools import --kind python \
  --file gemini_image_tool.py \
  --requirements-file gemini_requirements.txt \
  --app-id gemini_api
```

### Step 6: Add to SuperBob Agent
Edit `superbob_agent/agents/native/SuperBob_2079Hm.yaml` and add to tools list:
```yaml
tools:
  - web_search
  - trigger_wxo_agent
  - list_wxo_agents
  - generate_image_gemini  # ADD THIS LINE
```

### Step 7: Re-import SuperBob Agent
```bash
orchestrate agents import -f superbob_agent/agents/native/SuperBob_2079Hm.yaml
```

## 🎯 Tool Capabilities
- **Model**: Google Imagen 4.0 (imagen-4.0-generate-001)
- **Aspect Ratios**: 1:1, 3:4, 4:3, 9:16, 16:9
- **Images per request**: 1-4
- **Output**: Base64-encoded PNG with SynthID watermark
- **Prompt limit**: 480 tokens, English only

## 📝 Example Usage
Once imported, SuperBob can generate images:
```
"Generate a futuristic city at sunset with flying cars in 16:9 format"
```

## ⚠️ Known Limitations
- MCP server operations timeout due to interactive authentication requirements
- CLI must be authenticated manually in terminal
- Connection credentials must be set interactively
