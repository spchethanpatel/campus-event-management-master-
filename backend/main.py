"""
Main FastAPI application for Event Management System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
from routers import (
    colleges, admins, students, events, event_types, 
    registrations, attendance, feedback
)

# Note: Using existing database, so we don't create tables
# Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Event Management System with SQLite database",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(colleges.router, prefix="/api/v1", tags=["colleges"])
app.include_router(admins.router, prefix="/api/v1", tags=["admins"])
app.include_router(students.router, prefix="/api/v1", tags=["students"])
app.include_router(events.router, prefix="/api/v1", tags=["events"])
app.include_router(event_types.router, prefix="/api/v1", tags=["event-types"])
app.include_router(registrations.router, prefix="/api/v1", tags=["registrations"])
app.include_router(attendance.router, prefix="/api/v1", tags=["attendance"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with system information."""
    return {
        "message": "Welcome to Event Management System",
        "version": settings.VERSION,
        "database_path": settings.database_path,
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_STR
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database_connected": True,
        "database_path": settings.database_path,
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True  # Enable auto-reload in development
    )
