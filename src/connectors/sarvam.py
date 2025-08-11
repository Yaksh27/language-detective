import os
import requests
import asyncio
import time
from typing import Dict, Any, Optional
from .base import BaseConnector


class SarvamConnector(BaseConnector):
    """Complete Sarvam AI connector using BATCH API for longer audio files"""
    
    def __init__(self):
        super().__init__("Sarvam AI")
        self.api_key = os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY environment variable is required")
        
        self.base_url = "https://api.sarvam.ai"
        self.headers = {"api-subscription-key": self.api_key}
        
        # Official supported languages from search results
        self.supported_languages = {
            'hi-IN': 'hi', 'bn-IN': 'bn', 'ta-IN': 'ta', 'te-IN': 'te', 
            'gu-IN': 'gu', 'kn-IN': 'kn', 'ml-IN': 'ml', 'mr-IN': 'mr',
            'pa-IN': 'pa', 'od-IN': 'od', 'en-IN': 'en'
        }
    
    async def detect_language(self, audio_file_path: str) -> str:
        """
        Detect language using the correct approach for your 36-second audio:
        1. Use BATCH API for files > 30 seconds
        2. Use text-lid API for language detection from transcript
        """
        
        print(f"🔍 Sarvam: Starting detection for {os.path.basename(audio_file_path)}")
        
        if not os.path.exists(audio_file_path):
            print(f"❌ Sarvam: File not found: {audio_file_path}")
            return "en"
        
        file_size = os.path.getsize(audio_file_path)
        estimated_duration = self._estimate_duration(audio_file_path, file_size)
        
        print(f"📊 Sarvam: File size: {file_size:,} bytes, duration: ~{estimated_duration:.1f}s")
        
        try:
            # For 36-second audio, use batch API
            if estimated_duration > 30:
                print("📦 Sarvam: Audio >30s, using Batch API...")
                transcript = await self._use_batch_api(audio_file_path)
            else:
                print("🚀 Sarvam: Audio ≤30s, using real-time API...")
                transcript = await self._use_realtime_api(audio_file_path)
            
            if not transcript or len(transcript.strip()) < 5:
                print("❌ Sarvam: No meaningful transcript obtained")
                return "en"
            
            print(f"📝 Sarvam: Transcript: '{transcript[:100]}{'...' if len(transcript) > 100 else ''}'")
            
            # Use text-lid API for language detection
            detected_language = await self._detect_language_from_text(transcript)
            
            print(f"✅ Sarvam: Final detection result: {detected_language}")
            return detected_language
            
        except Exception as e:
            print(f"💥 Sarvam: Error in detection: {e}")
            return "en"
    
    async def _use_batch_api(self, audio_file_path: str) -> Optional[str]:
        """Use Sarvam's Batch API for audio files > 30 seconds (up to 1 hour)"""
        
        print("📦 Sarvam: Submitting to Batch API...")
        
        try:
            # Step 1: Submit batch job
            with open(audio_file_path, "rb") as audio_file:
                files = {"file": ("audio.m4a", audio_file, "audio/m4a")}
                data = {
                    "model": "saarika:v2",  # Latest model from search results
                    "language_code": "unknown",  # Auto-detect
                    "enable_diarization": False,  # Faster processing
                    "with_word_timestamps": False  # Not needed for language detection
                }
                
                response = requests.post(
                    f"{self.base_url}/speech-to-text/batch",
                    headers={"api-subscription-key": self.api_key},
                    files=files,
                    data=data,
                    timeout=60
                )
                
                print(f"📊 Sarvam: Batch submit response: {response.status_code}")
                
                if response.status_code == 202:  # Accepted
                    job_data = response.json()
                    job_id = job_data.get("job_id")
                    print(f"✅ Sarvam: Batch job submitted: {job_id}")
                    
                    # Step 2: Poll for completion
                    return await self._poll_batch_job(job_id)
                else:
                    print(f"❌ Sarvam: Batch submission failed: {response.status_code} - {response.text[:300]}")
                    return None
                    
        except Exception as e:
            print(f"💥 Sarvam: Batch API error: {e}")
            return None
    
    async def _poll_batch_job(self, job_id: str) -> Optional[str]:
        """Poll batch job until completion (supports up to 1 hour audio)"""
        
        print(f"⏳ Sarvam: Polling batch job {job_id}...")
        
        max_attempts = 60  # 10 minutes max (10 seconds between polls)
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"{self.base_url}/speech-to-text/batch/{job_id}",
                    headers={"api-subscription-key": self.api_key},
                    timeout=15
                )
                
                if response.status_code == 200:
                    job_status = response.json()
                    status = job_status.get("status", "unknown")
                    
                    print(f"📊 Sarvam: Batch status: {status} (attempt {attempt + 1})")
                    
                    if status == "completed":
                        # Extract transcript from results
                        results = job_status.get("results", [])
                        if results and len(results) > 0:
                            transcript = results[0].get("transcript", "").strip()
                            if transcript:
                                print(f"✅ Sarvam: Batch completed with transcript")
                                return transcript
                    
                    elif status == "failed":
                        error_msg = job_status.get("error", "Unknown error")
                        print(f"❌ Sarvam: Batch job failed: {error_msg}")
                        return None
                    
                    elif status in ["queued", "processing"]:
                        # Still processing, wait and continue
                        await asyncio.sleep(10)
                        continue
                    else:
                        print(f"⚠️ Sarvam: Unknown status: {status}")
                        await asyncio.sleep(10)
                        continue
                else:
                    print(f"❌ Sarvam: Polling failed: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"💥 Sarvam: Polling error: {e}")
                await asyncio.sleep(10)
                continue
        
        print("❌ Sarvam: Batch job polling timed out")
        return None
    
    async def _use_realtime_api(self, audio_file_path: str) -> Optional[str]:
        """Use real-time API for files ≤ 30 seconds"""
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                files = {"file": ("audio.m4a", audio_file, "audio/m4a")}
                data = {
                    "model": "saarika:v2",
                    "language_code": "unknown"  # Auto-detect
                }
                
                response = requests.post(
                    f"{self.base_url}/speech-to-text",
                    headers={"api-subscription-key": self.api_key},
                    files=files,
                    data=data,
                    timeout=45
                )
                
                if response.status_code == 200:
                    result = response.json()
                    transcript = result.get("transcript", "").strip()
                    return transcript if transcript else None
                else:
                    print(f"❌ Sarvam: Real-time API failed: {response.status_code} - {response.text[:200]}")
                    return None
                    
        except Exception as e:
            print(f"💥 Sarvam: Real-time API error: {e}")
            return None
    
    async def _detect_language_from_text(self, text: str) -> str:
        """Use Sarvam's text-lid API to detect language from transcript"""
        
        print("🔍 Sarvam: Using text-lid API for language detection...")
        
        try:
            payload = {
                "input": text[:1000]  # Max 1000 characters for text-lid
            }
            
            response = requests.post(
                f"{self.base_url}/text-lid",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
                timeout=15
            )
            
            print(f"📊 Sarvam: Text-LID response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sarvam: Text-LID result: {result}")
                
                language_code = result.get("language_code")
                if language_code and language_code in self.supported_languages:
                    detected_lang = self.supported_languages[language_code]
                    print(f"🎯 Sarvam: Detected: {language_code} -> {detected_lang}")
                    return detected_lang
                else:
                    print(f"⚠️ Sarvam: Unsupported language: {language_code}")
                    return self._fallback_script_detection(text)
            else:
                print(f"❌ Sarvam: Text-LID failed: {response.text[:200]}")
                return self._fallback_script_detection(text)
                
        except Exception as e:
            print(f"💥 Sarvam: Text-LID error: {e}")
            return self._fallback_script_detection(text)
    
    def _fallback_script_detection(self, text: str) -> str:
        """Fallback using Unicode script detection"""
        import re
        
        # Hindi (Devanagari)
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"
        # Bengali
        elif re.search(r'[\u0980-\u09FF]', text):
            return "bn"
        # Tamil
        elif re.search(r'[\u0B80-\u0BFF]', text):
            return "ta"
        # Telugu  
        elif re.search(r'[\u0C00-\u0C7F]', text):
            return "te"
        # Other Indian scripts...
        else:
            return "en"
    
    def _estimate_duration(self, audio_file_path: str, file_size: int) -> float:
        """Better duration estimation for M4A files"""
        if audio_file_path.lower().endswith('.m4a'):
            # M4A is compressed, roughly 1MB per minute
            return max(1.0, (file_size / (1024 * 1024)) * 60)
        else:
            # WAV files are larger
            return max(1.0, (file_size / (1024 * 1024)) * 30)
    
    def estimate_cost(self, audio_file_path: str) -> Dict[str, Any]:
        """Estimate cost based on Sarvam's pricing"""
        try:
            file_size = os.path.getsize(audio_file_path)
            duration_minutes = max(0.1, self._estimate_duration(audio_file_path, file_size) / 60)
            
            # Batch API + text-lid pricing
            batch_cost = duration_minutes * 0.02  # Batch STT
            text_lid_cost = 0.001  # Small text processing cost
            
            return {
                "tokens": int(duration_minutes * 150),
                "dollars": round(batch_cost + text_lid_cost, 4)
            }
        except Exception:
            return {"tokens": 150, "dollars": 0.025}
    
    async def test_connection(self) -> bool:
        """Test API connectivity"""
        try:
            payload = {"input": "नमस्ते दोस्त"}
            response = requests.post(
                f"{self.base_url}/text-lid",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
