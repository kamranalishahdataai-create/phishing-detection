#!/usr/bin/env python3
"""
Phishing Detection Backend - Run Script
Start the FastAPI server with uvicorn
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from config.settings import settings


def main():
    """Run the FastAPI server"""
    print("=" * 60)
    print(f"🛡️  {settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Host: {settings.HOST}")
    print(f"Port: {settings.PORT}")
    print(f"Debug: {settings.DEBUG}")
    print("=" * 60)
    
    # Use single worker on Windows to avoid socket issues
    workers = 1 if os.name == 'nt' or settings.DEBUG else settings.WORKERS
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=workers,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
