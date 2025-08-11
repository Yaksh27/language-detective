import asyncio
import time
from typing import List
from .models import ProviderResult, LanguageDetectionResponse
from .connectors.gemini import GeminiConnector
from .connectors.sarvam_mock import SarvamMockConnector
from .connectors.openai_mock import OpenAIMockConnector
from .connectors.elevenlabs import ElevenLabsConnector


class LanguageDetectionCoordinator:
    """Coordinates language detection across multiple providers"""
    
    def __init__(self):
        self.providers = [
            GeminiConnector(),
            SarvamMockConnector(),
            OpenAIMockConnector(),
            ElevenLabsConnector()
        ]
    
    async def detect_language_all_providers(self, audio_file_path: str) -> LanguageDetectionResponse:
        """Execute language detection with all providers concurrently"""
        start_time = time.time()
        
        # Execute all providers concurrently
        tasks = [
            provider.execute_with_metrics(audio_file_path)
            for provider in self.providers
        ]
        
        # Wait for all providers to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error result for failed providers
                error_result = ProviderResult(
                    provider_name=self.providers[i].provider_name,
                    detected_language=None,
                    time_taken=0.0,
                    estimated_cost={"tokens": 0, "dollars": 0.0},
                    status="error",
                    error_message=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        total_time = time.time() - start_time
        
        # Count successful and failed providers
        successful_providers = sum(1 for r in processed_results if r.status == "success")
        failed_providers = len(processed_results) - successful_providers
        
        return LanguageDetectionResponse(
            results=processed_results,
            total_time=total_time,
            successful_providers=successful_providers,
            failed_providers=failed_providers
        )
    
    async def detect_language_single_provider(self, audio_file_path: str, provider_name: str) -> ProviderResult:
        """Execute language detection with a single provider"""
        provider = next((p for p in self.providers if p.provider_name == provider_name), None)
        
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        return await provider.execute_with_metrics(audio_file_path)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [provider.provider_name for provider in self.providers]
