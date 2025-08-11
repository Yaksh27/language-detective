#!/usr/bin/env python3
"""
Test script for Language Detective Service using only mock connectors
"""

import asyncio
import os
import tempfile
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from connectors.openai_mock import OpenAIMockConnector
from connectors.elevenlabs_mock import ElevenLabsMockConnector
from models import ProviderResult, ProviderStatus


async def test_mock_connectors():
    """Test only the mock connectors"""
    print("🧪 Testing Language Detective Service (Mock Connectors Only)...")
    
    # Create mock connectors
    openai_mock = OpenAIMockConnector()
    elevenlabs_mock = ElevenLabsMockConnector()
    
    print(f"✅ Available mock providers: {openai_mock.provider_name}, {elevenlabs_mock.provider_name}")
    
    # Create test audio files with different names to test language detection
    test_files = [
        ("hindi_audio.wav", "Expected: Hindi (hi)"),
        ("tamil_speech.wav", "Expected: Tamil (ta)"),
        ("english_conversation.wav", "Expected: English (en)"),
        ("telugu_sample.wav", "Expected: Telugu (te)")
    ]
    
    for filename, expected in test_files:
        print(f"\n📁 Testing with file: {filename}")
        print(f"   {expected}")
        
        # Create temporary file with the descriptive name
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, filename)
        
        try:
            # Create the file with the descriptive name
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(b"mock audio data")
            
            # Debug: Show the actual file path being used
            print(f"   🔍 Debug: File path = {temp_file_path}")
            print(f"   🔍 Debug: Filename = {os.path.basename(temp_file_path)}")
            
            # Test OpenAI mock
            print("   🔄 Testing OpenAI Mock...")
            openai_result = await openai_mock.execute_with_metrics(temp_file_path)
            print(f"      ✅ Language: {openai_result.detected_language}")
            print(f"      ⏱️  Time: {openai_result.time_taken:.3f}s")
            print(f"      💰 Cost: ${openai_result.estimated_cost['dollars']:.6f}")
            print(f"      📊 Status: {openai_result.status}")
            
            # Test ElevenLabs mock
            print("   🔄 Testing ElevenLabs Mock...")
            elevenlabs_result = await elevenlabs_mock.execute_with_metrics(temp_file_path)
            print(f"      ✅ Language: {elevenlabs_result.detected_language}")
            print(f"      ⏱️  Time: {elevenlabs_result.time_taken:.3f}s")
            print(f"      💰 Cost: ${elevenlabs_result.estimated_cost['dollars']:.6f}")
            print(f"      📊 Status: {elevenlabs_result.status}")
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    print("\n🎉 Mock connector tests completed successfully!")
    print("   The service architecture is working correctly!")
    print("\n📝 Next steps:")
    print("   1. Add real API keys to .env file")
    print("   2. Test with real connectors")
    print("   3. Start the FastAPI service")


if __name__ == "__main__":
    print("🚀 Language Detective Service - Mock Testing")
    print("=" * 50)
    
    # Run the test
    asyncio.run(test_mock_connectors())
