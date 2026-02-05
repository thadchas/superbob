# SuperBob - WXO AI Automation Agent

## Project Overview

SuperBob is a comprehensive AI automation agent built for IBM watsonx Orchestrate (WXO). It combines web intelligence, AI creativity, and browser automation capabilities to help users accomplish complex tasks efficiently.

## Agent Information

**Agent Name:** SuperBob_2079Hm  
**Display Name:** SuperBob 🔨  
**LLM Model:** groq/openai/gpt-oss-120b  
**Style:** react  

### Description
SuperBob is your ultimate AI-powered automation assistant with capabilities including:
- 🔍 Web Search - Find current information from the internet
- 🎨 Image Generation - Create AI-generated images with Gemini
- 🌐 Browser Automation - Navigate, inspect, click, and interact with web pages
- 📸 Screenshot Capture - Take full-page or element screenshots
- 📝 Form Filling - Automate web form submissions

## Complete Tool Suite (10 Tools)

### 1. Web Search (`web_search`)
- **Purpose:** Search the internet using DuckDuckGo
- **Use Case:** Find current information, news, facts, or web content
- **Implementation:** `web_search_tool.py`

### 2. Image Generation (`generate_image`)
- **Purpose:** Generate AI images using Google Gemini
- **Requirements:** GEMINI_API_KEY environment variable
- **Use Case:** Create images from text descriptions
- **Implementation:** `image_generation_tool.py`

### 3. Browser Navigation (`browser_navigate`)
- **Purpose:** Navigate to URLs in a headless browser
- **Returns:** Page title and URL
- **Implementation:** `browser_automation_tool.py`

### 4. Browser Click (`browser_click`)
- **Purpose:** Click elements using CSS selectors
- **Use Case:** Interact with buttons, links, clickable elements
- **Implementation:** `browser_automation_tool.py`

### 5. Browser Screenshot (`browser_screenshot`)
- **Purpose:** Capture page or element screenshots
- **Returns:** Base64 encoded image
- **Implementation:** `browser_automation_tool.py`

### 6. Browser Inspect (`browser_inspect`)
- **Purpose:** Examine page elements
- **Returns:** Element properties, text, attributes
- **Implementation:** `browser_automation_tool.py`

### 7. Browser Form Fill (`browser_fill_form`)
- **Purpose:** Automatically fill web forms
- **Use Case:** Form automation and submission
- **Implementation:** `browser_automation_tool.py`

### 8. Trigger WXO Agent (`trigger_wxo_agent`)
- **Purpose:** Trigger other WXO agents programmatically
- **Use Case:** Multi-agent orchestration
- **Implementation:** `wxo_agent_trigger_tool.py`

### 9. List WXO Agents (`list_wxo_agents`)
- **Purpose:** Discover available agents
- **Returns:** Agent names, descriptions, capabilities
- **Implementation:** `wxo_agent_trigger_tool.py`

### 10. Get Agent Status (`get_wxo_agent_status`)
- **Purpose:** Monitor running agent tasks
- **Use Case:** Check status by run ID
- **Implementation:** `wxo_agent_trigger_tool.py`

## Environment Setup

### Prerequisites
- Python 3.12+
- IBM watsonx Orchestrate account
- watsonx Orchestrate ADK installed

### Environment Variables

Create a `.env` file in the project root:

```bash
# WXO Instance Configuration
WXO_INSTANCE=https://api.ap-southeast-1.dl.watson-orchestrate.ibm.com/instances/YOUR_INSTANCE_ID
WXO_API_KEY=YOUR_BASE64_ENCODED_API_KEY
WXO_ENVIRONMENT=remote

# Optional: For Image Generation
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### Installation

1. **Install watsonx Orchestrate ADK:**
```bash
pip install ibm-watsonx-orchestrate
```

2. **Install Browser Automation Dependencies:**
```bash
pip install playwright
playwright install chromium
```

3. **Install Additional Dependencies:**
```bash
pip install requests
```

4. **Configure WXO Environment:**
```bash
# Add environment
orchestrate env add -n remote \
  -u https://api.ap-southeast-1.dl.watson-orchestrate.ibm.com/instances/YOUR_INSTANCE_ID \
  --type mcsp --activate

