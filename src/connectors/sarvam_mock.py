import asyncio
import os
from typing import Dict, Any
from .base import BaseConnector


class SarvamMockConnector(BaseConnector):
    """Mock Sarvam AI connector for testing without real API calls"""

    def __init__(self):
        super().__init__("Sarvam AI (Mock)")

    async def detect_language(self, audio_file_path: str) -> str:
        """Mock language detection based on filename"""
        # Simulate API call delay
        await asyncio.sleep(1.5)
        
        # Extract filename and detect language based on keywords
        file_name = os.path.basename(audio_file_path).lower()
        
        # Language detection logic based on filename
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
        elif "french" in file_name:
            return "fr"
        elif "german" in file_name:
            return "de"
        elif "spanish" in file_name:
            return "es"
        elif "chinese" in file_name:
            return "zh"
        elif "japanese" in file_name:
            return "ja"
        elif "korean" in file_name:
            return "ko"
        elif "arabic" in file_name:
            return "ar"
        elif "russian" in file_name:
            return "ru"
        else:
            # Default to English for unknown languages
            return "en"

    def estimate_cost(self, audio_file_path: str) -> Dict[str, Any]:
        """Mock cost estimation for Sarvam AI"""
        try:
            file_size = os.path.getsize(audio_file_path)
            # Mock cost calculation: $0.001 per MB
            cost_per_mb = 0.001
            estimated_cost = (file_size / (1024 * 1024)) * cost_per_mb
            
            return {
                "tokens": int(file_size / 100),  # Mock token estimation
                "dollars": round(estimated_cost, 6)
            }
        except Exception:
            return {"tokens": 100, "dollars": 0.001}
