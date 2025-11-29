"""
Job processor - handles the complete pipeline for video generation
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import Job, JobStatus
from app.config import settings
from app.services.document_parser import parse_document
from app.services.slide_generator import generate_slides
from app.services.tts_generator import generate_audio_for_slides, generate_single_audio
from app.services.slide_image_generator import generate_slide_images
from app.services.video_composer import VideoComposer
from app.services.avatar_generator import generate_static_avatar_svg


class JobProcessor:
    """Process video generation jobs"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: int = None,
        message: str = None,
        error: str = None,
        **kwargs
    ):
        """Update job status in database"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if progress is not None:
            update_data["progress"] = progress
        if message:
            update_data["status_message"] = message
        if error:
            update_data["error_message"] = error
        
        update_data.update(kwargs)
        
        stmt = update(Job).where(Job.id == job_id).values(**update_data)
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()
    
    async def process_job(self, job_id: str) -> Dict:
        """
        Process a video generation job through the complete pipeline
        
        Pipeline steps:
        1. Parse document
        2. Generate slide script with LLM
        3. Generate slide images
        4. Generate TTS audio
        5. Compose video
        6. Add avatar overlay (if selected)
        """
        job = await self.get_job(job_id)
        if not job:
            return {"success": False, "error": "Job not found"}
        
        # Create job output directory
        job_dir = os.path.join(settings.output_dir, str(job_id))
        os.makedirs(job_dir, exist_ok=True)
        
        try:
            # Step 1: Parse document
            await self.update_job_status(
                job_id, 
                JobStatus.PARSING, 
                progress=5,
                message="Parsing document..."
            )
            
            parsed_content = await self._parse_document(job)
            
            if "error" in parsed_content and parsed_content["error"]:
                raise Exception(f"Failed to parse document: {parsed_content['error']}")
            
            await self.update_job_status(
                job_id,
                JobStatus.PARSING,
                progress=15,
                message="Document parsed successfully",
                extracted_text=parsed_content.get("text", "")[:50000],  # Limit stored text
                extracted_sections=parsed_content.get("sections", []),
                extracted_figures=parsed_content.get("figures", [])
            )
            
            # Step 2: Generate slide script
            await self.update_job_status(
                job_id,
                JobStatus.GENERATING_SCRIPT,
                progress=20,
                message="Generating presentation script with AI..."
            )
            
            slides = await self._generate_slides(job, parsed_content)
            
            await self.update_job_status(
                job_id,
                JobStatus.GENERATING_SCRIPT,
                progress=35,
                message=f"Generated {len(slides)} slides",
                slide_script=slides
            )
            
            # Step 3: Generate slide images
            await self.update_job_status(
                job_id,
                JobStatus.GENERATING_SLIDES,
                progress=40,
                message="Creating slide images..."
            )
            
            slides_dir = os.path.join(job_dir, "slides")
            slide_images = generate_slide_images(slides, slides_dir)
            
            await self.update_job_status(
                job_id,
                JobStatus.GENERATING_SLIDES,
                progress=55,
                message=f"Created {len(slide_images)} slide images",
                slide_images=slide_images
            )
            
            # Step 4: Generate TTS audio
            await self.update_job_status(
                job_id,
                JobStatus.GENERATING_AUDIO,
                progress=60,
                message="Generating voiceover..."
            )
            
            audio_dir = os.path.join(job_dir, "audio")
            audio_result = await generate_audio_for_slides(slides, audio_dir)
            
            if not audio_result["success"]:
                raise Exception(f"Failed to generate audio: {audio_result.get('error', 'Unknown error')}")
            
            # Check if we have any audio files
            if not audio_result.get("audio_files"):
                # Generate a simple intro audio if no slides had narration
                print("No slide audio generated, creating placeholder audio")
                intro_path = os.path.join(audio_dir, "intro.mp3")
                intro_result = await generate_single_audio(
                    f"Welcome to this presentation about {job.original_filename.rsplit('.', 1)[0]}.",
                    intro_path
                )
                if intro_result["success"]:
                    audio_result["audio_files"] = [{
                        "slide_number": 1,
                        "path": intro_path,
                        "duration": intro_result["estimated_duration"],
                        "word_count": intro_result["word_count"]
                    }]
            
            await self.update_job_status(
                job_id,
                JobStatus.GENERATING_AUDIO,
                progress=75,
                message="Voiceover generated"
            )
            
            # Step 5: Compose video
            await self.update_job_status(
                job_id,
                JobStatus.COMPOSING_VIDEO,
                progress=80,
                message="Composing video..."
            )
            
            video_path = os.path.join(job_dir, "presentation.mp4")
            video_result = await self._compose_video(
                slide_images,
                audio_result["audio_files"],
                video_path
            )
            
            if not video_result["success"]:
                raise Exception(f"Failed to compose video: {video_result.get('error')}")
            
            # Step 6: Add avatar overlay if selected
            final_video_path = video_path
            if job.avatar_option and job.avatar_option.value != "none":
                await self.update_job_status(
                    job_id,
                    JobStatus.COMPOSING_VIDEO,
                    progress=90,
                    message="Adding avatar overlay..."
                )
                
                avatar_video_path = await self._add_avatar(
                    video_path,
                    job_dir,
                    video_result.get("duration", 60),
                    job.avatar_option.value
                )
                
                if avatar_video_path:
                    final_video_path = avatar_video_path
            
            # Complete!
            await self.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                progress=100,
                message="Video generation complete!",
                video_path=final_video_path,
                video_duration=int(video_result.get("duration", 0)),
                completed_at=datetime.utcnow()
            )
            
            return {
                "success": True,
                "video_path": final_video_path,
                "duration": video_result.get("duration"),
                "slide_count": len(slides)
            }
            
        except Exception as e:
            await self.update_job_status(
                job_id,
                JobStatus.FAILED,
                progress=0,
                message="Job failed",
                error=str(e)
            )
            return {"success": False, "error": str(e)}
    
    async def _parse_document(self, job: Job) -> Dict:
        """Parse uploaded document"""
        output_dir = os.path.join(settings.output_dir, str(job.id), "parsed")
        os.makedirs(output_dir, exist_ok=True)
        
        # Ensure file_path is absolute
        file_path = job.file_path
        if not os.path.isabs(file_path):
            # Try relative to backend dir
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file_path = os.path.join(backend_dir, file_path)
        
        return parse_document(file_path, job.file_type, output_dir)
    
    async def _generate_slides(self, job: Job, parsed_content: Dict) -> list:
        """Generate slide script from parsed content"""
        title = job.original_filename.rsplit('.', 1)[0]  # Remove extension
        style = job.style_preset.value if job.style_preset else "concise"
        
        return await generate_slides(
            text=parsed_content.get("text", ""),
            sections=parsed_content.get("sections", []),
            style=style,
            title=title
        )
    
    async def _compose_video(
        self,
        slide_images: list,
        audio_files: list,
        output_path: str
    ) -> Dict:
        """Compose final video"""
        try:
            composer = VideoComposer()
            return composer.create_slideshow_video(
                slide_images,
                audio_files,
                output_path
            )
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _add_avatar(
        self,
        video_path: str,
        job_dir: str,
        duration: float,
        avatar_type: str
    ) -> Optional[str]:
        """Add avatar overlay to video"""
        try:
            from app.services.avatar_generator import SVGAvatarGenerator
            
            # Generate avatar video
            avatar_video_path = os.path.join(job_dir, "avatar.mp4")
            
            style = "professional_female"  # Default
            generator = SVGAvatarGenerator(style=style)
            result = generator.generate_avatar_video(avatar_video_path, duration)
            
            if not result.get("success"):
                print(f"Failed to generate avatar: {result.get('error')}")
                return None
            
            # Overlay avatar on video
            composer = VideoComposer()
            final_path = os.path.join(job_dir, "presentation_with_avatar.mp4")
            
            overlay_result = composer.add_avatar_overlay(
                video_path,
                avatar_video_path,
                final_path,
                position="bottom-right",
                scale=0.2
            )
            
            if overlay_result.get("success"):
                return final_path
            return None
            
        except Exception as e:
            print(f"Error adding avatar: {e}")
            return None


async def process_job_async(job_id: str, db: AsyncSession) -> Dict:
    """Main entry point for processing a job"""
    processor = JobProcessor(db)
    return await processor.process_job(job_id)
