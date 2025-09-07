#!/usr/bin/env python3
"""
FastAPI Backend Startup Script.
Run this script to start the Event Management System development server.
"""
import uvicorn

from config import settings


def main():
    """Start the FastAPI development server."""
    print("🚀 Starting Event Management System...")
    print(f"📁 Database path: {settings.database_path}")
    print(f"📖 API Documentation: http://localhost:8000/docs")
    print(f"🔍 Health check: http://localhost:8000/health")
    print(f"📊 ReDoc: http://localhost:8000/redoc")
    print("-" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()
