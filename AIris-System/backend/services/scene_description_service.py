"""
Scene Description Service - Handles scene description mode logic
With advanced risk scoring and fall detection
"""

import cv2
import numpy as np
import time
import json
import os
import asyncio
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from PIL import Image
import torch
from groq import Groq

from services.model_service import ModelService
from services.email_service import get_email_service
from utils.frame_utils import draw_guidance_on_frame, load_font


# Risk factor keywords for quick frame-level assessment
RISK_KEYWORDS = {
    "critical": {
        "keywords": ["fire", "flames", "burning", "smoke", "blood", "bleeding", "unconscious", 
                     "not moving", "motionless", "collapsed", "fallen", "lying on floor", 
                     "lying on ground", "emergency", "injury", "injured"],
        "weight": 0.8
    },
    "high": {
        "keywords": ["falling", "stumbling", "tripping", "struggling", "distress", "pain",
                     "hurt", "accident", "crash", "broken", "danger", "hazard", "sparks"],
        "weight": 0.5
    },
    "moderate": {
        "keywords": ["unsteady", "wobbling", "slipping", "spill", "mess", "dark", "blocked",
                     "obstacle", "sharp", "hot", "stove on", "water on floor"],
        "weight": 0.3
    },
    "low": {
        "keywords": ["unusual", "strange", "odd", "unexpected", "unfamiliar"],
        "weight": 0.1
    }
}

# Keywords indicating a normal scene with activity/objects
NORMAL_SCENE_KEYWORDS = [
    "person", "man", "woman", "people", "standing", "walking", "sitting", "looking", "reaching",
    "room", "kitchen", "living", "bedroom", "bathroom", "office", "hallway",
    "furniture", "table", "chair", "couch", "sofa", "bed", "desk", 
    "window", "door", "cabinet", "shelf", "counter",
    "television", "tv", "computer", "monitor", "lamp", "plant",
    "objects", "items", "things"
]

# Keywords indicating a static/uniform surface (possible fall - camera facing wall/floor/ceiling)
STATIC_SURFACE_KEYWORDS = [
    # Surfaces
    "wall", "floor", "ceiling", "ground", "carpet", "tile", "tiles", "wood", "concrete",
    # Colors/uniform descriptions  
    "white", "black", "gray", "grey", "brown", "beige", "blue", "green", "red", "yellow", "orange",
    "plain", "blank", "empty", "solid", "uniform", "flat", "tan", "cream", "pink", "purple",
    # Textures
    "texture", "surface", "pattern", "fabric", "material", "paint", "painted",
    # Close-up indicators
    "close up", "closeup", "close-up", "macro", "detail", "up close",
    # Darkness/obstruction
    "dark", "darkness", "black", "nothing", "blur", "blurry", "blurred", "obscured",
    # Fall indicators
    "fallen", "lying", "down", "collapsed", "floor level",
    # BLIP misidentification patterns (often appears when camera is obscured/dark)
    "skateboard", "surfboard", "board"
]

# Immediate fall trigger keywords - if these appear, very likely a fall
IMMEDIATE_FALL_KEYWORDS = [
    "dark", "darkness", "black", "nothing", "blank", "empty",
    "skateboard", "surfboard",  # BLIP often sees these in dark/obscured conditions
    "blur", "blurry", "blurred"
]

# Static-only patterns - descriptions that are PURELY about color/surface with no scene content
# If the description matches these patterns and has no normal scene keywords = IMMEDIATE FALL
STATIC_ONLY_COLORS = [
    "white", "black", "gray", "grey", "brown", "beige", "blue", "green", "red", 
    "yellow", "orange", "tan", "cream", "pink", "purple", "maroon", "navy", 
    "olive", "teal", "gold", "silver", "dark", "light"
]

