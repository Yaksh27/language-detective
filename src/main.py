import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

from .models import LanguageDetectionRequest, LanguageDetectionResponse
from .coordinator import LanguageDetectionCoordinator

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Language Detective Service",
    description="A service that detects spoken language in audio files using multiple AI providers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize coordinator
coordinator = LanguageDetectionCoordinator()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Language Detective Service",
        "version": "1.0.0",
        "endpoints": {
            "detect_language": "/detect/language",
            "providers": "/providers",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Language Detective Service"}


@app.get("/providers")
async def get_providers():
    """Get list of available providers"""
    try:
        providers = coordinator.get_available_providers()
        return {"providers": providers, "count": len(providers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting providers: {str(e)}")


@app.post("/detect/language", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    """
    Detect language in audio file using all available providers
    
    - **audio_file_path**: Path to the audio file to analyze
    - **ground_truth_language**: Optional ground truth language for context (not used in detection)
    """
    try:
        # Validate file path
        if not os.path.exists(request.audio_file_path):
            raise HTTPException(
                status_code=400, 
                detail=f"Audio file not found: {request.audio_file_path}"
            )
        
        # Check if file is an audio file (basic validation)
        audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac']
        file_ext = os.path.splitext(request.audio_file_path)[1].lower()
        
        if file_ext not in audio_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}. Supported formats: {', '.join(audio_extensions)}"
            )
        
        # Execute language detection with all providers
        result = await coordinator.detect_language_all_providers(request.audio_file_path)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/detect/language/{provider_name}")
async def detect_language_single_provider(provider_name: str, request: LanguageDetectionRequest):
    """
    Detect language using a specific provider
    
    - **provider_name**: Name of the provider to use
    - **audio_file_path**: Path to the audio file to analyze
    """
    try:
        # Validate file path
        if not os.path.exists(request.audio_file_path):
            raise HTTPException(
                status_code=400, 
                detail=f"Audio file not found: {request.audio_file_path}"
            )
        
        # Execute language detection with specific provider
        result = await coordinator.detect_language_single_provider(
            request.audio_file_path, 
            provider_name
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
