import os
import base64
import google.generativeai as genai
from typing import Dict, Any
from .base import BaseConnector


class GeminiConnector(BaseConnector):
    """Google Gemini connector for language detection"""
    
    def __init__(self):
        super().__init__("Google Gemini")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
    
    async def detect_language(self, audio_file_path: str) -> str:
        """Detect language using Gemini's audio analysis capabilities"""
        try:
            # Read and encode the audio file
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Create prompt for language detection
            prompt = """
            Analyze this audio file and detect the spoken language. 
            Return only the ISO 639-1 language code (e.g., 'en' for English, 'hi' for Hindi, 'ta' for Tamil).
            
            Focus on Indian languages if detected. Common Indian language codes:
            - hi: Hindi
            - ta: Tamil
            - te: Telugu
            - kn: Kannada
            - ml: Malayalam
            - bn: Bengali
            - mr: Marathi
            - gu: Gujarati
            - pa: Punjabi
            - ur: Urdu
            - sa: Sanskrit
            
            Return only the language code, nothing else.
            """
            
            # For Gemini, we'll use text generation since audio analysis might require different approach
            # This is a simplified implementation - in production you might need to use Gemini's audio models
            response = self.model.generate_content([
                prompt,
                {"mime_type": "audio/wav", "data": audio_base64}
            ])
            
            # Extract language code from response
            detected_lang = response.text.strip().lower()
            
            # Validate and return language code
            valid_codes = ['en', 'hi', 'ta', 'te', 'kn', 'ml', 'bn', 'mr', 'gu', 'pa', 'ur', 'sa', 
                          'fr', 'de', 'es', 'zh', 'ja', 'ko', 'ar', 'ru']
            
            if detected_lang in valid_codes:
                return detected_lang
            else:
                # Fallback to English if detection fails
                return 'en'
                
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def estimate_cost(self, audio_file_path: str) -> Dict[str, Any]:
        """Estimate cost for Gemini API call"""
        # Get file size for rough estimation
        try:
            file_size = os.path.getsize(audio_file_path)
            # Rough estimation: 1 token per 4 characters + base cost
            estimated_tokens = max(100, file_size // 4)
            estimated_cost = estimated_tokens * 0.0001  # Approximate Gemini pricing
            
            return {
                "tokens": estimated_tokens,
                "dollars": round(estimated_cost, 6)
            }
        except:
            return {
                "tokens": 100,
                "dollars": 0.01
            }
