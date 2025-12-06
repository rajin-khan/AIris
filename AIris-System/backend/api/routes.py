"""
API Routes for AIris Backend
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import base64
import cv2
import numpy as np
import time
import asyncio
from io import BytesIO

from services.camera_service import CameraService
from services.model_service import ModelService
from services.activity_guide_service import ActivityGuideService
from services.scene_description_service import SceneDescriptionService
from services.tts_service import TTSService
from services.stt_service import STTService
from models.schemas import (
    TaskRequest, TaskResponse, GuidanceResponse, 
    SceneDescriptionRequest, SceneDescriptionResponse,
    FeedbackRequest, CameraStatusResponse
)

router = APIRouter(prefix="/api/v1", tags=["airis"])

# Services will be initialized in main.py and passed here
_camera_service: CameraService = None
_model_service: ModelService = None
_activity_guide_service: ActivityGuideService = None
_scene_description_service: SceneDescriptionService = None
_tts_service: TTSService = None
_stt_service: STTService = None

def set_global_services(camera: CameraService, model: ModelService):
    """Set global services from main.py"""
    global _camera_service, _model_service, _scene_description_service, _activity_guide_service
    _camera_service = camera
    _model_service = model
    
    # Eagerly initialize services that need Groq so we see any errors at startup
    print("\n📦 Initializing AI services...")
    _scene_description_service = SceneDescriptionService(_model_service)
    _activity_guide_service = ActivityGuideService(_model_service)
    print("📦 AI services initialized.\n")

def get_camera_service() -> CameraService:
    global _camera_service
    if _camera_service is None:
        _camera_service = CameraService()
    return _camera_service

def get_model_service() -> ModelService:
    global _model_service
    if _model_service is None:
        raise RuntimeError("Model service not initialized. This should be set during app startup.")
    return _model_service

def get_activity_guide_service() -> ActivityGuideService:
    global _activity_guide_service, _model_service
    if _activity_guide_service is None:
        if _model_service is None:
            raise RuntimeError("Model service not initialized. This should be set during app startup.")
        _activity_guide_service = ActivityGuideService(_model_service)
    return _activity_guide_service

def get_scene_description_service() -> SceneDescriptionService:
    global _scene_description_service, _model_service
    if _scene_description_service is None:
        if _model_service is None:
            raise RuntimeError("Model service not initialized. This should be set during app startup.")
        _scene_description_service = SceneDescriptionService(_model_service)
    return _scene_description_service

def get_tts_service() -> TTSService:
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service

def get_stt_service() -> STTService:
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service

# ==================== Camera Endpoints ====================
class CameraConfigRequest(BaseModel):
    source_type: str  # "webcam" or "esp32"
    ip_address: Optional[str] = None

class ESP32WiFiProvisionRequest(BaseModel):
    ssid: str
    password: str = ""

@router.post("/camera/config")
async def set_camera_config(config: CameraConfigRequest):
    """Set camera configuration"""
    camera_service = get_camera_service()
    await camera_service.set_config(config.source_type, config.ip_address)
    return {"status": "success", "message": "Camera configuration updated"}

@router.post("/camera/esp32/provision-wifi")
async def provision_esp32_wifi(request: ESP32WiFiProvisionRequest):
    """Provision WiFi credentials to ESP32-CAM in setup mode"""
    import aiohttp
    import asyncio
    
    if not request.ssid:
        raise HTTPException(status_code=400, detail="SSID is required")
    
    # ESP32 in AP mode is always at 192.168.4.1
    setup_url = f"http://192.168.4.1/set-wifi?ssid={request.ssid}&pass={request.password}"
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get(setup_url) as response:
                if response.status == 200:
                    return {
                        "status": "success",
                        "success": True,
                        "message": "Credentials received! The camera is restarting. Please reconnect your PC to your Home WiFi now."
                    }
                else:
                    error_text = await response.text()
                    return {
                        "status": "error",
                        "success": False,
                        "message": f"Error: {error_text}"
                    }
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Connection timeout. Are you connected to ESP32-CAM-SETUP network?"
        )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection failed: {str(e)}. Are you connected to ESP32-CAM-SETUP network?"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/camera/start")
async def start_camera():
    """Start the camera feed"""
    try:
        camera_service = get_camera_service()
        success = await camera_service.start()
        if success:
            return {"status": "success", "message": "Camera started"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start camera")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/camera/stop")
async def stop_camera():
    """Stop the camera feed"""
    try:
        camera_service = get_camera_service()
        await camera_service.stop()
        return {"status": "success", "message": "Camera stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/camera/status")
async def get_camera_status():
    """Get camera status"""
    camera_service = get_camera_service()
    return {
        "is_running": camera_service.is_running(),
        "is_available": camera_service.is_available()
    }

@router.get("/camera/frame")
async def get_camera_frame():
    """Get a single frame from the camera"""
    camera_service = get_camera_service()
    frame = await camera_service.get_frame()
    if frame is None:
        raise HTTPException(status_code=404, detail="No frame available")
    
    # Encode frame as JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()
    
    return StreamingResponse(
        BytesIO(frame_bytes),
        media_type="image/jpeg"
    )

@router.websocket("/camera/stream")
async def camera_stream(websocket: WebSocket):
    """WebSocket endpoint for streaming camera frames with optimized frame rate"""
    await websocket.accept()
    camera_service = get_camera_service()
    
    # Adaptive frame rate based on source type
    frame_interval = 0.033  # Default ~30 FPS for webcam (1/30 seconds)
    if camera_service.source_type == "esp32":
        frame_interval = 0.05  # ~20 FPS for ESP32 (more stable, reduces network load)
    
    last_frame_sent_time = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Frame rate control: Ensure minimum time between frames
            # This prevents encoding/sending frames too quickly, saving CPU and bandwidth
            time_since_last_frame = current_time - last_frame_sent_time
            if time_since_last_frame < frame_interval:
                # Calculate exact sleep time needed to maintain target frame rate
                sleep_time = frame_interval - time_since_last_frame
                await asyncio.sleep(sleep_time)
                # After sleeping, update current time and proceed
                current_time = time.time()
            
            # Get frame from camera service
            frame = await camera_service.get_frame()
            if frame is None:
                await websocket.send_json({"error": "No frame available"})
                await asyncio.sleep(0.1)  # Wait a bit before retrying
                continue
            
            # Encode frame as JPEG with quality based on source
            # Lower quality for ESP32 = smaller file size = faster transmission = smoother playback
            jpeg_quality = 90 if camera_service.source_type == "webcam" else 75
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
            frame_bytes = buffer.tobytes()
            frame_base64 = base64.b64encode(frame_bytes).decode()
            
            # Send frame to client
            await websocket.send_json({
                "type": "frame",
                "data": frame_base64,
                "timestamp": camera_service.get_timestamp()
            })
            
            # Update timestamp after successful send
            last_frame_sent_time = time.time()
            
            # Small yield to allow other async tasks to run
            await asyncio.sleep(0.001)
    except WebSocketDisconnect:
        print("Client disconnected from camera stream")
    except Exception as e:
        print(f"Error in camera stream: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.close()
        except:
            pass

# ==================== Activity Guide Endpoints ====================

@router.post("/activity-guide/start-task", response_model=TaskResponse)
async def start_task(request: TaskRequest):
    """Start a new activity guide task"""
    try:
        activity_guide_service = get_activity_guide_service()
        result = await activity_guide_service.start_task(
            goal=request.goal,
            target_objects=request.target_objects
        )
        return TaskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activity-guide/process-frame")
async def process_activity_frame():
    """Process a frame for activity guide mode"""
    camera_service = get_camera_service()
    activity_guide_service = get_activity_guide_service()
    frame = await camera_service.get_frame()
    if frame is None:
        raise HTTPException(status_code=404, detail="No frame available")
    
    result = await activity_guide_service.process_frame(frame)
    
    # Encode processed frame (always process, even when idle, to show YOLO boxes)
    processed_frame = result.get("annotated_frame", frame)
    _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    frame_bytes = buffer.tobytes()
    frame_base64 = base64.b64encode(frame_bytes).decode()
    
    return {
        "frame": frame_base64,
        "guidance": result.get("guidance"),
        "stage": result.get("stage"),
        "instruction": result.get("instruction"),
        "detected_objects": result.get("detected_objects", []),
        "hand_detected": result.get("hand_detected", False)
    }

@router.post("/activity-guide/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for activity guide"""
    try:
        activity_guide_service = get_activity_guide_service()
        result = await activity_guide_service.handle_feedback(
            confirmed=request.confirmed,
            feedback_text=request.feedback_text
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity-guide/status")
async def get_activity_guide_status():
    """Get current activity guide status"""
    activity_guide_service = get_activity_guide_service()
    return activity_guide_service.get_status()

@router.post("/activity-guide/reset")
async def reset_activity_guide():
    """Reset the activity guide state"""
    activity_guide_service = get_activity_guide_service()
    activity_guide_service.reset()
    return {"status": "success", "message": "Activity guide reset"}

# ==================== Scene Description Endpoints ====================

@router.post("/scene-description/start-recording")
async def start_recording():
    """Start scene description recording"""
    try:
        scene_description_service = get_scene_description_service()
        result = await scene_description_service.start_recording()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scene-description/stop-recording")
async def stop_recording():
    """Stop scene description recording and save log"""
    try:
        scene_description_service = get_scene_description_service()
        result = await scene_description_service.stop_recording()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scene-description/process-frame")
async def process_scene_frame():
    """Process a frame for scene description mode"""
    camera_service = get_camera_service()
    scene_description_service = get_scene_description_service()
    frame = await camera_service.get_frame()
    if frame is None:
        raise HTTPException(status_code=404, detail="No frame available")
    
    result = await scene_description_service.process_frame(frame)
    
    # Encode processed frame
    processed_frame = result.get("annotated_frame", frame)
    _, buffer = cv2.imencode('.jpg', processed_frame)
    frame_bytes = buffer.tobytes()
    frame_base64 = base64.b64encode(frame_bytes).decode()
    
    return {
        "frame": frame_base64,
        "description": result.get("description"),
        "summary": result.get("summary"),
        "safety_alert": result.get("safety_alert", False),
        "is_recording": result.get("is_recording", False)
    }

@router.get("/scene-description/logs")
async def get_recording_logs():
    """Get all recording logs"""
    scene_description_service = get_scene_description_service()
    logs = scene_description_service.get_logs()
    return {"logs": logs}

@router.get("/scene-description/log/{log_id}")
async def get_recording_log(log_id: str):
    """Get a specific recording log"""
    scene_description_service = get_scene_description_service()
    log = scene_description_service.get_log(log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

# ==================== Text-to-Speech Endpoints ====================

@router.post("/tts/generate")
async def generate_speech(text: str):
    """Generate speech from text"""
    try:
        tts_service = get_tts_service()
        audio_data = await tts_service.generate(text)
        if audio_data:
            return JSONResponse({
                "audio_base64": base64.b64encode(audio_data).decode(),
                "duration": tts_service.estimate_duration(text)
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to generate speech")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tts/stream/{text}")
async def stream_speech(text: str):
    """Stream speech audio"""
    try:
        tts_service = get_tts_service()
        audio_data = await tts_service.generate(text)
        if audio_data:
            return StreamingResponse(
                BytesIO(audio_data),
                media_type="audio/mpeg"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate speech")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Speech-to-Text Endpoints ====================

@router.post("/stt/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), sample_rate: int = 16000):
    """Transcribe audio to text using free offline Whisper model"""
    try:
        stt_service = get_stt_service()
        
        # Read audio file
        audio_data = await audio.read()
        
        # Transcribe
        transcription = await stt_service.transcribe(audio_data, sample_rate)
        
        if transcription:
            return JSONResponse({
                "text": transcription,
                "success": True
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")
    except Exception as e:
        print(f"STT error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stt/transcribe-base64")
async def transcribe_audio_base64(request: Dict[str, Any]):
    """Transcribe base64-encoded audio to text"""
    try:
        stt_service = get_stt_service()
        
        audio_base64 = request.get("audio_base64")
        sample_rate = request.get("sample_rate", 16000)
        
        if not audio_base64:
            raise HTTPException(status_code=400, detail="audio_base64 is required")
        
        # Decode base64
        audio_data = base64.b64decode(audio_base64)
        
        # Transcribe
        transcription = await stt_service.transcribe(audio_data, sample_rate)
        
        if transcription:
            return JSONResponse({
                "text": transcription,
                "success": True
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")
    except Exception as e:
        print(f"STT error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

