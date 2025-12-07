"""
Scene Description Service - Handles scene description mode logic
"""

import cv2
import numpy as np
import time
import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from PIL import Image
import torch
from groq import Groq

from services.model_service import ModelService
from services.email_service import get_email_service
from utils.frame_utils import draw_guidance_on_frame, load_font

class SceneDescriptionService:
    def __init__(self, model_service: ModelService):
        self.model_service = model_service
        self.groq_client = None
        self._init_groq()
        
        # State management
        self.is_recording = False
        self.recording_start_time = 0
        self.last_frame_analysis_time = 0
        self.current_session_log = {}
        self.log_filename = ""
        self.frame_description_buffer = []
        self.logs = {}  # Store all logs in memory
        
        # Constants
        self.RECORDING_SPAN_MINUTES = 30
        self.FRAME_ANALYSIS_INTERVAL_SEC = 3  # Faster analysis (was 10s)
        self.SUMMARIZATION_BUFFER_SIZE = 5    # More samples before summarizing (was 3)
        self.RECORDINGS_DIR = "recordings"
        
        # Session stats
        self.descriptions_count = 0
        self.summaries_count = 0
        self.alerts_count = 0
        
        # Font path
        self.FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'RobotoCondensed-Regular.ttf')
        if not os.path.exists(self.FONT_PATH):
            self.FONT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Merged_System', 'RobotoCondensed-Regular.ttf')
        
        # Ensure recordings directory exists
        os.makedirs(self.RECORDINGS_DIR, exist_ok=True)
    
    def _init_groq(self):
        """Initialize Groq client"""
        print("\n🔧 [Scene Description] Initializing Groq client...")
        api_key = os.environ.get("GROQ_API_KEY")
        
        print(f"   Checking for GROQ_API_KEY in environment...")
        if not api_key:
            print("   ❌ GROQ_API_KEY environment variable not found!")
            print("   Please set GROQ_API_KEY in your .env file or environment variables")
            print("   Get your API key from: https://console.groq.com/keys")
            self.groq_client = None
            return
        
        if not api_key.strip():
            print("   ❌ GROQ_API_KEY is empty!")
            print("   Please set a valid GROQ_API_KEY in your .env file")
            self.groq_client = None
            return
        
        print(f"   ✓ Found API key: {api_key[:8]}...{api_key[-4:]}")
        
        try:
            print(f"   Creating Groq client...")
            self.groq_client = Groq(api_key=api_key)
            print(f"   ✓ Groq client object created")
            
            # Test the connection (optional - don't fail if this doesn't work)
            print(f"   Testing API connection...")
            try:
                test_response = self.groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                print("   ✓ API test successful!")
                print("✅ [Scene Description] Groq client ready (openai/gpt-oss-120b)")
            except Exception as test_error:
                print(f"   ⚠️ API test failed: {test_error}")
                print("   Client will still be used - test failure doesn't mean client is broken")
                print("✅ [Scene Description] Groq client ready (test skipped)")
        except Exception as e:
            print(f"❌ [Scene Description] Failed to create Groq client: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            self.groq_client = None
    
    def _get_groq_response(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = "openai/gpt-oss-120b") -> Optional[str]:
        """Get response from Groq API. Returns None if unavailable."""
        if not self.groq_client:
            return None
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model=model
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return None
    
    async def start_recording(self) -> Dict[str, Any]:
        """Start scene description recording"""
        if self.is_recording:
            return {"status": "error", "message": "Recording already in progress"}
        
        self.is_recording = True
        self.recording_start_time = time.time()
        self.last_frame_analysis_time = time.time()
        self.log_filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.current_session_log = {
            "session_start": datetime.now().isoformat(),
            "events": []
        }
        self.frame_description_buffer = []
        
        # Reset session stats
        self.descriptions_count = 0
        self.summaries_count = 0
        self.alerts_count = 0
        
        return {
            "status": "success",
            "message": "Recording started",
            "log_filename": self.log_filename
        }
    
    async def stop_recording(self) -> Dict[str, Any]:
        """Stop recording and save log"""
        if not self.is_recording:
            return {"status": "error", "message": "No recording in progress"}
        
        self.is_recording = False
        self.current_session_log["session_end"] = datetime.now().isoformat()
        
        # Save log to file
        filepath = os.path.join(self.RECORDINGS_DIR, self.log_filename)
        with open(filepath, 'w') as f:
            json.dump(self.current_session_log, f, indent=4)
        
        # Store in memory
        log_id = self.log_filename.replace('.json', '')
        self.logs[log_id] = self.current_session_log.copy()
        
        # Reset state
        log_filename = self.log_filename
        self.current_session_log = {}
        self.log_filename = ""
        
        return {
            "status": "success",
            "message": f"Recording stopped and saved",
            "log_filename": log_filename,
            "log_id": log_id
        }
    
    async def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a frame for scene description"""
        annotated_frame = frame.copy()
        elapsed_seconds = 0
        
        # Check if recording session should end
        if self.is_recording:
            elapsed_seconds = time.time() - self.recording_start_time
            elapsed_minutes = elapsed_seconds / 60
            if elapsed_minutes >= self.RECORDING_SPAN_MINUTES:
                await self.stop_recording()
                return {
                    "annotated_frame": annotated_frame,
                    "description": None,
                    "summary": None,
                    "safety_alert": False,
                    "is_recording": False,
                    "message": "Recording session ended automatically",
                    "stats": self._get_session_stats(elapsed_seconds)
                }
        
        # Analyze frame at intervals
        if self.is_recording and time.time() - self.last_frame_analysis_time > self.FRAME_ANALYSIS_INTERVAL_SEC:
            self.last_frame_analysis_time = time.time()
            
            # Get vision model
            vision_processor, vision_model, device = await self.model_service.load_vision_model()
            
            if vision_processor and vision_model:
                # Convert frame to PIL Image
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(rgb_frame)
                
                # Generate description
                inputs = vision_processor(images=image, return_tensors="pt").to(device)
                generated_ids = vision_model.generate(**inputs, max_length=50)
                description = vision_processor.decode(generated_ids[0], skip_special_tokens=True).strip()
                
                self.frame_description_buffer.append(description)
                self.descriptions_count += 1
                
                # Summarize when buffer is full
                if len(self.frame_description_buffer) >= self.SUMMARIZATION_BUFFER_SIZE:
                    descriptions = list(set(self.frame_description_buffer))
                    prompts = self.model_service.get_prompts()
                    
                    # LLM summarization required - no fallback
                    summary = None
                    is_harmful = False
                    
                    if not self.groq_client:
                        # LLM not available - skip summarization, keep collecting observations
                        print(f"⚠️  LLM not available for summarization!")
                        print(f"   self.groq_client = {self.groq_client}")
                        print(f"   GROQ_API_KEY in env: {'Yes' if os.environ.get('GROQ_API_KEY') else 'No'}")
                        print("   Please set GROQ_API_KEY in .env and restart the backend.")
                        self.frame_description_buffer = []  # Clear buffer to try again
                        return {
                            "annotated_frame": annotated_frame,
                            "description": description,
                            "summary": None,
                            "safety_alert": False,
                            "is_recording": True,
                            "stats": self._get_session_stats(elapsed_seconds),
                            "recent_observations": descriptions[-5:],
                            "error": "LLM not configured - summarization unavailable"
                        }
                    
                    system_prompt = prompts.get('scene_description', {}).get('summarization_system', '')
                    user_prompt = prompts.get('scene_description', {}).get('summarization_user', '').format(
                        observations=". ".join(descriptions)
                    )
                    summary = self._get_groq_response(user_prompt, system_prompt=system_prompt)
                    
                    # If LLM call failed, skip this summarization cycle
                    if not summary:
                        print("⚠️  LLM call failed - skipping summarization cycle")
                        self.frame_description_buffer = []  # Clear buffer to try again
                        return {
                            "annotated_frame": annotated_frame,
                            "description": description,
                            "summary": None,
                            "safety_alert": False,
                            "is_recording": True,
                            "stats": self._get_session_stats(elapsed_seconds),
                            "recent_observations": descriptions[-5:],
                            "error": "LLM call failed - will retry next cycle"
                        }
                    
                    self.summaries_count += 1
                    
                    # Safety check
                    safety_prompt = prompts.get('scene_description', {}).get('safety_alert_user', '').format(
                        summary=summary
                    )
                    safety_response = self._get_groq_response(safety_prompt)
                    if safety_response:
                        is_harmful = "HARMFUL" in safety_response.strip().upper()
                    
                    if is_harmful:
                        self.alerts_count += 1
                        # Send email alert in background (non-blocking)
                        asyncio.create_task(self._send_safety_alert_email(summary, descriptions))
                    else:
                        # Track non-alert observations for daily summary
                        self._track_observation(summary, descriptions)
                    
                    # Log entry
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "summary": summary,
                        "raw_descriptions": descriptions,
                        "flag": "SAFETY_ALERT" if is_harmful else "None"
                    }
                    self.current_session_log["events"].append(log_entry)
                    self.frame_description_buffer = []
                    
                    # Draw status on frame
                    elapsed_minutes = elapsed_seconds / 60
                    status_text = f"🔴 RECORDING | {int(elapsed_seconds)}s"
                    if is_harmful:
                        status_text += " | ⚠️ ALERT"
                    
                    annotated_frame = self._draw_text_on_frame(annotated_frame, status_text)
                    
                    return {
                        "annotated_frame": annotated_frame,
                        "description": description,
                        "summary": summary,
                        "safety_alert": is_harmful,
                        "is_recording": True,
                        "stats": self._get_session_stats(elapsed_seconds),
                        "recent_observations": list(self.frame_description_buffer[-5:]) if self.frame_description_buffer else descriptions[-5:]
                    }
                else:
                    # Return just the description without summary
                    elapsed_minutes = elapsed_seconds / 60
                    status_text = f"🔴 RECORDING | {int(elapsed_seconds)}s | Observing..."
                    annotated_frame = self._draw_text_on_frame(annotated_frame, status_text)
                    
                    return {
                        "annotated_frame": annotated_frame,
                        "description": description,
                        "summary": None,
                        "safety_alert": False,
                        "is_recording": True,
                        "stats": self._get_session_stats(elapsed_seconds),
                        "recent_observations": list(self.frame_description_buffer[-5:])
                    }
        
        # Draw status on frame
        if self.is_recording:
            status_text = f"🔴 RECORDING | {int(elapsed_seconds)}s"
            annotated_frame = self._draw_text_on_frame(annotated_frame, status_text)
        else:
            annotated_frame = self._draw_text_on_frame(annotated_frame, "Scene Description: Ready")
        
        return {
            "annotated_frame": annotated_frame,
            "description": None,
            "summary": None,
            "safety_alert": False,
            "is_recording": self.is_recording,
            "stats": self._get_session_stats(elapsed_seconds) if self.is_recording else None,
            "recent_observations": list(self.frame_description_buffer[-5:]) if self.frame_description_buffer else []
        }
    
    def _get_session_stats(self, elapsed_seconds: float) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            "elapsed_seconds": int(elapsed_seconds),
            "descriptions_count": self.descriptions_count,
            "summaries_count": self.summaries_count,
            "alerts_count": self.alerts_count,
            "buffer_size": len(self.frame_description_buffer),
            "buffer_max": self.SUMMARIZATION_BUFFER_SIZE,
            "analysis_interval": self.FRAME_ANALYSIS_INTERVAL_SEC
        }
    
    def _draw_text_on_frame(self, frame: np.ndarray, text: str) -> np.ndarray:
        """Draw text on frame using PIL for better quality"""
        custom_font = load_font(self.FONT_PATH, size=20)
        return draw_guidance_on_frame(frame, text, custom_font)
    
    async def _send_safety_alert_email(self, summary: str, descriptions: List[str]):
        """Send safety alert email in background"""
        try:
            email_service = get_email_service()
            if email_service.is_configured():
                await email_service.send_safety_alert(
                    summary=summary,
                    raw_descriptions=descriptions,
                    timestamp=datetime.now()
                )
        except Exception as e:
            print(f"⚠️  Failed to send safety alert email: {e}")
    
    def _track_observation(self, summary: str, descriptions: List[str]):
        """Track regular observation for daily/weekly summaries"""
        try:
            email_service = get_email_service()
            email_service.add_observation(
                summary=summary,
                descriptions=descriptions,
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"⚠️  Failed to track observation: {e}")
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all recording logs"""
        return list(self.logs.values())
    
    def get_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific recording log"""
        return self.logs.get(log_id)

