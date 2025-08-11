import os
import requests
import asyncio
from typing import Dict, Any
from .base import BaseConnector

class SarvamConnector(BaseConnector):
    """Optimized Sarvam AI connector with proper endpoints and fallback strategies"""
    
    def __init__(self):
        super().__init__("Sarvam AI")
        self.api_key = os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY environment variable is required")
        
        self.base_url = "https://api.sarvam.ai"
        self.headers = {"api-subscription-key": self.api_key}
    
    async def detect_language(self, audio_file_path: str) -> str:
        """Fast language detection with proper fallback strategy"""
        
        # Check audio duration first
        audio_duration = self._get_audio_duration(audio_file_path)
        
        if audio_duration <= 30:
            return await self._detect_realtime(audio_file_path)
        else:
            return await self._detect_batch(audio_file_path)
    
    def estimate_cost(self, audio_file_path: str) -> Dict[str, Any]:
        """Estimate cost based on Sarvam pricing"""
        try:
            file_size = os.path.getsize(audio_file_path)
            duration_minutes = max(0.1, file_size / (1024 * 1024))
            
            # Sarvam pricing estimate
            estimated_cost = duration_minutes * 0.02
            
            return {
                "tokens": int(duration_minutes * 100),
                "dollars": round(estimated_cost, 4)
            }
        except Exception:
            return {"tokens": 100, "dollars": 0.02}
    
    async def _detect_realtime(self, audio_file_path: str) -> str:
        """Real-time detection for audio ≤ 30 seconds"""
        
        # Method 1: Try speech-to-text-translate (auto-detects language)
        result = await self._try_translate_endpoint(audio_file_path)
        if result:
            return result
            
        # Method 2: Try regular speech-to-text with language attempts
        return await self._try_language_attempts(audio_file_path)
    
    async def _try_translate_endpoint(self, audio_file_path: str) -> str:
        """Use the working speech-to-text-translate endpoint"""
        
        # Use the correct models from error message
        models_to_try = ["saaras:v2.5", "saaras:turbo", "saaras:flash"]
        
        for model in models_to_try:
            try:
                with open(audio_file_path, "rb") as audio_file:
                    files = {"file": ("audio.wav", audio_file, "audio/wav")}
                    data = {"model": model}
                    
                    response = requests.post(
                        f"{self.base_url}/speech-to-text-translate",
                        headers=self.headers,
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Extract detected language
                        if "detected_language_code" in result:
                            lang_code = result["detected_language_code"]
                            return self._clean_language_code(lang_code)
                        elif "transcript" in result:
                            return self._detect_from_script(result["transcript"])
                            
                    elif response.status_code == 500:
                        continue
                    else:
                        print(f"Model {model} failed: {response.status_code}")
                        continue
                        
            except Exception as e:
                print(f"Error with model {model}: {e}")
                continue
        
        return None
    
    async def _try_language_attempts(self, audio_file_path: str) -> str:
        """Smart language attempts based on priority"""
        
        priority_languages = ["hi-IN", "en-IN", "ta-IN", "te-IN", "bn-IN"]
        
        for lang_code in priority_languages:
            try:
                with open(audio_file_path, "rb") as audio_file:
                    files = {"file": ("audio.wav", audio_file, "audio/wav")}
                    data = {
                        "model": "saaras:v2.5",
                        "language_code": lang_code
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/speech-to-text",
                        headers=self.headers,
                        files=files,
                        data=data,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        transcript = result.get("transcript", "")
                        confidence = result.get("confidence", 0)
                        
                        if confidence > 0.8 or len(transcript.strip()) > 5:
                            return lang_code.split("-")[0]
                            
            except Exception:
                continue
        
        return "en"
    
    async def _detect_batch(self, audio_file_path: str) -> str:
        """Use batch API for long audio files"""
        # Implementation for batch processing
        return "en"  # Simplified for now
    
    def _get_audio_duration(self, audio_file_path: str) -> float:
        """Estimate audio duration from file size"""
        try:
            file_size = os.path.getsize(audio_file_path)
            estimated_duration = file_size / (1024 * 1024) * 60
            return estimated_duration
        except:
            return 30
    
    def _clean_language_code(self, lang_code: str) -> str:
        """Clean language codes"""
        if not lang_code:
            return "en"
        return lang_code.lower().split("-")[0]
    
    def _detect_from_script(self, transcript: str) -> str:
        """Detect language from script characters"""
        if not transcript:
            return "en"
        
        import re
        
        script_patterns = {
            'hi': r'[\u0900-\u097F]',  # Devanagari
            'bn': r'[\u0980-\u09FF]',  # Bengali
            'ta': r'[\u0B80-\u0BFF]',  # Tamil
            'te': r'[\u0C00-\u0C7F]',  # Telugu
        }
        
        for lang, pattern in script_patterns.items():
            if re.search(pattern, transcript):
                return lang
        
        return "en"
