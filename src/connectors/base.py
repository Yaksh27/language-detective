from abc import ABC, abstractmethod
import time
from typing import Dict, Any
from ..models import ProviderResult, ProviderStatus


class BaseConnector(ABC):
    """Base class for all provider connectors"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
    
    @abstractmethod
    async def detect_language(self, audio_file_path: str) -> str:
        """Detect language from audio file"""
        pass
    
    @abstractmethod
    def estimate_cost(self, audio_file_path: str) -> Dict[str, Any]:
        """Estimate cost for the operation"""
        pass
    
    async def execute_with_metrics(self, audio_file_path: str) -> ProviderResult:
        """Execute language detection with timing and error handling"""
        start_time = time.time()
        
        try:
            detected_language = await self.detect_language(audio_file_path)
            time_taken = time.time() - start_time
            
            return ProviderResult(
                provider_name=self.provider_name,
                detected_language=detected_language,
                time_taken=time_taken,
                estimated_cost=self.estimate_cost(audio_file_path),
                status=ProviderStatus.SUCCESS,
                error_message=None
            )
            
        except Exception as e:
            time_taken = time.time() - start_time
            
            return ProviderResult(
                provider_name=self.provider_name,
                detected_language=None,
                time_taken=time_taken,
                estimated_cost=self.estimate_cost(audio_file_path),
                status=ProviderStatus.ERROR,
                error_message=str(e)
            )
