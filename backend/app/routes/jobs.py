"""
API routes for job management and file upload
"""

import os
import uuid
import shutil
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import Job, JobStatus, StylePreset, AvatarOption
from app.config import settings
from app.services.job_processor import process_job_async

router = APIRouter(prefix="/api", tags=["jobs"])


def get_file_type(filename: str) -> str:
    """Determine file type from filename"""
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    
    type_map = {
        'pdf': 'pdf',
        'docx': 'docx',
        'doc': 'docx',
        'pptx': 'pptx',
        'ppt': 'pptx',
        'zip': 'latex',
        'tex': 'latex'
    }
    
    return type_map.get(ext, 'unknown')


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    style_preset: str = Form("concise"),
    avatar_option: str = Form("svg"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a research paper and create a new job
    
    - **file**: The document file (PDF, DOCX, PPTX, or ZIP for LaTeX)
    - **style_preset**: 'concise' or 'detailed'
    - **avatar_option**: 'none', 'svg', or 'realistic'
    """
    # Validate file type
    file_type = get_file_type(file.filename)
    if file_type == 'unknown':
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload PDF, DOCX, PPTX, or ZIP (LaTeX)"
        )
    
    # Validate style preset
    try:
        style = StylePreset(style_preset)
    except ValueError:
        style = StylePreset.CONCISE
    
    # Validate avatar option
    try:
        avatar = AvatarOption(avatar_option)
    except ValueError:
        avatar = AvatarOption.SVG
    
    # Generate job ID and save file
    job_id = uuid.uuid4()
    upload_dir = os.path.join(settings.upload_dir, str(job_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save uploaded file
    file_path = os.path.join(upload_dir, file.filename)
    try:
        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create job record
    job = Job(
        id=job_id,
        original_filename=file.filename,
        file_type=file_type,
        file_path=file_path,
        style_preset=style,
        avatar_option=avatar,
        status=JobStatus.PENDING,
        progress=0,
        status_message="Job created, waiting to start..."
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    return {
        "job_id": str(job_id),
        "status": "pending",
        "message": "File uploaded successfully. Start processing with POST /api/jobs/{job_id}/start"
    }


@router.post("/jobs/{job_id}/start")
async def start_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Start processing a job"""
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    # Get job
    result = await db.execute(select(Job).where(Job.id == job_uuid))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.PENDING:
        raise HTTPException(
            status_code=400, 
            detail=f"Job is already {job.status.value}. Cannot start."
        )
    
    # Start background processing
    background_tasks.add_task(run_job_processing, str(job_id))
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": "Job processing started. Check status at GET /api/jobs/{job_id}"
    }


async def run_job_processing(job_id: str):
    """Background task to run job processing"""
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            await process_job_async(job_id, db)
        except Exception as e:
            print(f"Error processing job {job_id}: {e}")
            # Update job status to failed
            from sqlalchemy import update
            stmt = update(Job).where(Job.id == uuid.UUID(job_id)).values(
                status=JobStatus.FAILED,
                error_message=str(e)
            )
            await db.execute(stmt)
            await db.commit()


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get job status and details"""
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    result = await db.execute(select(Job).where(Job.id == job_uuid))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job.to_dict()


@router.get("/jobs")
async def list_jobs(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all jobs with optional status filter"""
    query = select(Job).order_by(desc(Job.created_at))
    
    if status:
        try:
            status_enum = JobStatus(status)
            query = query.where(Job.status == status_enum)
        except ValueError:
            pass
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return {
        "jobs": [job.to_dict() for job in jobs],
        "count": len(jobs),
        "offset": offset,
        "limit": limit
    }


@router.get("/jobs/{job_id}/video")
async def download_video(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Download the generated video"""
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    result = await db.execute(select(Job).where(Job.id == job_uuid))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"Video not ready. Job status: {job.status.value}"
        )
    
    if not job.video_path or not os.path.exists(job.video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        job.video_path,
        media_type="video/mp4",
        filename=f"{job.original_filename.rsplit('.', 1)[0]}_presentation.mp4"
    )


@router.get("/jobs/{job_id}/slides/{slide_number}")
async def get_slide_image(
    job_id: str,
    slide_number: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific slide image"""
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    result = await db.execute(select(Job).where(Job.id == job_uuid))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.slide_images:
        raise HTTPException(status_code=404, detail="Slides not generated yet")
    
    if slide_number < 1 or slide_number > len(job.slide_images):
        raise HTTPException(status_code=404, detail="Slide not found")
    
    slide_path = job.slide_images[slide_number - 1]
    
    if not os.path.exists(slide_path):
        raise HTTPException(status_code=404, detail="Slide image file not found")
    
    return FileResponse(slide_path, media_type="image/png")


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a job and its files"""
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    result = await db.execute(select(Job).where(Job.id == job_uuid))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete files
    upload_dir = os.path.join(settings.upload_dir, job_id)
    output_dir = os.path.join(settings.output_dir, job_id)
    
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir, ignore_errors=True)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)
    
    # Delete database record
    await db.delete(job)
    await db.commit()
    
    return {"message": "Job deleted successfully"}


@router.post("/jobs/{job_id}/retry")
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed job"""
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID")
    
    result = await db.execute(select(Job).where(Job.id == job_uuid))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Allow retry for failed jobs OR stuck jobs (not pending or completed)
    if job.status not in [JobStatus.FAILED, JobStatus.PARSING, JobStatus.GENERATING_SCRIPT, 
                          JobStatus.GENERATING_SLIDES, JobStatus.GENERATING_AUDIO, 
                          JobStatus.COMPOSING_VIDEO]:
        if job.status == JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Job already completed")
        if job.status == JobStatus.PENDING:
            raise HTTPException(status_code=400, detail="Job is already pending")
    
    # Reset job status
    job.status = JobStatus.PENDING
    job.progress = 0
    job.error_message = None
    job.status_message = "Job reset, retrying..."
    await db.commit()
    
    # Start background processing
    background_tasks.add_task(run_job_processing, str(job_id))
    
    return {
        "job_id": job_id,
        "status": "retrying",
        "message": "Job retry started"
    }
