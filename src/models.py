from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes"""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    MALAYALAM = "ml"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    PUNJABI = "pa"
    URDU = "ur"
    SANSKRIT = "sa"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    RUSSIAN = "ru"


class ProviderStatus(str, Enum):
    """Provider execution status"""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


class ProviderResult(BaseModel):
    """Result from a single provider"""
    provider_name: str
    detected_language: Optional[str] = None
    time_taken: float
    estimated_cost: dict  # {"tokens": int, "dollars": float}
    status: ProviderStatus
    error_message: Optional[str] = None


class LanguageDetectionRequest(BaseModel):
    """Request for language detection"""
    audio_file_path: str
    ground_truth_language: Optional[str] = None


class LanguageDetectionResponse(BaseModel):
    """Response with results from all providers"""
    results: List[ProviderResult]
    total_time: float
    successful_providers: int
    failed_providers: int
