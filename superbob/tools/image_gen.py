"""
Gemini Image Generation Tool for watsonx Orchestrate
Uses Google's Imagen 4.0 model to generate images from text prompts.
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from ibm_watsonx_orchestrate.run import connections
import base64
import io

GEMINI_APP_ID = 'gemini_api'

@tool(
    name="generate_image_gemini",
    display_name="Generate Image with Gemini Imagen",
    description="Generate high-quality images from text descriptions using Google's Imagen 4.0 model. Creates photorealistic AI-generated images based on detailed prompts.",
    expected_credentials=[
        {"app_id": GEMINI_APP_ID, "type": ConnectionType.API_KEY_AUTH}
    ]
)
def generate_image_gemini(prompt: str, aspect_ratio: str = "1:1", number_of_images: int = 1) -> dict:
    """
    Generate an image using Google's Imagen 4.0 model.
    
    Args:
        prompt: Detailed text description of the image to generate (max 480 tokens, English only). 
                Be specific and descriptive. Structure: Subject + Context/Background + Style.
        aspect_ratio: Image aspect ratio. Options: "1:1" (square), "3:4", "4:3", "9:16", "16:9". Default: "1:1"
        number_of_images: Number of images to generate (1-4). Default: 1
    
    Returns:
        dict: Contains success status, image data (base64), and metadata
    """
    try:
        from google import genai
        from google.genai import types
        
        # Get API key from connection
        conn = connections.api_key_auth(GEMINI_APP_ID)
        api_key = conn.api_key
        
        # Initialize client
        client = genai.Client(api_key=api_key)
        
        # Validate inputs
        if number_of_images < 1 or number_of_images > 4:
            number_of_images = 1
            
        valid_ratios = ["1:1", "3:4", "4:3", "9:16", "16:9"]
        if aspect_ratio not in valid_ratios:
            aspect_ratio = "1:1"
        
        # Generate images using Imagen 4.0
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio,
            )
        )
        
        # Process generated images
        if response.generated_images:
            images_data = []
            
            for idx, generated_image in enumerate(response.generated_images):
                # Convert PIL image to base64
                img_byte_arr = io.BytesIO()
                generated_image.image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                image_base64 = base64.b64encode(img_byte_arr.read()).decode('utf-8')
                
                images_data.append({
                    "index": idx + 1,
                    "image_base64": image_base64,
                    "format": "PNG"
                })
            
            return {
                "success": True,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "number_of_images": len(images_data),
                "images": images_data,
                "model": "imagen-4.0-generate-001",
                "message": f"Successfully generated {len(images_data)} image(s) with aspect ratio {aspect_ratio}",
                "note": "All images include SynthID watermark"
            }
        else:
            return {
                "success": False,
                "error": "No images were generated",
                "prompt": prompt
            }
            
    except ImportError as e:
        return {
            "success": False,
            "error": f"Required package not installed: {str(e)}. Install 'google-genai' package.",
            "prompt": prompt
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Image generation error: {str(e)}",
            "prompt": prompt
        }