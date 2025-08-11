import os
import requests
import asyncio
from typing import Dict, Any, Optional
from .base import BaseConnector


class ElevenLabsConnector(BaseConnector):
    """Real ElevenLabs connector using Speech-to-Text for language detection"""
    
    def __init__(self):
        super().__init__("ElevenLabs")
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key
            # Don't set Content-Type for multipart uploads
        }
    
    async def detect_language(self, audio_file_path: str) -> str:
        """Detect language using ElevenLabs Speech-to-Text API"""
        
        print(f"🔍 ElevenLabs: Starting detection for {os.path.basename(audio_file_path)}")
        
        if not os.path.exists(audio_file_path):
            print(f"❌ ElevenLabs: File not found: {audio_file_path}")
            return "en"
        
        try:
            # Use ElevenLabs Speech-to-Text API for language detection
            result = await self._transcribe_with_language_detection(audio_file_path)
            
            if result:
                detected_language = self._extract_language_from_result(result)
                print(f"✅ ElevenLabs: Detected language: {detected_language}")
                return detected_language
            else:
                print("❌ ElevenLabs: Transcription failed")
                return "en"
                
        except Exception as e:
            print(f"💥 ElevenLabs: Error: {e}")
            return "en"
    
    async def _transcribe_with_language_detection(self, audio_file_path: str) -> Optional[Dict]:
        """Alternative approach with different file parameter structure"""
        
        try:
            print("🎤 ElevenLabs: Calling Speech-to-Text API...")
            
            # Read file data
            with open(audio_file_path, "rb") as f:
                file_data = f.read()
            
            # Alternative 1: Simple file parameter
            files = {
                "file": file_data
            }
            
            data = {
                "model_id": "scribe_v1",
                "language": "auto"
            }
            
            response = requests.post(
                f"{self.base_url}/speech-to-text",
                headers={"xi-api-key": self.api_key},
                files=files,
                data=data,
                timeout=60
            )
            
            # If that fails, try Alternative 2
            if response.status_code == 400:
                print("🔄 ElevenLabs: Trying alternative file format...")
                
                files = {
                    "file": (os.path.basename(audio_file_path), file_data, self._get_mime_type(audio_file_path))
                }
                
                response = requests.post(
                    f"{self.base_url}/speech-to-text",
                    headers={"xi-api-key": self.api_key},
                    files=files,
                    data=data,
                    timeout=60
                )
            
            print(f"📊 ElevenLabs: API response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ ElevenLabs: Transcription successful")
                return result
            else:
                print(f"❌ ElevenLabs: API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"💥 ElevenLabs: Error: {e}")
            return None

    
    def _extract_language_from_result(self, result: Dict) -> str:
        """Extract detected language from ElevenLabs response"""
        
        # Check for direct language detection in response
        if "detected_language" in result:
            return self._clean_language_code(result["detected_language"])
        
        if "language" in result:
            return self._clean_language_code(result["language"])
        
        # Check in alignment data
        if "alignment" in result and isinstance(result["alignment"], dict):
            if "language" in result["alignment"]:
                return self._clean_language_code(result["alignment"]["language"])
        
        # Fallback: analyze transcript text
        if "text" in result and result["text"]:
            transcript = result["text"]
            print(f"📝 ElevenLabs: Transcript: '{transcript[:100]}...'")
            return self._detect_from_text(transcript)
        
        return "en"
    
    def _detect_from_text(self, text: str) -> str:
        """Detect language from transcript text using Unicode patterns"""
        import re
        
        if not text:
            return "en"
        
        # Unicode script detection
        script_patterns = {
            'hi': r'[\u0900-\u097F]',      # Devanagari (Hindi)
            'bn': r'[\u0980-\u09FF]',      # Bengali
            'ta': r'[\u0B80-\u0BFF]',      # Tamil
            'te': r'[\u0C00-\u0C7F]',      # Telugu
            'kn': r'[\u0C80-\u0CFF]',      # Kannada
            'ml': r'[\u0D00-\u0D7F]',      # Malayalam
            'gu': r'[\u0A80-\u0AFF]',      # Gujarati
            'pa': r'[\u0A00-\u0A7F]',      # Punjabi
            'ar': r'[\u0600-\u06FF]',      # Arabic
            'zh': r'[\u4e00-\u9fff]',      # Chinese
            'ja': r'[\u3040-\u309f\u30a0-\u30ff]',  # Japanese
            'ko': r'[\uac00-\ud7af]',      # Korean
            'ru': r'[\u0400-\u04FF]',      # Cyrillic
        }
        
        # Check for non-Latin scripts first
        for lang, pattern in script_patterns.items():
            if re.search(pattern, text):
                return lang
        
        # Check for common European language patterns
        text_lower = text.lower()
        
        # French patterns
        if re.search(r'\b(le|la|de|et|est|dans|pour|avec|que|un|une|sur|par|il|elle|vous|nous)\b', text_lower):
            return "fr"
        
        # German patterns  
        elif re.search(r'\b(der|die|das|und|ist|in|zu|von|ein|eine|mit|für|auf|dem|den|ich|du|er|sie)\b', text_lower):
            return "de"
        
        # Spanish patterns
        elif re.search(r'\b(el|la|de|y|en|es|por|con|que|un|una|se|te|le|los|las|yo|tú|él|ella)\b', text_lower):
            return "es"
        
        # Italian patterns
        elif re.search(r'\b(il|la|di|e|in|è|per|con|che|un|una|si|lo|gli|le|io|tu|lui|lei)\b', text_lower):
            return "it"
        
        # Portuguese patterns
        elif re.search(r'\b(o|a|de|e|em|é|para|com|que|um|uma|se|do|da|dos|das|eu|você|ele|ela)\b', text_lower):
            return "pt"
        
        # Default to English
        return "en"
    
    def _clean_language_code(self, lang_code: str) -> str:
        """Clean and standardize language codes"""
        if not lang_code:
            return "en"
        
        # Remove region suffixes and normalize
        clean_code = lang_code.lower().split("-")[0].split("_")[0]
        
        # Map common variations
        mappings = {
            'eng': 'en', 'english': 'en',
            'hin': 'hi', 'hindi': 'hi',
            'fra': 'fr', 'french': 'fr', 'français': 'fr',
            'deu': 'de', 'german': 'de', 'deutsch': 'de',
            'esp': 'es', 'spanish': 'es', 'español': 'es',
            'ita': 'it', 'italian': 'it', 'italiano': 'it',
            'por': 'pt', 'portuguese': 'pt', 'português': 'pt',
            'jpn': 'ja', 'japanese': 'ja',
            'kor': 'ko', 'korean': 'ko',
            'cmn': 'zh', 'mandarin': 'zh', 'chinese': 'zh',
            'rus': 'ru', 'russian': 'ru'
        }
        
        return mappings.get(clean_code, clean_code)
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        mime_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav', 
            '.m4a': 'audio/m4a',
            '.aac': 'audio/aac',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac'
        }
        
        return mime_types.get(ext, 'audio/mpeg')
    
    def estimate_cost(self, audio_file_path: str) -> Dict[str, Any]:
        """Estimate cost based on ElevenLabs Speech-to-Text pricing"""
        try:
            file_size = os.path.getsize(audio_file_path)
            duration_minutes = max(0.1, file_size / (1024 * 1024))
            
            # ElevenLabs Speech-to-Text: ~$0.002-0.005 per minute
            estimated_cost = duration_minutes * 0.005
            
            return {
                "tokens": int(duration_minutes * 1000),
                "dollars": round(estimated_cost, 4)
            }
        except Exception:
            return {"tokens": 1000, "dollars": 0.005}
