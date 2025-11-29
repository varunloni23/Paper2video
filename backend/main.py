"""
Paper2Video Backend API
FastAPI application for converting research papers to video presentations
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import init_db
from app.routes.jobs import router as jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting Paper2Video API...")
    await init_db()
    print("Database initialized")
    
    # Create directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    print(f"Upload directory: {settings.upload_dir}")
    print(f"Output directory: {settings.output_dir}")
    
    yield
    
    # Shutdown
    print("Shutting down Paper2Video API...")


# Create FastAPI application
app = FastAPI(
    title="Paper2Video API",
    description="Convert research papers to video presentations with AI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving generated content
if os.path.exists(settings.output_dir):
    app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")


# Health check endpoint for Render
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Include routers
app.include_router(jobs_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Paper2Video API",
        "version": "1.0.0",
        "description": "Convert research papers to video presentations",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /api/upload",
            "start_job": "POST /api/jobs/{job_id}/start",
            "job_status": "GET /api/jobs/{job_id}",
            "list_jobs": "GET /api/jobs",
            "download_video": "GET /api/jobs/{job_id}/video",
            "get_slide": "GET /api/jobs/{job_id}/slides/{slide_number}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
