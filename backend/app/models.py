from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database import Base

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PARSING = "parsing"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_SLIDES = "generating_slides"
    GENERATING_AUDIO = "generating_audio"
    COMPOSING_VIDEO = "composing_video"
    COMPLETED = "completed"
    FAILED = "failed"

class StylePreset(str, enum.Enum):
    CONCISE = "concise"
    DETAILED = "detailed"

class AvatarOption(str, enum.Enum):
    NONE = "none"
    SVG = "svg"
    REALISTIC = "realistic"

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # File info
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, latex, pptx
    file_path = Column(String(500), nullable=False)
    
    # User preferences
    style_preset = Column(SQLEnum(StylePreset), default=StylePreset.CONCISE)
    avatar_option = Column(SQLEnum(AvatarOption), default=AvatarOption.SVG)
    
    # Job status
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    status_message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Extracted content
    extracted_text = Column(Text, nullable=True)
    extracted_sections = Column(JSON, nullable=True)  # List of sections with titles
    extracted_figures = Column(JSON, nullable=True)  # List of figure paths
    
    # Generated content
    slide_script = Column(JSON, nullable=True)  # List of slide objects
    slide_images = Column(JSON, nullable=True)  # List of slide image paths
    audio_path = Column(String(500), nullable=True)
    
    # Final output
    video_path = Column(String(500), nullable=True)
    video_duration = Column(Integer, nullable=True)  # seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "style_preset": self.style_preset.value if self.style_preset else None,
            "avatar_option": self.avatar_option.value if self.avatar_option else None,
            "status": self.status.value if self.status else None,
            "progress": self.progress,
            "status_message": self.status_message,
            "error_message": self.error_message,
            "slide_script": self.slide_script,
            "slide_images": self.slide_images,
            "video_path": self.video_path,
            "video_duration": self.video_duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
