import os
import time
import asyncio
from typing import Dict, Any
from .base import BaseConnector


class OpenAIMockConnector(BaseConnector):
    """OpenAI mock connector for demonstration purposes"""
    
    def __init__(self):
        super().__init__("OpenAI (Mock)")
    
    async def detect_language(self, audio_file_path: str) -> str:
        """Mock language detection - simulates API call delay"""
        # Simulate API processing time
        await asyncio.sleep(0.5)
        
        # Mock language detection logic
        # In a real scenario, this would call OpenAI's Whisper API
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
        """Mock cost estimation for OpenAI Whisper API"""
        try:
            file_size = os.path.getsize(audio_file_path)
            # OpenAI Whisper pricing: $0.006 per minute
            # Assuming 1 minute = ~1MB
            duration_minutes = max(0.1, file_size / (1024 * 1024))
            estimated_cost = duration_minutes * 0.006
            
            return {
                "tokens": int(duration_minutes * 1000),  # Rough token estimation
                "dollars": round(estimated_cost, 6)
            }
        except:
            return {
                "tokens": 1000,
                "dollars": 0.006
            }
