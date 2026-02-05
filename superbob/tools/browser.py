"""
Browser Automation Tool for watsonx Orchestrate
Provides browser automation capabilities using Playwright for UI inspection, clicking, and interaction
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Dict, Any, Optional, List
import asyncio
import base64
import os


@tool(
    name="browser_navigate",
    display_name="Browser Navigate",
    description="Navigate to a URL in the browser. Opens a new browser session if needed and navigates to the specified URL. Returns page title and URL."
)
def browser_navigate(url: str) -> Dict[str, Any]:
    """
    Navigate to a URL in the browser.
    
    Args:
        url: The URL to navigate to
    
    Returns:
        Dictionary with navigation result, page title, and current URL
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            title = page.title()
            current_url = page.url
            
            browser.close()
            
            return {
                'success': True,
                'url': current_url,
                'title': title,
                'message': f'Successfully navigated to {url}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Navigation error: {str(e)}',
            'url': url
        }


@tool(
    name="browser_click",
    display_name="Browser Click Element",
    description="Click on an element in the browser using a CSS selector. Useful for interacting with buttons, links, and other clickable elements."
)
def browser_click(url: str, selector: str, wait_time: int = 2) -> Dict[str, Any]:
    """
    Click on an element in the browser.
    
    Args:
        url: The URL to navigate to
        selector: CSS selector for the element to click
        wait_time: Time to wait after clicking (seconds)
    
    Returns:
        Dictionary with click result and page state
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for element and click
            page.wait_for_selector(selector, timeout=10000)
            page.click(selector)
            
            # Wait for any navigation or changes
            page.wait_for_timeout(wait_time * 1000)
            
            title = page.title()
            current_url = page.url
            
            browser.close()
            
            return {
                'success': True,
                'selector': selector,
                'url': current_url,
                'title': title,
                'message': f'Successfully clicked element: {selector}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Click error: {str(e)}',
            'selector': selector,
            'url': url
        }


@tool(
    name="browser_screenshot",
    display_name="Browser Screenshot",
    description="Take a screenshot of a webpage. Captures the full page or a specific element and returns the image as base64."
)
def browser_screenshot(url: str, selector: Optional[str] = None, output_path: str = "/tmp/screenshot.png") -> Dict[str, Any]:
    """
    Take a screenshot of a webpage.
    
    Args:
        url: The URL to screenshot
        selector: Optional CSS selector to screenshot specific element
        output_path: Path to save the screenshot
    
    Returns:
        Dictionary with screenshot path and base64 data
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            if selector:
                element = page.wait_for_selector(selector, timeout=10000)
                screenshot_bytes = element.screenshot()
            else:
                screenshot_bytes = page.screenshot(full_page=True)
            
            # Save screenshot
            with open(output_path, 'wb') as f:
                f.write(screenshot_bytes)
            
            # Convert to base64
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            browser.close()
            
            return {
                'success': True,
                'url': url,
                'screenshot_path': output_path,
                'screenshot_base64': screenshot_base64[:100] + '...',  # Truncated
                'message': f'Screenshot saved to {output_path}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Screenshot error: {str(e)}',
            'url': url
        }


@tool(
    name="browser_inspect",
    display_name="Browser Inspect Element",
    description="Inspect elements on a webpage. Returns information about elements matching a CSS selector including text content, attributes, and properties."
)
def browser_inspect(url: str, selector: str) -> Dict[str, Any]:
    """
    Inspect elements on a webpage.
    
    Args:
        url: The URL to inspect
        selector: CSS selector for elements to inspect
    
    Returns:
        Dictionary with element information
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for elements
            page.wait_for_selector(selector, timeout=10000)
            
            # Get all matching elements
            elements = page.query_selector_all(selector)
            
            element_info = []
            for i, element in enumerate(elements[:10]):  # Limit to 10 elements
                info = {
                    'index': i,
                    'tag': element.evaluate('el => el.tagName'),
                    'text': element.text_content(),
                    'visible': element.is_visible(),
                    'enabled': element.is_enabled(),
                    'attributes': element.evaluate('''el => {
                        const attrs = {};
                        for (let attr of el.attributes) {
                            attrs[attr.name] = attr.value;
                        }
                        return attrs;
                    }''')
                }
                element_info.append(info)
            
            browser.close()
            
            return {
                'success': True,
                'url': url,
                'selector': selector,
                'element_count': len(elements),
                'elements': element_info,
                'message': f'Found {len(elements)} elements matching {selector}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Inspect error: {str(e)}',
            'url': url,
            'selector': selector
        }


@tool(
    name="browser_fill_form",
    display_name="Browser Fill Form",
    description="Fill out form fields on a webpage. Provide a dictionary of CSS selectors and values to fill."
)
def browser_fill_form(url: str, form_data: Dict[str, str], submit_selector: Optional[str] = None) -> Dict[str, Any]:
    """
    Fill out form fields on a webpage.
    
    Args:
        url: The URL with the form
        form_data: Dictionary mapping CSS selectors to values
        submit_selector: Optional CSS selector for submit button
    
    Returns:
        Dictionary with form filling result
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Fill each field
            filled_fields = []
            for selector, value in form_data.items():
                page.wait_for_selector(selector, timeout=10000)
                page.fill(selector, value)
                filled_fields.append(selector)
            
            # Submit if selector provided
            if submit_selector:
                page.click(submit_selector)
                page.wait_for_timeout(2000)
            
            title = page.title()
            current_url = page.url
            
            browser.close()
            
            return {
                'success': True,
                'url': current_url,
                'title': title,
                'filled_fields': filled_fields,
                'submitted': bool(submit_selector),
                'message': f'Successfully filled {len(filled_fields)} form fields'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Form fill error: {str(e)}',
            'url': url
        }
