"""
Scene Description Service - Handles scene description mode logic
"""

import cv2
import numpy as np
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from PIL import Image
import torch
from groq import Groq

from services.model_service import ModelService
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
        self.FRAME_ANALYSIS_INTERVAL_SEC = 10
        self.SUMMARIZATION_BUFFER_SIZE = 3
        self.RECORDINGS_DIR = "recordings"
        
        # Font path
        self.FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'RobotoCondensed-Regular.ttf')
        if not os.path.exists(self.FONT_PATH):
            self.FONT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Merged_System', 'RobotoCondensed-Regular.ttf')
        
        # Ensure recordings directory exists
        os.makedirs(self.RECORDINGS_DIR, exist_ok=True)
    
    def _init_groq(self):
        """Initialize Groq client with GPT-OSS 120B model"""
        api_key = os.environ.get("GROQ_API_KEY")
        
        if not api_key:
            print("⚠️  GROQ_API_KEY environment variable not found!")
            print("   Please set GROQ_API_KEY in your .env file or environment variables")
            print("   Get your API key from: https://console.groq.com/keys")
            self.groq_client = None
            return
        
        if not api_key.strip():
            print("⚠️  GROQ_API_KEY is empty!")
            print("   Please set a valid GROQ_API_KEY in your .env file")
            self.groq_client = None
            return
        
        try:
            # Remove any proxy-related env vars that might interfere
            old_proxies = os.environ.pop('HTTP_PROXY', None), os.environ.pop('HTTPS_PROXY', None)
            try:
                # Initialize Groq client with API key
                self.groq_client = Groq(api_key=api_key)
                
                # Test the connection by making a simple API call
                try:
                    test_response = self.groq_client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "user", "content": "test"}
                        ],
                        max_tokens=5
                    )
                    print("✓ Groq client initialized successfully with GPT-OSS 120B (Scene Description)")
                    print(f"  Model: openai/gpt-oss-120b")
                except Exception as test_error:
                    print(f"⚠️  Groq client created but test API call failed: {test_error}")
                    print("   This might be a temporary issue. The client will still be used.")
            finally:
                # Restore proxies if they existed
                if old_proxies[0]:
                    os.environ['HTTP_PROXY'] = old_proxies[0]
                if old_proxies[1]:
                    os.environ['HTTPS_PROXY'] = old_proxies[1]
        except Exception as e:
            print(f"❌ Failed to initialize Groq client: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            self.groq_client = None
    
    def _get_groq_response(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = "openai/gpt-oss-120b") -> str:
        """Get response from Groq API using GPT-OSS 120B model"""
        if not self.groq_client:
            return "LLM Client not initialized. Please set GROQ_API_KEY in your .env file. Get your key from https://console.groq.com/keys"
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
            return f"Error: {e}"
    
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
        
        # Check if recording session should end
        if self.is_recording:
            elapsed_minutes = (time.time() - self.recording_start_time) / 60
            if elapsed_minutes >= self.RECORDING_SPAN_MINUTES:
                await self.stop_recording()
                return {
                    "annotated_frame": annotated_frame,
                    "description": None,
                    "summary": None,
                    "safety_alert": False,
                    "is_recording": False,
                    "message": "Recording session ended automatically"
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
                
                # Summarize when buffer is full
                if len(self.frame_description_buffer) >= self.SUMMARIZATION_BUFFER_SIZE:
                    descriptions = list(set(self.frame_description_buffer))
                    prompts = self.model_service.get_prompts()
                    
                    system_prompt = prompts.get('scene_description', {}).get('summarization_system', '')
                    user_prompt = prompts.get('scene_description', {}).get('summarization_user', '').format(
                        observations=". ".join(descriptions)
                    )
                    
                    summary = self._get_groq_response(user_prompt, system_prompt=system_prompt)
                    
                    # Safety check
                    safety_prompt = prompts.get('scene_description', {}).get('safety_alert_user', '').format(
                        summary=summary
                    )
                    safety_response = self._get_groq_response(safety_prompt).strip().upper()
                    is_harmful = "HARMFUL" in safety_response
                    
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
                    status_text = f"🔴 RECORDING... | Session ends in {self.RECORDING_SPAN_MINUTES - elapsed_minutes:.1f} mins"
                    if is_harmful:
                        status_text += " | ⚠️ SAFETY ALERT"
                    
                    annotated_frame = self._draw_text_on_frame(annotated_frame, status_text)
                    
                    return {
                        "annotated_frame": annotated_frame,
                        "description": description,
                        "summary": summary,
                        "safety_alert": is_harmful,
                        "is_recording": True
                    }
        
        # Draw status on frame
        if self.is_recording:
            elapsed_minutes = (time.time() - self.recording_start_time) / 60
            status_text = f"🔴 RECORDING... | Session ends in {self.RECORDING_SPAN_MINUTES - elapsed_minutes:.1f} mins"
            annotated_frame = self._draw_text_on_frame(annotated_frame, status_text)
        else:
            annotated_frame = self._draw_text_on_frame(annotated_frame, "Scene Description: Recording Paused")
        
        return {
            "annotated_frame": annotated_frame,
            "description": None,
            "summary": None,
            "safety_alert": False,
            "is_recording": self.is_recording
        }
    
    def _draw_text_on_frame(self, frame: np.ndarray, text: str) -> np.ndarray:
        """Draw text on frame using PIL for better quality"""
        custom_font = load_font(self.FONT_PATH, size=20)
        return draw_guidance_on_frame(frame, text, custom_font)
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all recording logs"""
        return list(self.logs.values())
    
    def get_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific recording log"""
        return self.logs.get(log_id)

