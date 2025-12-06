"""
Activity Guide Service - Handles activity guide mode logic
"""

import numpy as np
import cv2
import mediapipe as mp
import time
import re
import ast
from typing import Dict, List, Optional, Tuple, Any
from groq import Groq
import os
from PIL import ImageFont

from services.model_service import ModelService
from utils.frame_utils import draw_guidance_on_frame, load_font

class ActivityGuideService:
    def __init__(self, model_service: ModelService):
        self.model_service = model_service
        self.groq_client = None
        self._init_groq()
        
        # State management
        self.guidance_stage = "IDLE"
        self.current_instruction = "Start the camera and enter a task."
        self.instruction_history = []
        self.target_objects = []
        self.found_object_location = None
        self.last_guidance_time = 0
        self.verification_pairs = []
        self.next_stage_after_guiding = ""
        self.task_done_displayed = False
        self.object_last_seen_time = None
        self.object_disappeared_notified = False
        
        # Feedback tracking - to adjust behavior after failed attempts
        self.failed_attempts = 0
        self.last_failed_reason = None  # "depth", "misclassification", or "unknown"
        
        # Constants
        self.CONFIDENCE_THRESHOLD = 0.5
        self.DISTANCE_THRESHOLD_PIXELS = 100
        self.OCCLUSION_IOU_THRESHOLD = 0.3
        self.GUIDANCE_UPDATE_INTERVAL_SEC = 3
        self.POST_SPEECH_DELAY_SEC = 3
        
        # Font path
        self.FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'RobotoCondensed-Regular.ttf')
        if not os.path.exists(self.FONT_PATH):
            # Try alternative path
            self.FONT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Merged_System', 'RobotoCondensed-Regular.ttf')
        
        # Object aliases - only used when primary object is NOT found
        # Note: Removed cell phone -> remote alias as it caused false matches
        self.OBJECT_ALIASES = {
            "phone": ["cell phone"],  # "phone" can match "cell phone" (YOLO label)
            "watch": ["clock"],
            "bottle": ["cup", "mug"]
        }
        # Pairs that need verification (visually similar objects)
        self.VERIFICATION_PAIRS = [("watch", "clock")]
    
    def _init_groq(self):
        """Initialize Groq client with Llama 3.3 70B model"""
        # Try multiple ways to get the API key
        api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("groq_api_key")
        
        # Debug: Print environment info
        print(f"🔍 Checking for GROQ_API_KEY...")
        print(f"   GROQ_API_KEY exists: {bool(os.environ.get('GROQ_API_KEY'))}")
        print(f"   groq_api_key exists: {bool(os.environ.get('groq_api_key'))}")
        if api_key:
            print(f"   Key length: {len(api_key)} characters")
            print(f"   Key starts with: {api_key[:8]}...")
        
        if not api_key:
            print("⚠️  GROQ_API_KEY environment variable not found!")
            print("   Please set GROQ_API_KEY in your .env file or environment variables")
            print("   Get your API key from: https://console.groq.com/keys")
            print(f"   Current working directory: {os.getcwd()}")
            print(f"   Looking for .env in: {os.path.dirname(__file__)}")
            self.groq_client = None
            return
        
        if not api_key.strip():
            print("⚠️  GROQ_API_KEY is empty!")
            print("   Please set a valid GROQ_API_KEY in your .env file")
            self.groq_client = None
            return
        
        try:
            # Initialize Groq client with API key
            self.groq_client = Groq(api_key=api_key)
            
            # Test the connection by making a simple API call
            try:
                test_response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "user", "content": "test"}
                    ],
                    max_tokens=5
                )
                print("✓ Groq client initialized successfully (Activity Guide)")
                print(f"  Model: openai/gpt-oss-120b")
                print(f"  API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '****'}")
            except Exception as test_error:
                print(f"⚠️  Groq client created but test API call failed: {test_error}")
                print("   This might be a temporary issue. The client will still be used.")
                # Don't set to None - let it try anyway
                
        except TypeError as e:
            # Handle case where Groq client doesn't accept certain parameters
            if "proxies" in str(e) or "unexpected keyword" in str(e):
                print(f"⚠️  Groq client version may not support certain parameters. Error: {e}")
                print("   Trying alternative initialization...")
                try:
                    # Try with just api_key, no other parameters
                    import groq
                    import inspect
                    sig = inspect.signature(groq.Groq.__init__)
                    params = {}
                    if 'api_key' in sig.parameters:
                        params['api_key'] = api_key
                    self.groq_client = Groq(**params)
                    print("✓ Groq client initialized with minimal parameters")
                except Exception as e2:
                    print(f"❌ Alternative Groq initialization also failed: {e2}")
                    self.groq_client = None
            else:
                print(f"❌ Failed to initialize Groq client: {e}")
                self.groq_client = None
        except Exception as e:
            print(f"❌ Failed to initialize Groq client: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            self.groq_client = None
    
    def _get_groq_response(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = "openai/gpt-oss-120b") -> Optional[str]:
        """Get response from Groq API. Returns None if unavailable."""
        if not self.groq_client:
            return None  # Return None so callers can use fallback
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
            return None  # Return None so callers can use fallback
    
    async def start_task(self, goal: str, target_objects: Optional[List[str]] = None) -> Dict[str, Any]:
        """Start a new task"""
        # Reset state
        self.instruction_history = []
        self.task_done_displayed = False
        self.is_speaking = False
        self.object_last_seen_time = None
        self.object_disappeared_notified = False
        
        # Reset feedback tracking and adaptive thresholds
        self.failed_attempts = 0
        self.last_failed_reason = None
        self.CONFIDENCE_THRESHOLD = 0.5  # Reset to default
        if hasattr(self, 'DEPTH_STRICTNESS_MULTIPLIER'):
            del self.DEPTH_STRICTNESS_MULTIPLIER
        
        # Extract target objects if not provided
        if target_objects is None:
            prompts = self.model_service.get_prompts()
            extraction_prompt = prompts.get('activity_guide', {}).get('object_extraction', '').format(goal=goal)
            
            print(f"Extracting target object from goal: '{goal}'")
            response = self._get_groq_response(extraction_prompt)
            
            # Check if LLM client is not initialized or returned an error
            if not response:
                print("⚠️  LLM unavailable, falling back to direct goal parsing")
            else:
                print(f"LLM extraction response: {response}")
            
            try:
                target_extracted = False
                
                if response:
                    # Try to find a list in the response
                    match = re.search(r"\[.*?\]", response)
                    if match:
                        try:
                            target_list = ast.literal_eval(match.group(0))
                            if isinstance(target_list, list) and target_list:
                                primary_target = target_list[0].strip().lower()
                                print(f"✓ Extracted primary target from LLM list: {primary_target}")
                                self.verification_pairs = self.VERIFICATION_PAIRS
                                if primary_target in self.OBJECT_ALIASES:
                                    target_list.extend(self.OBJECT_ALIASES[primary_target])
                                self.target_objects = list(set([t.strip().lower() for t in target_list]))
                                print(f"Final target objects: {self.target_objects}")
                                target_extracted = True
                        except (ValueError, SyntaxError) as e:
                            print(f"Failed to parse list from LLM response: {e}")
                
                # If LLM extraction failed, extract directly from goal
                if not target_extracted:
                    print("Extracting object directly from goal text...")
                    goal_lower = goal.lower().strip()
                    print(f"  Goal (lowercase): '{goal_lower}'")
                    
                    # Define common objects in order of specificity (longer names first)
                    # IMPORTANT: Order matters - longer/more specific matches first
                    common_objects = [
                        "cell phone",  # Must come before "phone"
                        "keyboard", "mouse",  # Multi-word objects
                        "bottle", "cup", "mug", "watch", "clock", "phone", "remote", 
                        "book", "laptop", "pen", "pencil", "wallet", "keys"
                    ]
                    
                    # Find all matching objects using word boundaries
                    found_objects = []
                    for obj in common_objects:
                        # Use word boundaries to avoid false matches (e.g., "keys" in "keyboard")
                        pattern = r'\b' + re.escape(obj) + r'\b'
                        if re.search(pattern, goal_lower):
                            found_objects.append(obj)
                            print(f"  Found match: '{obj}' in goal")
                    
                    if found_objects:
                        # Prefer longer/more specific matches (e.g., "cell phone" over "phone")
                        primary_target = max(found_objects, key=len)
                        print(f"✓ Selected target (longest match): {primary_target}")
                        self.verification_pairs = self.VERIFICATION_PAIRS
                        target_list = [primary_target]
                        if primary_target in self.OBJECT_ALIASES:
                            target_list.extend(self.OBJECT_ALIASES[primary_target])
                        self.target_objects = list(set(target_list))
                        print(f"Final target objects: {self.target_objects}")
                        target_extracted = True
                    else:
                        print(f"  No objects found in goal: '{goal_lower}'")
                        raise ValueError(f"Could not determine object from goal: '{goal}'. Please be more specific (e.g., 'find my watch', 'find my keys').")
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing task: {e}")
                print(f"LLM Response: {response}")
                return {
                    "status": "error",
                    "message": f"Sorry, I had trouble understanding the task. Please try rephrasing it. (Error: {str(e)})",
                    "target_objects": [],
                    "primary_target": "",
                    "stage": "IDLE"
                }
        else:
            self.target_objects = target_objects
        
        if not self.target_objects:
            return {
                "status": "error",
                "message": "Could not determine what object to find. Please be more specific (e.g., 'find my keys', 'find my watch').",
                "target_objects": [],
                "primary_target": "",
                "stage": "IDLE"
            }
        
        primary_target = self.target_objects[0]
        self.guidance_stage = "FINDING_OBJECT"
        self.current_instruction = f"Okay, let's find the {primary_target}."
        self.instruction_history.append(self.current_instruction)
        self.last_guidance_time = time.time()
        self.found_object_location = None  # Reset found object location
        
        return {
            "status": "success",
            "message": f"Task started: {goal}",
            "target_objects": self.target_objects,
            "primary_target": primary_target,
            "stage": self.guidance_stage
        }
    
    async def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a frame for activity guide - always shows YOLO boxes and hand tracking"""
        yolo_model = self.model_service.get_yolo_model()
        hand_model = self.model_service.get_hand_model()
        
        if yolo_model is None:
            # Even without YOLO, try to show hand tracking if available
            annotated_frame = frame.copy()
            detected_hands = []
            if hand_model is not None:
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_results = hand_model.process(rgb_frame)
                    if mp_results.multi_hand_landmarks:
                        for hand_landmarks in mp_results.multi_hand_landmarks:
                            h, w, _ = frame.shape
                            coords = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
                            x_min, y_min = np.min(coords, axis=0)
                            x_max, y_max = np.max(coords, axis=0)
                            current_hand_box = [int(x_min * w), int(y_min * h), int(x_max * w), int(y_max * h)]
                            detected_hands.append({'box': current_hand_box})
                            mp.solutions.drawing_utils.draw_landmarks(
                                annotated_frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                            )
                except Exception as e:
                    print(f"Error processing hand detection: {e}")
            
            custom_font = load_font(self.FONT_PATH, size=24)
            annotated_frame = draw_guidance_on_frame(annotated_frame, self.current_instruction, custom_font)
            
            return {
                "annotated_frame": annotated_frame,
                "guidance": None,
                "stage": self.guidance_stage,
                "instruction": "YOLO model not loaded",
                "detected_objects": [],
                "hand_detected": len(detected_hands) > 0
            }
        
        # Run YOLO detection with tracking (always show boxes)
        # Use the device determined during model initialization (optimized for M1 Mac)
        device = self.model_service.get_yolo_device()
        
        try:
            yolo_results = yolo_model.track(
                frame,
                persist=True,
                conf=self.CONFIDENCE_THRESHOLD,
                verbose=False,
                device=device,  # Use device determined during initialization (MPS on M1/M2 if available)
                tracker="botsort.yaml"
            )
            # Plot YOLO boxes on frame
            annotated_frame = yolo_results[0].plot(line_width=2)
        except Exception as e:
            print(f"Error running YOLO tracking: {e}")
            # Fallback: use predict instead of track
            try:
                yolo_results = yolo_model.predict(
                    frame,
                    conf=self.CONFIDENCE_THRESHOLD,
                    verbose=False,
                    device=device
                )
                annotated_frame = yolo_results[0].plot(line_width=2)
            except Exception as e2:
                print(f"Error with YOLO predict fallback: {e2}")
                # Last resort: just return the frame
                annotated_frame = frame.copy()
        
        # Detect hands (if hand model is available)
        detected_hands = []
        if hand_model is not None:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_results = hand_model.process(rgb_frame)
                
                if mp_results.multi_hand_landmarks:
                    for hand_landmarks in mp_results.multi_hand_landmarks:
                        h, w, _ = frame.shape
                        coords = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
                        x_min, y_min = np.min(coords, axis=0)
                        x_max, y_max = np.max(coords, axis=0)
                        current_hand_box = [int(x_min * w), int(y_min * h), int(x_max * w), int(y_max * h)]
                        detected_hands.append({'box': current_hand_box})
                        mp.solutions.drawing_utils.draw_landmarks(
                            annotated_frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                        )
            except Exception as e:
                print(f"Error processing hand detection: {e}")
                detected_hands = []
        
        # Get detected objects
        detected_objects = {}
        if yolo_results[0].boxes is not None and len(yolo_results[0].boxes) > 0:
            for box, cls in zip(yolo_results[0].boxes.xyxy, yolo_results[0].boxes.cls):
                obj_name = yolo_model.names[int(cls)]
                detected_objects[obj_name] = box.cpu().numpy().tolist()
        
        # Process guidance logic (only when task is active)
        should_update = (
            time.time() - self.last_guidance_time > self.GUIDANCE_UPDATE_INTERVAL_SEC and
            self.guidance_stage not in ['IDLE', 'DONE', 'AWAITING_FEEDBACK'] and
            len(self.target_objects) > 0 and  # Only update if we have a task
            self.guidance_stage != 'IDLE'  # Don't update if idle
        )
        
        if should_update:
            await self._update_guidance(frame, detected_objects, detected_hands, yolo_model)
        
        # Check if hand has reached object and trigger confirmation (similar to Merged_System)
        # This check runs every frame to immediately detect when stage changes to confirmation
        # In Merged_System, this happens after speech completes, but we check every frame for responsiveness
        if self.guidance_stage in ['CONFIRMING_PICKUP', 'VERIFYING_OBJECT']:
            # Hand has reached the object - show confirmation message immediately
            primary_target = self.target_objects[0] if self.target_objects else "object"
            confirmation_text = f"Your hand is at the {'object' if self.guidance_stage == 'VERIFYING_OBJECT' else primary_target}. Can you confirm if this is correct? Please use the Yes or No buttons."
            if self.current_instruction != confirmation_text:
                print(f"✓ Hand reached object! Transitioning to AWAITING_FEEDBACK stage.")
                self._update_instruction(confirmation_text)
                self.guidance_stage = 'AWAITING_FEEDBACK'
        
        # Draw target object box (highlight in yellow/cyan)
        if self.found_object_location and self.guidance_stage == 'GUIDING_TO_PICKUP':
            box = self.found_object_location
            cv2.rectangle(
                annotated_frame,
                (int(box[0]), int(box[1])),
                (int(box[2]), int(box[3])),
                (0, 255, 255),  # Yellow in BGR
                3
            )
        
        # Draw guidance text on frame
        custom_font = load_font(self.FONT_PATH, size=24)
        annotated_frame = draw_guidance_on_frame(annotated_frame, self.current_instruction, custom_font)
        
        return {
            "annotated_frame": annotated_frame,
            "guidance": {
                "instruction": self.current_instruction,
                "stage": self.guidance_stage
            },
            "stage": self.guidance_stage,
            "instruction": self.current_instruction,
            "detected_objects": [
                {"name": name, "box": box}
                for name, box in detected_objects.items()
            ],
            "hand_detected": len(detected_hands) > 0,
            "object_location": self.found_object_location,
            "hand_location": detected_hands[0]['box'] if detected_hands else None
        }
    
    async def _update_guidance(self, frame: np.ndarray, detected_objects: Dict, detected_hands: List, yolo_model):
        """Update guidance based on current state"""
        primary_target = self.target_objects[0] if self.target_objects else None
        
        if self.guidance_stage == 'FINDING_OBJECT':
            found_target_name = next(
                (target for target in self.target_objects if target in detected_objects),
                None
            )
            if found_target_name:
                self.found_object_location = detected_objects[found_target_name]
                verification_needed = (primary_target, found_target_name) in self.verification_pairs
                if verification_needed:
                    instruction = f"I see something that could be the {primary_target}, but it looks like a {found_target_name}. I will guide you to it for verification."
                    self._update_instruction(instruction)
                    self.next_stage_after_guiding = 'VERIFYING_OBJECT'
                    self.guidance_stage = 'GUIDING_TO_PICKUP'
                else:
                    location_desc = self._describe_location_detailed(self.found_object_location, frame.shape)
                    instruction = f"Great, I see the {primary_target} {location_desc}. I will now guide your hand to it."
                    self._update_instruction(instruction)
                    self.next_stage_after_guiding = 'CONFIRMING_PICKUP'
                    self.guidance_stage = 'GUIDING_TO_PICKUP'
            else:
                # Only update instruction if it's different to avoid duplicates
                new_instruction = f"I am looking for the {primary_target}. Please scan the area."
                if self.current_instruction != new_instruction:
                    self._update_instruction(new_instruction)
        
        elif self.guidance_stage == 'GUIDING_TO_PICKUP':
            target_box = self.found_object_location
            if not detected_hands:
                self._update_instruction("I can't see your hand. Please bring it into view.")
            else:
                # Check if object is still visible
                object_still_visible = any(
                    target in detected_objects for target in self.target_objects
                )
                
                # Find closest hand
                target_center = self._get_box_center(target_box)
                closest_hand = min(
                    detected_hands,
                    key=lambda h: np.linalg.norm(
                        np.array(target_center) - np.array(self._get_box_center(h['box']))
                    )
                )
                
                # Check if hand has reached the object (using same logic as Merged_System)
                reached, distance, iou, overlap_ratio = self._is_hand_at_object(
                    closest_hand['box'], target_box, frame.shape
                )
                
                if reached:
                    # Calculate depth ratio for logging
                    hand_area = (closest_hand['box'][2] - closest_hand['box'][0]) * (closest_hand['box'][3] - closest_hand['box'][1])
                    obj_area = (target_box[2] - target_box[0]) * (target_box[3] - target_box[1])
                    depth_ratio_log = obj_area / hand_area if hand_area > 0 else 0
                    
                    print(f"✓✓✓ SUCCESS: Hand reached object!")
                    print(f"   Distance: {distance:.1f}px (threshold: <{self.DISTANCE_THRESHOLD_PIXELS}px)")
                    print(f"   IOU: {iou:.3f} (threshold: >{self.OCCLUSION_IOU_THRESHOLD})")
                    print(f"   Overlap ratio: {overlap_ratio:.3f} (threshold: >0.4)")
                    print(f"   Depth ratio: {depth_ratio_log:.2f} (valid range: 0.3-3.0)")
                    print(f"   Transitioning to stage: {self.next_stage_after_guiding}")
                    self.guidance_stage = self.next_stage_after_guiding
                elif not object_still_visible and self.object_last_seen_time is not None:
                    time_since_disappeared = time.time() - self.object_last_seen_time
                    if time_since_disappeared > 1.0:
                        if not self.object_disappeared_notified:
                            hand_center = self._get_box_center(closest_hand['box'])
                            last_object_center = self._get_box_center(target_box)
                            dist_to_last_location = self._calculate_distance(hand_center, last_object_center)
                            
                            if dist_to_last_location < self.DISTANCE_THRESHOLD_PIXELS * 1.5:
                                self.guidance_stage = self.next_stage_after_guiding
                                self.object_disappeared_notified = False
                            else:
                                self._update_instruction(
                                    f"I can't see the {primary_target} anymore. If you have it, great! Otherwise, please scan the area again."
                                )
                                self.object_disappeared_notified = True
                else:
                    if object_still_visible:
                        self.object_last_seen_time = time.time()
                        self.object_disappeared_notified = False
                        
                        # Update target box
                        for target in self.target_objects:
                            if target in detected_objects:
                                self.found_object_location = detected_objects[target]
                                target_box = detected_objects[target]
                                break
                    
                    # Generate directional guidance using fast rule-based approach
                    # (LLM is too slow for real-time hand guidance)
                    guidance = self._generate_rule_based_guidance(
                        closest_hand['box'], target_box, primary_target, distance, frame.shape
                    )
                    self._update_instruction(guidance)
    
    def _update_instruction(self, new_instruction: str):
        """Update current instruction"""
        self.last_guidance_time = time.time()
        if self.current_instruction != new_instruction:
            self.current_instruction = new_instruction
            # Only add to history if it's not a duplicate of the last entry
            if not self.instruction_history or self.instruction_history[0] != new_instruction:
                self.instruction_history.insert(0, new_instruction)
                # Keep only last 20 instructions
                self.instruction_history = self.instruction_history[:20]
    
    def _describe_location_detailed(self, box: List[float], frame_shape: Tuple) -> str:
        """Describe object location in detail (corrected for front-facing camera mirror effect)"""
        h, w = frame_shape[:2]
        center_x, center_y = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        # INVERTED left/right for front-facing camera
        # Object on left of frame = actually on user's right, and vice versa
        h_pos = "to your right" if center_x < w / 3 else "to your left" if center_x > 2 * w / 3 else "in front of you"
        v_pos = "in the upper part" if center_y < h / 3 else "in the lower part" if center_y > 2 * h / 3 else "at chest level"
        # Depth estimation from box size (larger = closer to camera = farther from user's body)
        relative_area = ((box[2] - box[0]) * (box[3] - box[1])) / (w * h)
        dist = "and is farther from your body" if relative_area > 0.1 else "and appears to be within reach" if relative_area > 0.03 else "and is closer to your body"
        return f"{v_pos} and {h_pos}, {dist}" if h_pos != "in front of you" else f"{h_pos}, {v_pos}, {dist}"
    
    def _get_distance_description(self, distance_pixels: float, frame_width: int) -> str:
        """Convert pixel distance to descriptive terms"""
        relative_distance = distance_pixels / frame_width
        if relative_distance < 0.05:
            return "very close, almost touching"
        elif relative_distance < 0.1:
            return "very near"
        elif relative_distance < 0.15:
            return "close"
        elif relative_distance < 0.25:
            return "nearby"
        else:
            return "some distance away"
    
    def _estimate_depth(self, hand_box: List[float], object_box: List[float], frame_shape: Tuple) -> str:
        """Estimate relative depth between hand and object based on bounding box sizes.
        
        For FRONT-FACING camera (webcam facing user):
        - Larger bounding box = closer to camera = FARTHER from user's body
        - Smaller bounding box = farther from camera = CLOSER to user's body
        """
        h, w = frame_shape[:2]
        frame_area = w * h
        
        # Calculate bounding box areas
        hand_area = (hand_box[2] - hand_box[0]) * (hand_box[3] - hand_box[1])
        object_area = (object_box[2] - object_box[0]) * (object_box[3] - object_box[1])
        
        # Normalize relative to frame
        hand_relative = hand_area / frame_area
        object_relative = object_area / frame_area
        
        # Calculate depth ratio
        if hand_relative <= 0:
            return "Unable to estimate depth - hand not clearly visible."
        
        depth_ratio = object_relative / hand_relative
        
        # Interpret the ratio (corrected for front-facing camera)
        if depth_ratio < 0.3:
            return "The object is much closer to your body than your hand. Pull your hand back towards yourself."
        elif depth_ratio < 0.5:
            return "The object is closer to your body. Move your hand back towards you."
        elif depth_ratio < 0.7:
            return "The object is slightly closer to your body. Bring your hand back a bit."
        elif depth_ratio < 1.3:
            return "Your hand and the object are at roughly the same distance from your body. Focus on left/right and up/down alignment."
        elif depth_ratio < 2.0:
            return "The object is slightly farther out than your hand. Extend your hand outward a bit."
        elif depth_ratio < 3.0:
            return "The object is farther from your body than your hand. Reach outward."
        else:
            return "The object is much farther out. Extend your arm forward, away from your body."
    
    def _generate_rule_based_guidance(self, hand_box: List[float], object_box: List[float], 
                                       target_name: str, distance: float, frame_shape: Tuple) -> str:
        """Generate simple directional guidance without LLM, including depth estimation"""
        h, w = frame_shape[:2]
        
        hand_center = self._get_box_center(hand_box)
        object_center = self._get_box_center(object_box)
        
        # Calculate direction from hand to object
        dx = object_center[0] - hand_center[0]  # positive = object is to the right
        dy = object_center[1] - hand_center[1]  # positive = object is below
        
        # Calculate bounding box areas for depth estimation
        # Larger box = closer to camera, smaller box = farther from camera
        hand_area = (hand_box[2] - hand_box[0]) * (hand_box[3] - hand_box[1])
        object_area = (object_box[2] - object_box[0]) * (object_box[3] - object_box[1])
        
        # Normalize areas relative to frame
        frame_area = w * h
        hand_relative_size = hand_area / frame_area
        object_relative_size = object_area / frame_area
        
        # Estimate depth difference based on relative sizes
        # With a FRONT-FACING camera (webcam/selfie style):
        # - Object appears smaller = farther from camera = CLOSER to user's body
        # - Object appears larger = closer to camera = FARTHER from user's body
        depth_ratio = object_relative_size / hand_relative_size if hand_relative_size > 0 else 1.0
        
        # Determine primary direction(s)
        directions = []
        
        # Depth direction (forward/back) - adjusted for front-facing camera
        if depth_ratio < 0.4:
            # Object is much smaller = farther from camera = closer to user's body
            # User needs to pull hand BACK towards their body
            directions.append("back towards you")
        elif depth_ratio > 2.5:
            # Object is much larger = closer to camera = farther from user's body
            # User needs to reach OUT/FORWARD away from their body
            directions.append("forward away from you")
        
        # Horizontal direction (INVERTED for front-facing camera mirror effect)
        if abs(dx) > w * 0.05:  # More than 5% of frame width
            if dx > 0:
                # Object appears on right side of frame = actually on user's LEFT
                directions.append("left")
            else:
                # Object appears on left side of frame = actually on user's RIGHT
                directions.append("right")
        
        # Vertical direction
        if abs(dy) > h * 0.05:  # More than 5% of frame height
            if dy > 0:
                directions.append("down")
            else:
                directions.append("up")
        
        # Get distance description
        distance_desc = self._get_distance_description(distance, w)
        
        # Build instruction with depth context (for front-facing camera)
        depth_context = ""
        if depth_ratio < 0.4:
            depth_context = f" The {target_name} is closer to your body than your hand."
        elif depth_ratio > 2.5:
            depth_context = f" The {target_name} is farther out, away from your body."
        elif 0.7 < depth_ratio < 1.4:
            depth_context = f" Your hand and the {target_name} are at a similar distance from your body."
        
        # Build final instruction
        if not directions:
            return f"Your hand is {distance_desc} the {target_name}. Keep reaching forward.{depth_context}"
        elif len(directions) == 1:
            return f"Move your hand {directions[0]}. The {target_name} is {distance_desc}.{depth_context}"
        else:
            direction_str = ", ".join(directions[:-1]) + " and " + directions[-1]
            return f"Move your hand {direction_str}. The {target_name} is {distance_desc}.{depth_context}"
    
    def _get_box_center(self, box: List[float]) -> List[float]:
        """Calculate center of a bounding box"""
        return [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]
    
    def _calculate_distance(self, point1: List[float], point2: List[float]) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def _calculate_iou(self, boxA: List[float], boxB: List[float]) -> float:
        """Calculate Intersection over Union"""
        xA, yA = max(boxA[0], boxB[0]), max(boxA[1], boxB[1])
        xB, yB = min(boxA[2], boxB[2]), min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        denominator = float(boxAArea + boxBArea - interArea)
        return interArea / denominator if denominator != 0 else 0
    
    def _calculate_box_overlap_area(self, hand_box: List[float], object_box: List[float]) -> float:
        """Calculate overlapping area between hand and object boxes"""
        xA = max(hand_box[0], object_box[0])
        yA = max(hand_box[1], object_box[1])
        xB = min(hand_box[2], object_box[2])
        yB = min(hand_box[3], object_box[3])
        if xB < xA or yB < yA:
            return 0
        return (xB - xA) * (yB - yA)
    
    def _is_hand_at_object(self, hand_box: List[float], object_box: List[float], frame_shape: Tuple) -> Tuple[bool, float, float, float]:
        """Determine if hand has reached the object, including depth similarity check"""
        h, w = frame_shape[:2]
        frame_area = w * h
        
        hand_center = self._get_box_center(hand_box)
        object_center = self._get_box_center(object_box)
        
        distance = self._calculate_distance(hand_center, object_center)
        iou = self._calculate_iou(hand_box, object_box)
        overlap_area = self._calculate_box_overlap_area(hand_box, object_box)
        object_area = (object_box[2] - object_box[0]) * (object_box[3] - object_box[1])
        overlap_ratio = overlap_area / object_area if object_area > 0 else 0
        
        # Calculate depth similarity based on bounding box sizes
        hand_area = (hand_box[2] - hand_box[0]) * (hand_box[3] - hand_box[1])
        
        # Depth ratio: how similar are the apparent sizes?
        # Ratio close to 1.0 = similar depth
        depth_ratio = (object_area / hand_area) if hand_area > 0 else 0
        
        # Depth is considered "similar" if ratio is within acceptable range
        # Range can be tightened after failed attempts (via DEPTH_STRICTNESS_MULTIPLIER)
        strictness = getattr(self, 'DEPTH_STRICTNESS_MULTIPLIER', 1.0)
        min_depth_ratio = 0.3 / strictness  # Tighter when strictness < 1
        max_depth_ratio = 3.0 * strictness  # Tighter when strictness < 1
        
        # After failed attempts, require stricter depth matching
        if strictness < 1.0:
            # Stricter range: 0.43 to 2.1 when strictness is 0.7
            min_depth_ratio = 0.3 / strictness
            max_depth_ratio = 3.0 * strictness
        
        depth_similar = min_depth_ratio <= depth_ratio <= max_depth_ratio
        
        # 2D proximity conditions (existing logic)
        proximity_2d = (
            distance < self.DISTANCE_THRESHOLD_PIXELS or
            iou > self.OCCLUSION_IOU_THRESHOLD or
            overlap_ratio > 0.4
        )
        
        # Object is truly "reached" only if both 2D proximity AND depth are satisfied
        reached = proximity_2d and depth_similar
        
        # Debug logging for depth check
        if proximity_2d and not depth_similar:
            print(f"⚠️  2D overlap detected but depth mismatch! Depth ratio: {depth_ratio:.2f} (need 0.3-3.0)")
        
        return reached, distance, iou, overlap_ratio
    
    async def handle_feedback(self, confirmed: bool, feedback_text: Optional[str] = None) -> Dict[str, Any]:
        """Handle user feedback with adaptive behavior after failed attempts"""
        if confirmed:
            # Success! Reset failed attempts counter
            self.failed_attempts = 0
            self.last_failed_reason = None
            self._update_instruction("Great, task complete!")
            self.guidance_stage = 'DONE'
            self.task_done_displayed = True
            return {
                "status": "success",
                "message": "Task completed successfully",
                "next_stage": "DONE"
            }
        else:
            # Track failed attempts
            self.failed_attempts += 1
            self.found_object_location = None
            
            primary_target = self.target_objects[0] if self.target_objects else "object"
            
            # Provide adaptive guidance based on number of failed attempts
            if self.failed_attempts == 1:
                # First failure - likely depth issue or slight misalignment
                instruction = (
                    f"Okay, let me try again. This might have been a depth issue - "
                    f"make sure your hand is actually touching the {primary_target}, not just passing in front of or behind it. "
                    f"I'll guide you more carefully this time."
                )
                self.last_failed_reason = "depth"
                # Tighten depth requirements for next attempt
                self.DEPTH_STRICTNESS_MULTIPLIER = 0.7  # More strict depth matching
                
            elif self.failed_attempts == 2:
                # Second failure - might be misclassification
                instruction = (
                    f"Let me scan again more carefully. The detected object might not have been the correct {primary_target}. "
                    f"Please make sure the {primary_target} is clearly visible in the camera."
                )
                self.last_failed_reason = "misclassification"
                # Increase confidence threshold temporarily
                self.CONFIDENCE_THRESHOLD = min(0.7, self.CONFIDENCE_THRESHOLD + 0.1)
                
            elif self.failed_attempts >= 3:
                # Multiple failures - object might be gone or very difficult to detect
                instruction = (
                    f"Having trouble finding the {primary_target}. It may have been moved or is hard to detect. "
                    f"Try repositioning the {primary_target} so it's clearly visible, or check if it's still there. "
                    f"I'll scan the area again."
                )
                self.last_failed_reason = "unknown"
                # Reset thresholds but keep tracking
                self.CONFIDENCE_THRESHOLD = 0.5
                if hasattr(self, 'DEPTH_STRICTNESS_MULTIPLIER'):
                    del self.DEPTH_STRICTNESS_MULTIPLIER
            
            self._update_instruction(instruction)
            self.guidance_stage = 'FINDING_OBJECT'
            
            print(f"📝 Feedback: NO (attempt #{self.failed_attempts}, suspected reason: {self.last_failed_reason})")
            
            return {
                "status": "success",
                "message": f"Restarting search (attempt #{self.failed_attempts + 1})",
                "next_stage": "FINDING_OBJECT",
                "failed_attempts": self.failed_attempts,
                "suspected_reason": self.last_failed_reason
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current activity guide status"""
        return {
            "stage": self.guidance_stage,
            "current_instruction": self.current_instruction,
            "target_objects": self.target_objects,
            "instruction_history": self.instruction_history[-10:]  # Last 10 instructions
        }
    
    def reset(self):
        """Reset activity guide state"""
        self.guidance_stage = "IDLE"
        self.current_instruction = "Start the camera and enter a task."
        self.instruction_history = []
        self.target_objects = []
        self.found_object_location = None
        self.last_guidance_time = 0
        self.task_done_displayed = False
        self.object_last_seen_time = None
        self.object_disappeared_notified = False
        
        # Reset feedback tracking and adaptive thresholds
        self.failed_attempts = 0
        self.last_failed_reason = None
        self.CONFIDENCE_THRESHOLD = 0.5
        if hasattr(self, 'DEPTH_STRICTNESS_MULTIPLIER'):
            del self.DEPTH_STRICTNESS_MULTIPLIER

