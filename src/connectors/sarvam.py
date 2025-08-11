import os
import requests
import json
from typing import Dict, Any
from .base import BaseConnector


class SarvamConnector(BaseConnector):
    """Sarvam AI connector for language detection"""
    
    def __init__(self):
        super().__init__("Sarvam AI")
        self.api_key = os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY environment variable is required")
        
        self.base_url = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def detect_language(self, audio_file_path: str) -> str:
        """Detect language using Sarvam AI's language detection API"""
        try:
            # Read the audio file
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Prepare the request payload
            payload = {
                "audio": audio_data.hex(),  # Convert to hex string for JSON transmission
                "task": "language_detection",
                "options": {
                    "return_language_code": True,
                    "supported_languages": [
                        "en", "hi", "ta", "te", "kn", "ml", "bn", "mr", "gu", "pa", "ur", "sa",
                        "fr", "de", "es", "zh", "ja", "ko", "ar", "ru"
                    ]
                }
            }
            
            # Make API call to Sarvam AI
            response = requests.post(
                f"{self.base_url}/v1/audio/analyze",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Sarvam API error: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # Extract language code from response
            if "language_code" in result:
                detected_lang = result["language_code"].lower()
            elif "language" in result:
                detected_lang = result["language"].lower()
            else:
                # Fallback: try to extract from any text response
                detected_lang = self._extract_language_from_text(result.get("text", ""))
            
            # Validate language code
            valid_codes = ['en', 'hi', 'ta', 'te', 'kn', 'ml', 'bn', 'mr', 'gu', 'pa', 'ur', 'sa', 
                          'fr', 'de', 'es', 'zh', 'ja', 'ko', 'ar', 'ru']
            
            if detected_lang in valid_codes:
                return detected_lang
            else:
                # Fallback to English if detection fails
                return 'en'
                
        except Exception as e:
            raise Exception(f"Sarvam AI API error: {str(e)}")
    
    def _extract_language_from_text(self, text: str) -> str:
        """Extract language code from text response"""
        text_lower = text.lower()
        
        # Language mapping for common responses
        language_mapping = {
            "hindi": "hi", "tamil": "ta", "telugu": "te", "kannada": "kn",
            "malayalam": "ml", "bengali": "bn", "marathi": "mr", "gujarati": "gu",
            "punjabi": "pa", "urdu": "ur", "sanskrit": "sa", "english": "en",
            "french": "fr", "german": "de", "spanish": "es", "chinese": "zh",
            "japanese": "ja", "korean": "ko", "arabic": "ar", "russian": "ru"
        }
        
        for lang_name, lang_code in language_mapping.items():
            if lang_name in text_lower:
                return lang_code
        
        return "en"  # Default fallback
    
    def estimate_cost(self, audio_file_path: str) -> Dict[str, Any]:
        """Estimate cost for Sarvam AI API call"""
        try:
            file_size = os.path.getsize(audio_file_path)
            # Sarvam AI pricing: typically per minute of audio
            # Assuming 1 minute = ~1MB, and cost is $0.01 per minute
            duration_minutes = max(0.1, file_size / (1024 * 1024))  # Rough estimation
            estimated_cost = duration_minutes * 0.01
            
            return {
                "tokens": int(duration_minutes * 100),  # Rough token estimation
                "dollars": round(estimated_cost, 4)
            }
        except:
            return {
                "tokens": 100,
                "dollars": 0.01
            }
