import os
import requests
import asyncio
from typing import Dict, Any, Optional
from .base import BaseConnector


class ElevenLabsConnector(BaseConnector):
    """Real ElevenLabs connector with automatic language detection via Speech-to-Text"""
    
    def __init__(self):
        super().__init__("ElevenLabs")
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key
        }
        
        # ElevenLabs supports 99+ languages with automatic detection
        self.supported_languages = {
            'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 
            'ar', 'zh', 'ja', 'hu', 'ko', 'hi', 'bn', 'ta', 'te', 'kn', 'ml',
            'gu', 'mr', 'pa', 'ur', 'ne', 'si', 'th', 'vi', 'id', 'ms', 'tl',
            'sv', 'da', 'no', 'fi', 'el', 'he', 'fa', 'bg', 'hr', 'sk', 'sl',
            'et', 'lv', 'lt', 'mt', 'ga', 'cy', 'eu', 'ca', 'gl', 'ast', 'an'
        }
    
    async def detect_language(self, audio_file_path: str) -> str:
        """
        Detect language using ElevenLabs Speech-to-Text with automatic language detection
        This is MUCH better than Sarvam AI - supports 99 languages and handles M4A files
        """
        
        print(f"🔍 ElevenLabs: Starting detection for {os.path.basename(audio_file_path)}")
        
        if not os.path.exists(audio_file_path):
            print(f"❌ ElevenLabs: File not found: {audio_file_path}")
            return "en"
        
        try:
            # ElevenLabs Speech-to-Text with automatic language detection
            transcript_data = await self._transcribe_audio(audio_file_path)
            
            if not transcript_data:
                print("❌ ElevenLabs: Transcription failed")
                return "en"
            
            # Extract detected language from transcription response
            detected_language = self._extract_language_from_response(transcript_data)
            
            print(f"✅ ElevenLabs: Detected language: {detected_language}")
            return detected_language
            
        except Exception as e:
            print(f"💥 ElevenLabs: Error in language detection: {e}")
            return "en"
    
    async def _transcribe_audio(self, audio_file_path: str) -> Optional[Dict]:
        """Use ElevenLabs Speech-to-Text API with automatic language detection"""
        
        print("🎤 ElevenLabs: Transcribing audio with language detection...")
        
        try:
            # Determine MIME type based on file extension
            mime_type = self._get_mime_type(audio_file_path)
            
            with open(audio_file_path, "rb") as audio_file:
                files = {
                    "audio": (os.path.basename(audio_file_path), audio_file, mime_type)
                }
                
                # ElevenLabs Speech-to-Text parameters
                data = {
                    "model_id": "eleven_multilingual_v2",  # Supports 99 languages
                    "language": "auto",  # Automatic language detection
                    "timestamp_granularities[]": "word",  # Get word-level timestamps
                    "detect_language": "true"  # Enable language detection
                }
                
                response = requests.post(
                    f"{self.base_url}/speech-to-text",
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=120  # ElevenLabs can handle longer files
                )
                
                print(f"📊 ElevenLabs: Transcription response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ ElevenLabs: Transcription successful")
                    return result
                else:
                    print(f"❌ ElevenLabs: Transcription failed: {response.status_code} - {response.text[:300]}")
                    return None
                    
        except Exception as e:
            print(f"💥 ElevenLabs: Transcription error: {e}")
            return None
    
    def _extract_language_from_response(self, transcript_data: Dict) -> str:
        """Extract detected language from ElevenLabs response"""
        
        # ElevenLabs returns language in different possible fields
        detected_lang = None
        
        # Method 1: Check for direct language field
        if "detected_language" in transcript_data:
            detected_lang = transcript_data["detected_language"]
        elif "language" in transcript_data:
            detected_lang = transcript_data["language"]
        
        # Method 2: Check alignment data for language info
        elif "alignment" in transcript_data:
            alignment = transcript_data["alignment"]
            if isinstance(alignment, dict) and "language" in alignment:
                detected_lang = alignment["language"]
        
        # Method 3: Analyze transcript text if language not directly provided
        if not detected_lang and "text" in transcript_data:
            transcript_text = transcript_data["text"]
            if transcript_text:
                print(f"📝 ElevenLabs: Transcript: '{transcript_text[:100]}...'")
                detected_lang = self._detect_language_from_text(transcript_text)
        
        # Clean and validate language code
        if detected_lang:
            clean_lang = self._clean_language_code(detected_lang)
            if clean_lang in self.supported_languages:
                return clean_lang
        
        # Fallback to English
        return "en"
    
    def _detect_language_from_text(self, text: str) -> str:
        """Fallback language detection using Unicode script analysis"""
        import re
        
        if not text:
            return "en"
        
        # Unicode script patterns for major languages
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
            'el': r'[\u0370-\u03FF]',      # Greek
            'th': r'[\u0E00-\u0E7F]'       # Thai
        }
        
        # Count characters for each script
        for lang, pattern in script_patterns.items():
            if re.search(pattern, text):
                char_count = len(re.findall(pattern, text))
                if char_count > len(text) * 0.1:  # At least 10% of characters
                    return lang
        
        # Check for common European languages using word patterns
        if re.search(r'\b(the|and|is|in|to|of|a|that|it|with|for|as|was|on|are|you)\b', text.lower()):
            return "en"
        elif re.search(r'\b(le|la|de|et|est|dans|pour|avec|que|un|une|sur|par|il|elle)\b', text.lower()):
            return "fr"
        elif re.search(r'\b(der|die|das|und|ist|in|zu|von|ein|eine|mit|für|auf|dem|den)\b', text.lower()):
            return "de"
        elif re.search(r'\b(el|la|de|y|en|es|por|con|que|un|una|se|te|le|los|las)\b', text.lower()):
            return "es"
        
        return "en"
    
    def _clean_language_code(self, lang_code: str) -> str:
        """Clean and standardize language codes"""
        if not lang_code:
            return "en"
        
        # Remove region suffixes and convert to lowercase
        clean_code = lang_code.lower().split("-")[0].split("_")[0]
        
        # Language code mappings
        language_mappings = {
            'eng': 'en', 'english': 'en',
            'hin': 'hi', 'hindi': 'hi',
            'ben': 'bn', 'bengali': 'bn',
            'tam': 'ta', 'tamil': 'ta',
            'tel': 'te', 'telugu': 'te',
            'kan': 'kn', 'kannada': 'kn',
            'mal': 'ml', 'malayalam': 'ml',
            'guj': 'gu', 'gujarati': 'gu',
            'mar': 'mr', 'marathi': 'mr',
            'pan': 'pa', 'punjabi': 'pa',
            'urd': 'ur', 'urdu': 'ur',
            'fra': 'fr', 'french': 'fr',
            'deu': 'de', 'german': 'de',
            'esp': 'es', 'spanish': 'es',
            'ita': 'it', 'italian': 'it',
            'por': 'pt', 'portuguese': 'pt',
            'rus': 'ru', 'russian': 'ru',
            'jpn': 'ja', 'japanese': 'ja',
            'kor': 'ko', 'korean': 'ko',
            'cmn': 'zh', 'mandarin': 'zh', 'chinese': 'zh'
        }
        
        return language_mappings.get(clean_code, clean_code)
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        mime_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/m4a',
            '.aac': 'audio/aac',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac',
            '.webm': 'audio/webm'
        }
        
        return mime_types.get(ext, 'audio/mpeg')
    
    def estimate_cost(self, audio_file_path: str) -> Dict[str, Any]:
        """Estimate cost based on ElevenLabs pricing"""
        try:
            file_size = os.path.getsize(audio_file_path)
            
            # ElevenLabs Speech-to-Text pricing (as of 2024):
            # $0.002 per minute for standard quality
            # $0.005 per minute for enhanced quality
            duration_minutes = max(0.1, file_size / (1024 * 1024))
            estimated_cost = duration_minutes * 0.005  # Enhanced quality
            
            return {
                "tokens": int(duration_minutes * 1000),  # Character-based estimation
                "dollars": round(estimated_cost, 4)
            }
        except Exception:
            return {
                "tokens": 1000,
                "dollars": 0.005
            }
    
    async def test_connection(self) -> bool:
        """Test API connectivity"""
        try:
            # Test with a simple API call to check authentication
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers,
                timeout=10
            )
            
            print(f"🧪 ElevenLabs: Connection test: {response.status_code}")
            return response.status_code == 200
            
        except Exception as e:
            print(f"💥 ElevenLabs: Connection error: {e}")
            return False
    
    async def debug_detection(self, audio_file_path: str):
        """Debug method for testing language detection"""
        
        print("\n" + "="*60)
        print("🔍 ELEVENLABS DEBUG MODE - LANGUAGE DETECTION")
        print("="*60)
        
        print(f"📁 File: {audio_file_path}")
        print(f"🔑 API Key: {self.api_key[:15]}..." if self.api_key else "❌ No API key")
        
        # Test connection
        connection_ok = await self.test_connection()
        print(f"🌐 Connection: {'✅ OK' if connection_ok else '❌ Failed'}")
        
        if connection_ok:
            # Test detection
            result = await self.detect_language(audio_file_path)
            print(f"🎯 Detection result: {result}")
        
        print("="*60)


# Usage example:
"""
async def test_elevenlabs():
    connector = ElevenLabsConnector()
    
    # Test with your problematic files
    files_to_test = [
        "hindi_test.m4a",
        "french_audio.wav",
        "your_36_second_file.m4a"
    ]
    
    for file_path in files_to_test:
        if os.path.exists(file_path):
            result = await connector.detect_language(file_path)
            print(f"File: {file_path} -> Language: {result}")

# Run the test
import asyncio
asyncio.run(test_elevenlabs())
"""