STATIC_ONLY_SURFACES = [
    "wall", "floor", "ceiling", "ground", "carpet", "tile", "tiles", "wood", 
    "concrete", "surface", "texture", "fabric", "material", "paint", "painted",
    "plain", "solid", "uniform", "flat", "close up", "closeup", "close-up"
]

# Abrupt event detection patterns (frame-to-frame transitions)
FALL_TRANSITION_PATTERNS = [
    # Normal scene → Static surface/wall/floor
    (NORMAL_SCENE_KEYWORDS, STATIC_SURFACE_KEYWORDS),
]


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
        self.frame_description_buffer: List[Dict[str, Any]] = []  # Now stores {timestamp, description, risk_indicators}
        self.logs = {}
        
        # Constants - OPTIMIZED FOR 2 FPS
        self.RECORDING_SPAN_MINUTES = 30
        self.FRAME_ANALYSIS_INTERVAL_SEC = 0.5   # 2 FPS for better fall detection
        self.SUMMARIZATION_BUFFER_SIZE = 5       # 5 frames = 2.5 seconds (faster summaries)
        self.RECORDINGS_DIR = "recordings"
        
        # Session stats
        self.descriptions_count = 0
        self.summaries_count = 0
        self.alerts_count = 0
        
        # Fall detection state
        self.previous_description = ""
        self.fall_alert_pending = False
        self.fall_confirmation_count = 0
        self.FALL_CONFIRMATION_THRESHOLD = 2  # Need 2 consecutive fall signals
        
        # Risk tracking
        self.current_risk_score = 0.0
        self.last_risk_factors: List[str] = []
        
        # Alert cooldown (1 minute between alerts)
        self.last_alert_time: Optional[float] = None
        self.ALERT_COOLDOWN_SECONDS = 60  # 1 minute
        
        # Font path
        self.FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'RobotoCondensed-Regular.ttf')
        if not os.path.exists(self.FONT_PATH):
            self.FONT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Merged_System', 'RobotoCondensed-Regular.ttf')
        
        os.makedirs(self.RECORDINGS_DIR, exist_ok=True)
    
    def _init_groq(self):
        """Initialize Groq client"""
        print("\n🔧 [Scene Description] Initializing Groq client...")
        api_key = os.environ.get("GROQ_API_KEY")
        
        if not api_key or not api_key.strip():
            print("   ❌ GROQ_API_KEY not found or empty!")
            self.groq_client = None
            return
        
        print(f"   ✓ Found API key: {api_key[:8]}...{api_key[-4:]}")
        
        try:
            self.groq_client = Groq(api_key=api_key)
            print("✅ [Scene Description] Groq client ready")
        except Exception as e:
            print(f"❌ [Scene Description] Failed to create Groq client: {e}")
            self.groq_client = None
    
    def _get_groq_response(self, prompt: str, system_prompt: str = "You are a helpful assistant.", 
                           model: str = "openai/gpt-oss-120b") -> Optional[str]:
        """Get response from Groq API"""
        if not self.groq_client:
            return None
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=0.3,  # Lower temperature for more consistent risk assessment
                max_tokens=500
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return None
    
    def _quick_risk_assessment(self, description: str) -> Tuple[float, List[str]]:
        """Quick keyword-based risk assessment for a single frame"""
        desc_lower = description.lower()
        risk_score = 0.0
        risk_factors = []
        
        for level, data in RISK_KEYWORDS.items():
            for keyword in data["keywords"]:
                if keyword in desc_lower:
                    risk_score = max(risk_score, data["weight"])
                    risk_factors.append(f"{level}: {keyword}")
        
        return risk_score, risk_factors
    
    def _is_static_only_frame(self, description: str) -> Tuple[bool, str]:
        """
        Check if a frame description indicates a fall/collision.
        Triggers on:
        - "dark area", "dark room", "dark space", "darkness" (dark area/view, not just "dark" word)
        - "skateboard" keyword (BLIP misidentification pattern for dark/obscured views)
        - "wall" mentioned (any wall, with or without color - stationary view indicates fall)
        - OR background/floor/ceiling/ground mentioned WITH a color
        Returns (is_static_only, reason)
        """
        desc_lower = description.lower().strip()
        
        # Check for "dark area" patterns - indicates dark view/area, not just "dark" as an adjective
        dark_area_patterns = [
            "dark area", "dark room", "dark space", "dark place", "dark view",
            "darkness", "dark scene", "dark image", "dark picture", "dark view"
        ]
        for pattern in dark_area_patterns:
            if pattern in desc_lower:
                return True, f"Dark area/view detected: '{desc_lower}'"
        
        # Check for "skateboard" - BLIP often sees this in dark/obscured conditions
        if "skateboard" in desc_lower or "surfboard" in desc_lower:
            return True, f"Skateboard/surfboard detected (fall indicator): '{desc_lower}'"
        
        # Check for "wall" - any wall mention indicates stationary view = fall
        if "wall" in desc_lower:
            return True, f"Wall detected (stationary view): '{desc_lower}'"
        
        # Check for background/floor/ceiling/ground WITH a color
        surface_keywords = ["background", "floor", "ceiling", "ground"]
        has_surface = any(surface in desc_lower for surface in surface_keywords)
        
        if has_surface:
            # Check if a color is also mentioned
            has_color = any(color in desc_lower for color in STATIC_ONLY_COLORS)
            if has_color:
                return True, f"Surface ({[s for s in surface_keywords if s in desc_lower][0]}) with color detected: '{desc_lower}'"
        
        return False, ""
    
    def _check_fall_transition(self, prev: str, curr: str) -> bool:
        """Check if there's a fall-indicating transition between frames - VERY SENSITIVE"""
        if not prev:
            return False
        
        prev_l, curr_l = prev.lower(), curr.lower()
        
        # IMMEDIATE FALL TRIGGERS - these keywords alone indicate a fall
        # (skateboard/surfboard often appear when BLIP sees dark/obscured views)
        has_immediate_trigger = any(kw in curr_l for kw in IMMEDIATE_FALL_KEYWORDS)
        if has_immediate_trigger:
            triggered_by = [kw for kw in IMMEDIATE_FALL_KEYWORDS if kw in curr_l]
            print(f"🚨 IMMEDIATE FALL TRIGGER: '{triggered_by}' detected in current frame")
            print(f"   Curr: '{curr_l[:100]}'")
            return True
        
        # Check if previous frame had ANY visible scenery
        prev_had_scenery = any(kw in prev_l for kw in NORMAL_SCENE_KEYWORDS)
        
        # Check if current frame shows static/color/surface
        curr_has_static = any(kw in curr_l for kw in STATIC_SURFACE_KEYWORDS)
        
        # If previous had scenery and current has any static indicator = FALL
        if prev_had_scenery and curr_has_static:
            print(f"🔍 FALL DETECTED: Scenery → Static surface")
            print(f"   Prev: '{prev_l[:80]}...'")
            print(f"   Curr: '{curr_l[:80]}...'")
            return True
        
        # Very short description after a scene = likely just seeing a surface
        curr_words = len(curr_l.split())
        if prev_had_scenery and curr_words <= 4:
            print(f"🔍 FALL DETECTED: Scenery → Very short description ({curr_words} words)")
            print(f"   Prev: '{prev_l[:80]}...'")
            print(f"   Curr: '{curr_l}'")
            return True
        
        # Color-only detection
        color_keywords = ["white", "gray", "grey", "brown", "beige", "blue", "green", "red", 
                         "yellow", "orange", "tan", "cream", "pink", "purple"]
        curr_is_color = any(kw in curr_l for kw in color_keywords)
        
        if curr_is_color and curr_words <= 6:
            print(f"🔍 FALL DETECTED: Current is primarily a color")
            return True
        
        return False
    
    def _build_analysis_prompt(self, frame_entries: List[Dict[str, Any]]) -> str:
        """Build the combined summarization + risk assessment prompt"""
        observations = "\n".join([
            f"{i+1}. [{entry['offset']:.1f}s] {entry['description']}"
            for i, entry in enumerate(frame_entries)
        ])
        
        duration = len(frame_entries) * 0.5  # Each frame is 0.5 seconds
        
        prompt = f"""You are analyzing vision model outputs from a safety monitoring camera for a visually impaired person.

CRITICAL CONTEXT:
- These descriptions come from a basic vision model (BLIP) that produces LITERAL, CRUDE descriptions
- Descriptions like "a person in a room" or "a table with items" are normal - don't read danger into mundane descriptions
- The vision model often describes ordinary scenes in simple terms - this is NOT suspicious
- Infer LOGICAL, REALISTIC scenarios from the descriptions - most situations are perfectly normal
- DO NOT overexaggerate or assume danger without clear indicators
- A low risk score (0.0-0.2) is the EXPECTED default for normal daily activities

OBSERVATIONS ({len(frame_entries)} frames over ~{duration:.1f}s):
{observations}

Provide analysis in this exact JSON format (no markdown):
{{
    "summary": "1-2 sentence description of what's likely happening. Be matter-of-fact, not alarmist.",
    "risk_score": 0.0,
    "risk_factors": [],
    "confidence": 0.0,
    "reasoning": "Brief explanation"
}}

RISK SCORE (be conservative - most situations are safe):
- 0.0-0.2: Normal activity (DEFAULT for everyday scenes - sitting, walking, cooking, watching TV, working)
- 0.3-0.4: Minor unusual activity (reaching high, quick movement) - still probably fine
- 0.5-0.6: Potentially concerning (if multiple frames suggest something off)
- 0.7-0.8: Likely concerning (clear signs of distress, hazard, or problem)
- 0.9-1.0: Emergency (fall confirmed, fire/smoke visible, injury, person collapsed)

ACTUAL DANGER SIGNS:
- Person on floor/ground when they were standing before
- Sudden camera view change to ceiling/floor/wall (possible fall)
- Words like "fire", "smoke", "flames", "blood", "fallen", "collapsed"
- Consistent frames showing the same concerning pattern

CRITICAL - FALL/COLLISION DETECTION:
If observations suddenly change from showing a scene (room, furniture, person, objects) to showing:
- A plain wall, floor, or ceiling
- A solid color (white, black, gray, brown, etc.)
- A uniform texture or surface
- "Close up" of any material
- Dark/black/nothing
This likely means the camera (or person wearing it) has FALLEN or COLLIDED with something.
Rate this as HIGH RISK (0.7-0.9) if you see this pattern.

DO NOT flag as risky:
- Normal room descriptions ("a room with furniture", "a kitchen", "person sitting")
- Ordinary activities described simply
- Single ambiguous frame among normal ones
- Lighting changes or camera adjustments

Respond with JSON only."""
        
        return prompt
    
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
        
        # Reset stats and state
        self.descriptions_count = 0
        self.summaries_count = 0
        self.alerts_count = 0
        self.previous_description = ""
        self.fall_alert_pending = False
        self.fall_confirmation_count = 0
        self.current_risk_score = 0.0
        self.last_risk_factors = []
        
        return {
            "status": "success",
            "message": "Recording started (2 FPS, 10-sec summaries)",
            "log_filename": self.log_filename
        }
    
    async def stop_recording(self) -> Dict[str, Any]:
        """Stop recording and save log"""
        if not self.is_recording:
            return {"status": "error", "message": "No recording in progress"}
        
        self.is_recording = False
        self.current_session_log["session_end"] = datetime.now().isoformat()
        
        filepath = os.path.join(self.RECORDINGS_DIR, self.log_filename)
        with open(filepath, 'w') as f:
            json.dump(self.current_session_log, f, indent=4)
        
        log_id = self.log_filename.replace('.json', '')
        self.logs[log_id] = self.current_session_log.copy()
        
        log_filename = self.log_filename
        self.current_session_log = {}
        self.log_filename = ""
        
        return {
            "status": "success",
            "message": "Recording stopped and saved",
            "log_filename": log_filename,
            "log_id": log_id
        }
    
    async def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a frame for scene description with risk assessment"""
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
                    "risk_score": 0.0,
                    "is_recording": False,
                    "message": "Recording session ended automatically",
                    "stats": self._get_session_stats(elapsed_seconds)
                }
        
        # Analyze frame at intervals (0.5 sec = 2 FPS)
        current_time = time.time()
        if self.is_recording and (current_time - self.last_frame_analysis_time) >= self.FRAME_ANALYSIS_INTERVAL_SEC:
            self.last_frame_analysis_time = current_time
            frame_offset = elapsed_seconds  # Time since recording started
            
            # Get vision model
            vision_processor, vision_model, device = await self.model_service.load_vision_model()
            
            if vision_processor and vision_model:
                # Generate description
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(rgb_frame)
                inputs = vision_processor(images=image, return_tensors="pt").to(device)
                generated_ids = vision_model.generate(**inputs, max_length=50)
                description = vision_processor.decode(generated_ids[0], skip_special_tokens=True).strip()
                
                # Quick risk assessment for this frame
                frame_risk, risk_indicators = self._quick_risk_assessment(description)
                
                # Track if fall alert was sent this frame
                fall_alert_sent = False
                
                # === FALL DETECTION: STATIC-ONLY FRAME (IMMEDIATE TRIGGER) ===
                is_static, static_reason = self._is_static_only_frame(description)
                if is_static:
                    print(f"🚨 STATIC-ONLY FRAME DETECTED - IMMEDIATE FALL ALERT!")
                    print(f"   Reason: {static_reason}")
                    
                    # Send immediate fall alert (with cooldown check)
                    email_sent = await self._send_fall_alert_email()
                    if email_sent:
                        self.alerts_count += 1
                        fall_alert_sent = True
                        
                        # Log the event
                        self.current_session_log["events"].append({
                            "timestamp": datetime.now().isoformat(),
                            "type": "FALL_ALERT",
                            "summary": f"Possible fall or collision detected: {static_reason}",
                            "risk_score": 0.95
                        })
                        
                        # Track for daily/weekly summary
                        self._track_fall_event()
                    else:
                        print("⚠️ Fall alert not sent (cooldown or email not configured)")
                    
                    # Reset fall detection state
                    self.fall_confirmation_count = 0
                
                # === FALL DETECTION: TRANSITION-BASED (BACKUP) ===
                elif self._check_fall_transition(self.previous_description, description):
                    self.fall_confirmation_count += 1
                    print(f"⚠️ Fall transition signal! Count: {self.fall_confirmation_count}/{self.FALL_CONFIRMATION_THRESHOLD}")
                    
                    if self.fall_confirmation_count >= self.FALL_CONFIRMATION_THRESHOLD:
                        print("🚨 FALL CONFIRMED via transition - Sending alert!")
                        
                        # Send fall alert (with cooldown check)
                        email_sent = await self._send_fall_alert_email()
                        if email_sent:
                            self.alerts_count += 1
                            fall_alert_sent = True
                            
                            self.current_session_log["events"].append({
                                "timestamp": datetime.now().isoformat(),
                                "type": "FALL_ALERT",
                                "summary": "Possible fall or collision detected (scene transition)",
                                "risk_score": 0.95
                            })
                            
                            self._track_fall_event()
                        else:
                            print("⚠️ Fall alert not sent (cooldown or email not configured)")
                        
                        self.fall_confirmation_count = 0
                else:
                    # No fall detected - reset counter
                    self.fall_confirmation_count = 0
                
                self.previous_description = description
                
                # Add to buffer with metadata
                self.frame_description_buffer.append({
                    "timestamp": datetime.now().isoformat(),
                    "offset": frame_offset,
                        "description": description,
                    "frame_risk": frame_risk,
                    "risk_indicators": risk_indicators
                })
                self.descriptions_count += 1
                
                # === SUMMARIZATION WITH RISK SCORING (every 20 frames = 10 sec) ===
                if len(self.frame_description_buffer) >= self.SUMMARIZATION_BUFFER_SIZE:
                    result = await self._process_buffer(annotated_frame, elapsed_seconds, description)
                    # Add fall_alert_sent flag and merge alert_sent
                    result["fall_alert_sent"] = fall_alert_sent
                    if fall_alert_sent:
                        result["alert_sent"] = True
                        result["safety_alert"] = True
                    return result
                else:
                    # Return current frame info without summary
                    status_text = f"🔴 REC {int(elapsed_seconds)}s | Frame {len(self.frame_description_buffer)}/{self.SUMMARIZATION_BUFFER_SIZE}"
                    if frame_risk > 0.3:
                        status_text += f" | Risk: {frame_risk:.1f}"
                    if fall_alert_sent:
                        status_text += " | ⚠️ FALL ALERT SENT"
                    annotated_frame = self._draw_text_on_frame(annotated_frame, status_text)
                    
                    return {
                        "annotated_frame": annotated_frame,
                        "description": description,
                        "summary": None,
                        "safety_alert": fall_alert_sent,
                        "risk_score": 0.95 if fall_alert_sent else frame_risk,
                        "is_recording": True,
                        "stats": self._get_session_stats(elapsed_seconds),
                        "recent_observations": [e["description"] for e in self.frame_description_buffer[-5:]],
                        "fall_alert_sent": fall_alert_sent,
                        "alert_sent": fall_alert_sent
                    }
        
        # No analysis this frame - return current state
        if self.is_recording:
            buffer_count = len(self.frame_description_buffer)
            status_text = f"🔴 REC {int(elapsed_seconds)}s | {buffer_count}/{self.SUMMARIZATION_BUFFER_SIZE}"
            annotated_frame = self._draw_text_on_frame(annotated_frame, status_text)
        else:
            annotated_frame = self._draw_text_on_frame(annotated_frame, "Scene Description: Ready")
        
        return {
            "annotated_frame": annotated_frame,
            "description": None,
            "summary": None,
            "safety_alert": False,
            "risk_score": self.current_risk_score,
            "is_recording": self.is_recording,
            "stats": self._get_session_stats(elapsed_seconds) if self.is_recording else None,
            "recent_observations": [e["description"] for e in self.frame_description_buffer[-5:]] if self.frame_description_buffer else [],
            "fall_alert_sent": False,
            "alert_sent": False
        }
    
    async def _process_buffer(self, annotated_frame: np.ndarray, elapsed_seconds: float, 
                              latest_description: str) -> Dict[str, Any]:
        """Process the full buffer with LLM for summary and risk assessment"""
        buffer_copy = list(self.frame_description_buffer)
        self.frame_description_buffer = []  # Clear buffer
        
        if not self.groq_client:
            print("⚠️ LLM not available for summarization!")
            return {
                "annotated_frame": annotated_frame,
                "description": latest_description,
                "summary": None,
                "safety_alert": False,
                "risk_score": 0.0,
                "is_recording": True,
                "stats": self._get_session_stats(elapsed_seconds),
                "error": "LLM not configured",
                "fall_alert_sent": False,
                "alert_sent": False
            }
        
        # Build and send analysis prompt
        prompt = self._build_analysis_prompt(buffer_copy)
        system_prompt = """You analyze camera observations for a home safety system. The observations come from a basic vision model that produces simple, literal descriptions of scenes.

