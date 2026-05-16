# backend/app/llm_service.py
"""
LLM Service for Azure OpenAI + Gemini Integration
Uses official Azure OpenAI SDK and Google Gemini API
"""

import os
import json
from typing import Dict, Any, Optional
from backend.app import prompts

# ============================================================
# CONFIGURATION - Your API Keys
# ============================================================
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

AZURE_ENDPOINT = "https://openai-lab37-hackathon.openai.azure.com"
AZURE_API_VERSION = "2025-04-01-preview"
AZURE_DEPLOYMENT = "gpt-5-mini1"
# ============================================================


class LLMService:
    """Service for handling all LLM-based content generation"""
    
    def __init__(self):
        """Initialize LLM Service with Azure OpenAI and Gemini"""
        self.azure_endpoint = AZURE_ENDPOINT
        self.azure_api_key = OPENAI_API_KEY
        self.azure_api_version = AZURE_API_VERSION
        self.azure_deployment = AZURE_DEPLOYMENT
        self.gemini_api_key = GEMINI_API_KEY
        
        # Initialize Azure OpenAI client
        try:
            from openai import AzureOpenAI
            self.azure_client = AzureOpenAI(
                api_key=self.azure_api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=self.azure_api_version,
            )
            self.azure_available = True
        except Exception as e:
            print(f"⚠️  Warning: Azure OpenAI client initialization failed: {e}")
            self.azure_client = None
            self.azure_available = False
        
        # Initialize Gemini client
        try:
            from google import genai
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            self.gemini_available = True
        except Exception as e:
            print(f"⚠️  Warning: Gemini client initialization failed: {e}")
            self.gemini_client = None
            self.gemini_available = False
    
    def _call_azure_openai(
        self, 
        system_prompt: str, 
        user_message: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        response_format: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Call Azure OpenAI API using official SDK
        
        Args:
            system_prompt: System prompt defining the AI's role
            user_message: User's input message
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0-1.0)
            response_format: Optional response format (e.g., {"type": "json_object"})
            
        Returns:
            Dict with 'success' (bool) and either 'data' or 'error'
        """
        if not self.azure_available or not self.azure_client:
            return {"success": False, "error": "Azure OpenAI client not available"}
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Prepare kwargs
            kwargs = {
                "model": self.azure_deployment,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            
            # Add response_format if specified
            if response_format:
                kwargs["response_format"] = response_format
            
            # Call Azure OpenAI
            response = self.azure_client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            
            # If response_format is json_object, parse it
            if response_format and response_format.get("type") == "json_object":
                try:
                    parsed_data = json.loads(content)
                    return {"success": True, "data": parsed_data}
                except json.JSONDecodeError:
                    # If parsing fails, return as text
                    return {"success": True, "data": {"text": content}}
            else:
                return {"success": True, "data": {"text": content}}
                
        except Exception as e:
            return {"success": False, "error": f"Azure OpenAI error: {str(e)}"}
    
    # ============================================================
    # SOCIAL MEDIA CONTENT GENERATION
    # ============================================================
    def generate_social_content(
        self,
        campaign_goal: str,
        platform: str = "Instagram",
        target_audience: str = "General audience",
        brand_tone: str = "professional",
        additional_details: str = ""
    ) -> Dict[str, Any]:
        """
        Generate social media content (caption, hashtags, image prompt, CTA)
        
        Args:
            campaign_goal: What the campaign aims to achieve
            platform: Social media platform (Instagram, Facebook, LinkedIn, Twitter)
            target_audience: Description of target audience
            brand_tone: Tone of voice (professional, casual, playful, inspirational)
            additional_details: Any extra context or requirements
            
        Returns:
            Dict with success status and generated content or error
        """
        user_message = f"""
Campaign Goal: {campaign_goal}
Platform: {platform}
Target Audience: {target_audience}
Brand Tone: {brand_tone}
Additional Details: {additional_details}

Please generate engaging social media content for this campaign.
"""
        return self._call_azure_openai(
            prompts.SOCIAL_MEDIA_PROMPT, 
            user_message,
            response_format={"type": "json_object"}
        )
    
    # ============================================================
    # COPYWRITING GENERATION
    # ============================================================
    def generate_copy(
        self,
        product_service: str,
        copy_type: str = "description",
        tone: str = "professional",
        length: str = "medium",
        key_points: str = ""
    ) -> Dict[str, Any]:
        """
        Generate marketing copy (headline, body copy, CTA)
        
        Args:
            product_service: Product or service description
            copy_type: Type of copy (description, ad copy, email, landing page, tagline)
            tone: Writing tone (professional, conversational, authoritative, friendly, urgent)
            length: Copy length (short, medium, long)
            key_points: Key selling points to emphasize
            
        Returns:
            Dict with success status and generated copy or error
        """
        user_message = f"""
Product/Service: {product_service}
Copy Type: {copy_type}
Tone: {tone}
Length: {length}
Key Points: {key_points}

