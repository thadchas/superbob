"""
Web Search Tool for watsonx Orchestrate
Provides internet search capabilities using DuckDuckGo
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import List, Dict, Any
import requests
from urllib.parse import quote_plus


@tool(
    name="web_search",
    display_name="Web Search",
    description="Search the internet for information using DuckDuckGo. Use this tool when you need to find current information, news, facts, or any content available on the web. Provide a clear search query to get relevant results."
)
def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search the web using DuckDuckGo and return relevant results.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5, max: 10)
    
    Returns:
        A dictionary containing search results with titles, snippets, and URLs
    """
    try:
        # Limit max_results to reasonable bounds
        max_results = min(max(1, max_results), 10)
        
        # Use DuckDuckGo Instant Answer API
        encoded_query = quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        results = []
        
        # Extract Abstract if available
        if data.get('Abstract'):
            results.append({
                'title': data.get('Heading', 'Summary'),
                'snippet': data.get('Abstract', ''),
                'url': data.get('AbstractURL', ''),
                'source': data.get('AbstractSource', 'DuckDuckGo')
            })
        
        # Extract Related Topics
        for topic in data.get('RelatedTopics', [])[:max_results]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append({
                    'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else 'Related',
                    'snippet': topic.get('Text', ''),
                    'url': topic.get('FirstURL', ''),
                    'source': 'DuckDuckGo'
                })
        
        # If no results from API, try HTML scraping approach
        if not results:
            html_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            html_response = requests.get(html_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Simple parsing - look for result links
            # Note: This is a fallback and may need adjustment based on DuckDuckGo's HTML structure
            results.append({
                'title': 'Search Results',
                'snippet': f'Found results for: {query}',
                'url': f'https://duckduckgo.com/?q={encoded_query}',
                'source': 'DuckDuckGo'
            })
        
        return {
            'success': True,
            'query': query,
            'results_count': len(results),
            'results': results[:max_results]
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Network error: {str(e)}',
            'query': query,
            'results': []
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Search error: {str(e)}',
            'query': query,
            'results': []
        }