KEY PRINCIPLES:
- Most observations describe NORMAL, SAFE daily activities - treat them as such
- Simple descriptions like "a person in a room" or "kitchen with appliances" are completely normal
- Only flag genuine safety concerns with clear, consistent evidence across multiple frames
- A person doing ordinary things (sitting, walking, cooking, watching TV) is SAFE
- Default to low risk scores (0.0-0.2) unless there's real evidence of danger
- Respond with valid JSON only"""
        
        response = self._get_groq_response(prompt, system_prompt=system_prompt)
        
        if not response:
            print("⚠️ LLM call failed")
            return {
                "annotated_frame": annotated_frame,
                "description": latest_description,
                "summary": None,
                "safety_alert": False,
                "risk_score": 0.0,
                "is_recording": True,
                "stats": self._get_session_stats(elapsed_seconds),
                "error": "LLM call failed",
                "fall_alert_sent": False,
                "alert_sent": False
            }
        
        # Parse JSON response
        try:
            # Clean up response (remove markdown if present)
            json_str = response.strip()
            if json_str.startswith("```"):
                json_str = re.sub(r'^```(?:json)?\s*', '', json_str)
                json_str = re.sub(r'\s*```$', '', json_str)
            
            analysis = json.loads(json_str)
            
            summary = analysis.get("summary", "No summary available")
            risk_score = float(analysis.get("risk_score", 0.0))
            risk_factors = analysis.get("risk_factors", [])
            confidence = float(analysis.get("confidence", 0.5))
            reasoning = analysis.get("reasoning", "")
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"⚠️ Failed to parse LLM response: {e}")
            print(f"   Response was: {response[:200]}...")
            # Fallback: use response as summary, calculate risk from frame-level data
            summary = response[:500] if response else "Analysis failed"
            avg_frame_risk = sum(e["frame_risk"] for e in buffer_copy) / len(buffer_copy)
            risk_score = avg_frame_risk
            risk_factors = list(set(
                indicator 
                for e in buffer_copy 
                for indicator in e.get("risk_indicators", [])
            ))
            confidence = 0.3
            reasoning = "Fallback analysis"
        
        self.summaries_count += 1
        self.current_risk_score = risk_score
        self.last_risk_factors = risk_factors
        
        # Get risk threshold from email service
        email_service = get_email_service()
        risk_threshold = getattr(email_service, 'risk_threshold', 0.5)
        
        # Determine if alert should be sent
        should_alert = risk_score >= risk_threshold
        alert_actually_sent = False
        
        if should_alert:
            print(f"🚨 Risk score {risk_score:.2f} >= threshold {risk_threshold:.2f} - Sending alert!")
            alert_actually_sent = await self._send_safety_alert_email(
                summary=summary,
                descriptions=[e["description"] for e in buffer_copy],
                risk_score=risk_score,
                risk_factors=risk_factors
            )
            if alert_actually_sent:
                self.alerts_count += 1
            else:
                print("⚠️ Safety alert not sent (cooldown or email not configured)")
        else:
            # Track for daily summary
            self._track_observation(summary, [e["description"] for e in buffer_copy], risk_score)
        
        # Log the event
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "SUMMARY",
            "summary": summary,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "reasoning": reasoning,
            "alert_sent": alert_actually_sent,
            "frame_count": len(buffer_copy)
        }
        self.current_session_log["events"].append(log_entry)
        
        # Draw status
        status_text = f"🔴 REC {int(elapsed_seconds)}s | Risk: {risk_score:.2f}"
        if alert_actually_sent:
            status_text += " | ⚠️ ALERT"
        annotated_frame = self._draw_text_on_frame(annotated_frame, status_text)
        
        return {
            "annotated_frame": annotated_frame,
            "description": latest_description,
            "summary": summary,
            "safety_alert": alert_actually_sent,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "is_recording": True,
            "stats": self._get_session_stats(elapsed_seconds),
            "recent_observations": [e["description"] for e in buffer_copy[-5:]],
            "fall_alert_sent": False,  # Will be overwritten by caller if fall was detected
            "alert_sent": alert_actually_sent
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
            "analysis_interval": self.FRAME_ANALYSIS_INTERVAL_SEC,
            "current_risk_score": self.current_risk_score,
            "fps": 1 / self.FRAME_ANALYSIS_INTERVAL_SEC
        }
    
    def _draw_text_on_frame(self, frame: np.ndarray, text: str) -> np.ndarray:
        """Draw text on frame using PIL for better quality"""
        custom_font = load_font(self.FONT_PATH, size=20)
        return draw_guidance_on_frame(frame, text, custom_font)
    
    def _can_send_alert(self) -> bool:
        """Check if enough time has passed since last alert (cooldown)"""
        if self.last_alert_time is None:
            return True
        
        time_since_last = time.time() - self.last_alert_time
        if time_since_last >= self.ALERT_COOLDOWN_SECONDS:
            return True
        
        remaining = self.ALERT_COOLDOWN_SECONDS - time_since_last
        print(f"⏳ Alert cooldown active. {remaining:.1f} seconds remaining.")
        return False
    
    async def _send_safety_alert_email(self, summary: str, descriptions: List[str], 
                                       risk_score: float, risk_factors: List[str]):
        """Send safety alert email with risk score (with cooldown check)"""
        if not self._can_send_alert():
            print("⚠️ Skipping safety alert - cooldown active")
            return False
        
        try:
            email_service = get_email_service()
            if email_service.is_configured():
                await email_service.send_safety_alert(
                    summary=summary,
                    raw_descriptions=descriptions,
                    timestamp=datetime.now(),
                    risk_score=risk_score,
                    risk_factors=risk_factors,
                    is_fall=False
                )
                self.last_alert_time = time.time()
                return True
        except Exception as e:
            print(f"⚠️ Failed to send safety alert email: {e}")
        return False
    
    async def _send_fall_alert_email(self):
        """Send a simple fall alert email - no extra details (with cooldown check)"""
        if not self._can_send_alert():
            print("⚠️ Skipping fall alert - cooldown active")
            return False
        
        try:
            email_service = get_email_service()
            if email_service.is_configured():
                await email_service.send_fall_alert(timestamp=datetime.now())
                self.last_alert_time = time.time()
                return True
        except Exception as e:
            print(f"⚠️ Failed to send fall alert email: {e}")
        return False
    
    def _track_fall_event(self):
        """Track fall event for daily/weekly summaries - simple entry only"""
        try:
            email_service = get_email_service()
            email_service.add_fall_event(timestamp=datetime.now())
        except Exception as e:
            print(f"⚠️ Failed to track fall event: {e}")
    
    async def _send_fall_alert_email(self):
        """Send a simple fall alert email - no extra details"""
        try:
            email_service = get_email_service()
            if email_service.is_configured():
                await email_service.send_fall_alert(timestamp=datetime.now())
        except Exception as e:
            print(f"⚠️ Failed to send fall alert email: {e}")
    
    def _track_fall_event(self):
        """Track fall event for daily/weekly summaries"""
        try:
            email_service = get_email_service()
            email_service.add_fall_event(timestamp=datetime.now())
        except Exception as e:
            print(f"⚠️ Failed to track fall event: {e}")
    
    def _track_observation(self, summary: str, descriptions: List[str], risk_score: float):
        """Track observation for daily/weekly summaries"""
        try:
            email_service = get_email_service()
            email_service.add_observation(
                summary=summary,
                descriptions=descriptions,
                timestamp=datetime.now(),
                risk_score=risk_score
            )
        except Exception as e:
            print(f"⚠️ Failed to track observation: {e}")
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all recording logs"""
        return list(self.logs.values())
    
    def get_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific recording log"""
        return self.logs.get(log_id)
