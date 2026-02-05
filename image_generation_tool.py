"""
Image Generation Tool for watsonx Orchestrate
Generates images using Google Gemini API
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from typing import Dict, Any
import os
import base64
import requests
from datetime import datetime


GEMINI_APP_ID = 'gemini_api'


@tool(
    name="generate_image",
    display_name="Generate Image with Gemini",
    description="Generate images using Google Gemini's image generation capabilities. Provide a detailed text description of the image you want to create. The tool will return the generated image as a base64-encoded string and save it locally.",
    expected_credentials=[
        {"app_id": GEMINI_APP_ID, "type": ConnectionType.API_KEY_AUTH}
    ]
)
def generate_image(prompt: str, output_dir: str = "/tmp") -> Dict[str, Any]:
    """
    Generate an image using Google Gemini API based on a text prompt.

    Args:
        prompt: Detailed description of the image to generate
        output_dir: Directory to save the generated image (default: /tmp)

    Returns:
        A dictionary containing the image data, file path, and generation details
    """
    try:
        # Get API key: prefer WXO connection, fall back to environment variable
        api_key = None
        try:
            from ibm_watsonx_orchestrate.run import connections
            conn = connections.api_key_auth(GEMINI_APP_ID)
            api_key = conn.api_key
        except Exception:
            api_key = os.environ.get('GEMINI_API_KEY')

        if not api_key:
            return {
                'success': False,
                'error': 'GEMINI_API_KEY not configured. Set up a connection named '
                         f"'{GEMINI_APP_ID}' in WXO or set the GEMINI_API_KEY environment variable.",
                'prompt': prompt
            }

        # Use Gemini generateContent endpoint with image output
        # Try models in order of preference
        models = [
            "gemini-2.5-flash-image",
            "gemini-2.0-flash-exp-image-generation",
            "gemini-3-pro-image-preview",
        ]

        headers = {
            'Content-Type': 'application/json'
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }

        response = None
        last_error = None
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            if response.status_code == 200:
                break
            last_error = f"{model}: {response.status_code} {response.text[:200]}"

        response.raise_for_status()

        result = response.json()

        # Extract image from response parts
        candidates = result.get('candidates', [])
        if not candidates:
            return {
                'success': False,
                'error': 'No candidates in response',
                'prompt': prompt,
                'response': result
            }

        parts = candidates[0].get('content', {}).get('parts', [])
        image_base64 = None
        mime_type = 'image/png'
        text_response = ''

        for part in parts:
            # REST API returns camelCase keys (inlineData, mimeType)
            inline = part.get('inline_data') or part.get('inlineData')
            if inline:
                image_base64 = inline.get('data')
                mime_type = inline.get('mime_type') or inline.get('mimeType') or 'image/png'
            elif 'text' in part:
                text_response = part['text']

        if image_base64:
            # Generate filename with timestamp
            ext = mime_type.split('/')[-1] if '/' in mime_type else 'png'
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"gemini_image_{timestamp}.{ext}"
            filepath = os.path.join(output_dir, filename)

            # Decode and save the image
            image_bytes = base64.b64decode(image_base64)
            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            return {
                'success': True,
                'prompt': prompt,
                'image_path': filepath,
                'image_base64': image_base64[:100] + '...',
                'mime_type': mime_type,
                'text_response': text_response,
                'message': f'Image generated successfully and saved to {filepath}'
            }
        else:
            return {
                'success': False,
                'error': 'No image data in response',
                'prompt': prompt,
                'text_response': text_response
            }

    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'API request error: {str(e)}',
            'prompt': prompt
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Image generation error: {str(e)}',
            'prompt': prompt
        }