# Activate environment (will prompt for API key)
orchestrate env activate remote
```

## Project Structure

```
SuperBob/
├── .env                          # Environment variables
├── .bob/
│   └── mcp.json                  # MCP server configuration
├── superbob_agent/
│   └── agents/
│       └── native/
│           └── SuperBob_2079Hm.yaml  # Agent specification
├── web_search_tool.py            # Web search implementation
├── image_generation_tool.py      # Image generation implementation
├── browser_automation_tool.py    # Browser automation tools
├── wxo_agent_trigger_tool.py     # WXO agent orchestration
├── bob_wxo_trigger.py            # Direct API client (auth issues)
├── bob_wxo_cli_wrapper.py        # CLI wrapper (recommended)
├── bob_wxo_simple.sh             # Bash wrapper for MCP tools
└── README.md                     # Project documentation
```

## Usage

### Using WXO MCP Server

The MCP server provides direct integration with Bob-shell:

```json
{
  "mcpServers": {
    "wxo-mcp": {
      "command": "uvx",
      "args": [
        "--with",
        "ibm-watsonx-orchestrate==1.13.0",
        "ibm-watsonx-orchestrate-mcp-server"
      ],
      "env": {
        "WXO_MCP_WORKING_DIRECTORY": "/Users/thadchaisaenprasert/Desktop/work/SuperBob"
      }
    }
  }
}
```

### Importing Tools

```bash
# Import web search tool
orchestrate tools import -k python -f web_search_tool.py

# Import image generation tool
orchestrate tools import -k python -f image_generation_tool.py

# Import browser automation tools
orchestrate tools import -k python -f browser_automation_tool.py

# Import WXO orchestration tools
orchestrate tools import -k python -f wxo_agent_trigger_tool.py
```

### Importing/Updating Agent

```bash
# Import agent
orchestrate agents import -f superbob_agent/agents/native/SuperBob_2079Hm.yaml

# Export agent
orchestrate agents export -n SuperBob_2079Hm -o superbob_agent.zip
```

### Bob-shell Integration

#### Option 1: CLI Wrapper (Recommended)
```bash
# List agents
python bob_wxo_cli_wrapper.py list

# Trigger SuperBob
python bob_wxo_cli_wrapper.py trigger SuperBob_2079Hm "Search for AI news"

# Export agent
python bob_wxo_cli_wrapper.py export SuperBob_2079Hm ./agent.zip
```

#### Option 2: Bash Wrapper
```bash
# List agents
./bob_wxo_simple.sh list

# Trigger agent
./bob_wxo_simple.sh trigger SuperBob_2079Hm "Generate an image of a robot"

