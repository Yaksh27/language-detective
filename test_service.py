#!/usr/bin/env python3
"""
Simple test script for the Language Detective Service
"""

import asyncio
import os
import tempfile
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from coordinator import LanguageDetectionCoordinator


async def test_coordinator():
    """Test the coordinator with mock audio files"""
    print("🧪 Testing Language Detective Service...")
    
    # Create coordinator
    coordinator = LanguageDetectionCoordinator()
    
    # Test available providers
    providers = coordinator.get_available_providers()
    print(f"✅ Available providers: {providers}")
    
    # Create a temporary test audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(b"mock audio data")
        temp_file_path = temp_file.name
    
    try:
        print(f"📁 Testing with temporary file: {temp_file_path}")
        
        # Test language detection with all providers
        print("🔄 Running language detection with all providers...")
        result = await coordinator.detect_language_all_providers(temp_file_path)
        
        print(f"✅ Detection completed in {result.total_time:.3f} seconds")
        print(f"📊 Results: {result.successful_providers} successful, {result.failed_providers} failed")
        
        # Print individual results
        for provider_result in result.results:
            status_emoji = "✅" if provider_result.status == "success" else "❌"
            print(f"{status_emoji} {provider_result.provider_name}:")
            print(f"   Language: {provider_result.detected_language or 'N/A'}")
            print(f"   Time: {provider_result.time_taken:.3f}s")
            print(f"   Cost: ${provider_result.estimated_cost['dollars']:.6f}")
            print(f"   Status: {provider_result.status}")
            if provider_result.error_message:
                print(f"   Error: {provider_result.error_message}")
            print()
        
        # Test single provider
        print("🔄 Testing single provider (OpenAI (Mock))...")
        single_result = await coordinator.detect_language_single_provider(
            temp_file_path, "OpenAI (Mock)"
        )
        print(f"✅ Single provider result: {single_result.detected_language}")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)
        print("🧹 Cleaned up temporary files")
    
    print("🎉 Test completed successfully!")


if __name__ == "__main__":
    # Check if environment variables are set
    required_vars = ["GEMINI_API_KEY", "SARVAM_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {missing_vars}")
        print("   Some providers may not work correctly.")
        print("   Please set the required API keys in your .env file.")
        print()
    
    # Run the test
    asyncio.run(test_coordinator())
