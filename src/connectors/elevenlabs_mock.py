import os
import time
import asyncio
from typing import Dict, Any
from .base import BaseConnector


class ElevenLabsMockConnector(BaseConnector):
    """ElevenLabs mock connector for demonstration purposes"""
    
    def __init__(self):
        super().__init__("ElevenLabs (Mock)")
    
    async def detect_language(self, audio_file_path: str) -> str:
        """Mock language detection - simulates API call delay"""
        # Simulate API processing time
        await asyncio.sleep(0.3)
        
        # Mock language detection logic
        # In a real scenario, this would call ElevenLabs' language detection API
        file_name = os.path.basename(audio_file_path).lower()
        
        # Simple mock logic based on filename - check for exact matches first
        if "hindi" in file_name:
            return "hi"
        elif "tamil" in file_name:
            return "ta"
        elif "telugu" in file_name:
            return "te"
        elif "kannada" in file_name:
            return "kn"
        elif "malayalam" in file_name:
            return "ml"
        elif "bengali" in file_name:
            return "bn"
        elif "marathi" in file_name:
            return "mr"
        elif "gujarati" in file_name:
            return "gu"
        elif "punjabi" in file_name:
            return "pa"
        elif "urdu" in file_name:
            return "ur"
        elif "sanskrit" in file_name:
            return "sa"
        else:
            # Default to English for most cases
            return "en"
    
    def estimate_cost(self, audio_file_path: str) -> Dict[str, Any]:
        """Mock cost estimation for ElevenLabs API"""
        try:
            file_size = os.path.getsize(audio_file_path)
            # ElevenLabs pricing: typically per character or per minute
            # Assuming 1 minute = ~1MB, and cost is $0.005 per minute
            duration_minutes = max(0.1, file_size / (1024 * 1024))
            estimated_cost = duration_minutes * 0.005
            
            return {
                "tokens": int(duration_minutes * 500),  # Rough token estimation
                "dollars": round(estimated_cost, 4)
            }
        except:
            return {
                "tokens": 500,
                "dollars": 0.005
            }