# Check status
./bob_wxo_simple.sh status <run_id>
```

## Agent Configuration

### Welcome Message
```
🔨 SuperBob - Your AI Automation Assistant! 
Web Search | Image Gen | Browser Automation 🚀
```

### Instructions
SuperBob follows these guidelines:
- Always explain actions before using tools
- For web tasks, inspect elements first before interacting
- Provide clear, actionable results
- Try alternative approaches if tools fail
- Be proactive in suggesting help

### Personality
- Professional yet friendly
- Solution-oriented and efficient
- Clear and concise communication
- Helpful and proactive

## Tool Implementation Details

### Web Search Tool
- **API:** DuckDuckGo
- **Max Results:** Configurable (default: 5, max: 10)
- **Returns:** Titles, snippets, URLs, sources
- **Error Handling:** Network errors, API failures

### Image Generation Tool
- **API:** Google Gemini imagen-3.0-generate-001
- **Requirements:** GEMINI_API_KEY
- **Output:** Base64 encoded PNG + local file
- **Parameters:** Prompt, output directory

### Browser Automation Tools
- **Engine:** Playwright (Chromium)
- **Mode:** Headless
- **Capabilities:**
  - Navigate to URLs
  - Click elements via CSS selectors
  - Take screenshots (full page or elements)
  - Inspect element properties
  - Fill and submit forms
- **Timeout:** Configurable per operation

### WXO Orchestration Tools
- **Authentication:** Uses WXO SDK
- **Capabilities:**
  - List all agents
  - Trigger agents with messages
  - Monitor run status
  - Wait for completion or async
- **Timeout:** Configurable (default: 60s)

## Authentication

### WXO API Key Format
The WXO_API_KEY is base64 encoded and follows the format:
```
k1:usr_<user_id>:<actual_token>
```

The SDK automatically handles decoding and authentication.

### Authentication Types
- **IBM Cloud:** IBM IAM authentication
- **AWS (MCSP):** Multi-Cloud Service Platform auth
- **On-premises:** CPD authentication

## Troubleshooting

### 401 Unauthorized Errors
- Verify WXO_INSTANCE URL is correct
- Ensure WXO_API_KEY is properly base64 encoded
- Check API key hasn't expired
- Confirm correct authentication type for your environment

### Tool Import Failures
- Verify Python dependencies are installed
- Check tool decorator imports: `from ibm_watsonx_orchestrate.agent_builder.tools import tool`
- Ensure file paths are absolute

### Browser Automation Issues
- Install Playwright browsers: `playwright install chromium`
- Check timeout settings for slow pages
- Verify CSS selectors are correct

### Image Generation Failures
- Set GEMINI_API_KEY environment variable
- Get API key from: https://aistudio.google.com/app/apikey
- Check API quota and limits

## Development

### Adding New Tools

1. Create tool file with proper decorator:
```python
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool(
    name="my_tool",
    display_name="My Tool",
    description="Tool description for LLM"
)
def my_tool(param: str) -> dict:
    # Implementation
    return {"success": True, "result": "..."}
```

2. Import tool:
```bash
orchestrate tools import -k python -f my_tool.py
```

3. Update agent YAML:
```yaml
tools:
  - my_tool
```

4. Re-import agent:
```bash
orchestrate agents import -f superbob_agent/agents/native/SuperBob_2079Hm.yaml
```

### Testing Tools Locally

```python
# Test web search
from web_search_tool import web_search
result = web_search("AI news", max_results=3)
print(result)

# Test browser navigation
from browser_automation_tool import browser_navigate
result = browser_navigate("https://example.com")
print(result)
```

## API Reference

### MCP Server Tools

All tools are available through the MCP server when configured in Bob-shell.

**Available MCP Tools:**
- `list_agents` - List all WXO agents
- `create_or_update_agent` - Create/update agents
- `import_agent` - Import agent from spec
- `remove_agent` - Remove agent
- `export_agent` - Export agent to file
- `import_tool` - Import tool
- `list_tools` - List all tools
- `remove_tool` - Remove tool
- `export_tool` - Export tool
- And more...

## Best Practices

1. **Tool Usage:**
   - Use web_search for current information
   - Use browser tools for interactive web tasks
   - Use agent orchestration for complex workflows

2. **Error Handling:**
   - Always check tool response success field
   - Implement retry logic for network operations
   - Provide fallback options

3. **Security:**
   - Never commit API keys to version control
   - Use environment variables for credentials
   - Validate user inputs in tools

4. **Performance:**
   - Set appropriate timeouts
   - Use background processes for long operations
   - Cache results when appropriate

## Support and Resources

- **WXO Documentation:** https://developer.watson-orchestrate.ibm.com/
- **ADK Documentation:** https://developer.watson-orchestrate.ibm.com/getting_started/installing
- **MCP Server:** https://developer.watson-orchestrate.ibm.com/mcp_server/wxOmcp_installation
- **Playwright Docs:** https://playwright.dev/python/

## Version History

- **v1.0** - Initial SuperBob agent with 10 tools
  - Web search capability
  - Image generation with Gemini
  - Browser automation (5 tools)
  - WXO agent orchestration (3 tools)
  - Complete profile and instructions
  - Bob-shell integration scripts

## License

This project uses IBM watsonx Orchestrate which requires appropriate licensing.

## Contributors

- Initial development and tool integration
- MCP server configuration
- Bob-shell integration scripts
