"""
Pydantic schemas for request/response models
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== Camera Schemas ====================

class CameraStatusResponse(BaseModel):
    is_running: bool
    is_available: bool

# ==================== Activity Guide Schemas ====================

class TaskRequest(BaseModel):
    goal: str
    target_objects: Optional[List[str]] = None

class TaskResponse(BaseModel):
    status: str
    message: str
    target_objects: List[str]
    primary_target: str
    stage: str

class GuidanceResponse(BaseModel):
    instruction: str
    stage: str
    detected_objects: List[Dict[str, Any]]
    hand_detected: bool
    object_location: Optional[Dict[str, float]] = None
    hand_location: Optional[Dict[str, float]] = None

class FeedbackRequest(BaseModel):
    confirmed: bool
    feedback_text: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    message: str
    next_stage: str

# ==================== Scene Description Schemas ====================

class SceneDescriptionRequest(BaseModel):
    start_recording: bool = True

class SceneDescriptionResponse(BaseModel):
    description: str
    summary: Optional[str] = None
    safety_alert: bool = False
    timestamp: datetime

class RecordingLog(BaseModel):
    log_id: str
    session_start: datetime
    session_end: Optional[datetime] = None
    events: List[Dict[str, Any]]
    filename: str

# ==================== TTS Schemas ====================

class TTSRequest(BaseModel):
    text: str
    lang: str = "en"

class TTSResponse(BaseModel):
    audio_base64: str
    duration: float

# ==================== General Schemas ====================

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None

