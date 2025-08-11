#!/usr/bin/env python3
"""
Startup script for the Language Detective Service
"""

import uvicorn
from src.main import app

if __name__ == "__main__":
    print("🚀 Starting Language Detective Service...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🌐 Service URL: http://localhost:8000")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