Please generate compelling marketing copy for this product/service.
"""
        return self._call_azure_openai(
            prompts.COPYWRITING_PROMPT, 
            user_message,
            response_format={"type": "json_object"}
        )
    
    # ============================================================
    # BANNER DESIGN SPECS GENERATION
    # ============================================================
    def generate_banner_design(
        self,
        dimensions: str = "1200x628",
        message: str = "",
        brand_colors: str = "use vibrant colors",
        cta_text: str = "Learn More"
    ) -> Dict[str, Any]:
        """
        Generate banner design specifications
        
        Args:
            dimensions: Banner dimensions (e.g., 1200x628, 728x90, 300x250)
            message: Main message to convey
            brand_colors: Brand color palette or color preferences
            cta_text: Call-to-action button text
            
        Returns:
            Dict with success status and design specs or error
        """
        user_message = f"""
Dimensions: {dimensions}
Message: {message}
Brand Colors: {brand_colors}
CTA Text: {cta_text}

Please generate detailed banner design specifications.
"""
        return self._call_azure_openai(
            prompts.BANNER_DESIGN_PROMPT, 
            user_message,
            response_format={"type": "json_object"}
        )
    
    # ============================================================
    # IMAGE PROMPT OPTIMIZATION
    # ============================================================
    def generate_image_prompt(
        self,
        description: str,
        style: str = "realistic",
        mood: str = "professional",
        context: str = "social media"
    ) -> Dict[str, Any]:
        """
        Optimize image generation prompt for DALL-E or similar models
        
        Args:
            description: Basic description of desired image
            style: Artistic style (realistic, digital art, illustration, 3D render, etc.)
            mood: Mood or atmosphere (professional, energetic, calm, dramatic, etc.)
            context: Usage context (social media, website, print, advertisement)
            
        Returns:
            Dict with success status and optimized prompt or error
        """
        user_message = f"""
Description: {description}
Style: {style}
Mood: {mood}
Context: {context}

Please optimize this into a detailed image generation prompt.
"""
        return self._call_azure_openai(
            prompts.IMAGE_GENERATION_PROMPT, 
            user_message,
            response_format={"type": "json_object"}
        )
    
    # ============================================================
    # GEMINI IMAGE GENERATION
    # ============================================================
    def generate_image_with_gemini(
        self, 
        prompt: str,
        number_of_images: int = 1
    ) -> Dict[str, Any]:
        """
        Generate image using Google Gemini (Imagen 4.0)
        
        Args:
            prompt: Image generation prompt
            number_of_images: Number of images to generate (1-4)
            
        Returns:
            Dict with success status and image data or error
        """
        if not self.gemini_available or not self.gemini_client:
            return {"success": False, "error": "Gemini client not available"}
        
        try:
            from google.genai import types
            
            response = self.gemini_client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=min(number_of_images, 4)
                ),
            )
            
            # Extract image URLs or data
            images = []
            for img in response.generated_images:
                # Images come as bytes, you can save them or encode as base64
                images.append({
                    "image_data": img.image._image_bytes if hasattr(img.image, '_image_bytes') else None,
                    "generated": True
                })
            
            return {
                "success": True, 
                "data": {
                    "images": images,
                    "count": len(images),
                    "prompt": prompt
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Gemini generation error: {str(e)}"}
    
    # ============================================================
    # IMAGE EDITING INSTRUCTIONS
    # ============================================================
    def generate_image_edit_instructions(
        self,
        edit_request: str,
        image_context: str = "",
        desired_outcome: str = ""
    ) -> Dict[str, Any]:
        """
        Generate image editing instructions
        
        Args:
            edit_request: What needs to be edited
            image_context: Description of the current image
            desired_outcome: What the final result should look like
            
        Returns:
            Dict with success status and edit instructions or error
        """
        user_message = f"""
Edit Request: {edit_request}
Image Context: {image_context}
Desired Outcome: {desired_outcome}

Please provide detailed image editing instructions.
"""
        return self._call_azure_openai(
            prompts.IMAGE_EDIT_PROMPT, 
            user_message,
            response_format={"type": "json_object"}
        )
    
    # ============================================================
    # GENERIC TEXT GENERATION (Fallback)
    # ============================================================
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generic text generation (for backwards compatibility)
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum length of response
            
        Returns:
            Generated text string
        """
        system_prompt = "You are a creative content assistant. Generate engaging, professional content based on user requests."
        
        result = self._call_azure_openai(
            system_prompt=system_prompt,
            user_message=prompt,
            max_tokens=max_tokens,
            temperature=0.8
        )
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, dict):
                # Try to extract text from various possible keys
                for key in ["text", "content", "response", "output"]:
                    if key in data:
                        return str(data[key])
                # Return first string value found
                return next((str(v) for v in data.values() if isinstance(v, str)), str(data))
            return str(data)
        else:
            return f"Error: {result['error']}"
    
    # ============================================================
    # HEALTH CHECK
    # ============================================================
    def health_check(self) -> Dict[str, Any]:
        """
        Check if LLM services are properly configured
        
        Returns:
            Dict with status information
        """
        return {
            "azure_openai": {
                "available": self.azure_available,
                "endpoint": self.azure_endpoint,
                "deployment": self.azure_deployment
            },
            "gemini": {
                "available": self.gemini_available,
            },
            "overall_status": "ok" if (self.azure_available or self.gemini_available) else "error"
        }


# Create singleton instance
llm_service = LLMService()