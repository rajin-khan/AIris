"""
Model Service - Handles loading and managing ML models
"""

import os
import torch
from ultralytics import YOLO
import mediapipe as mp
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import Optional, Tuple
import yaml
import cv2

class ModelService:
    def __init__(self):
        self.yolo_model: Optional[YOLO] = None
        self.hand_model: Optional[mp.solutions.hands.Hands] = None
        self.vision_processor: Optional[BlipProcessor] = None
        self.vision_model: Optional[BlipForConditionalGeneration] = None
        self.device: str = "cpu"
        self.yolo_device: str = "cpu"  # Device for YOLO inference
        self.prompts: dict = {}
        self.models_loaded = False
        
        # Constants
        self.YOLO_MODEL_PATH = os.getenv('YOLO_MODEL_PATH', 'yolov8s.pt')
        self.CONFIG_PATH = os.getenv('CONFIG_PATH', 'config.yaml')
    
    async def initialize(self):
        """Initialize all models"""
        if self.models_loaded:
            return
        
        print("Loading models...")
        
        # Load prompts
        self._load_prompts()
        
        # Load YOLO model
        await self._load_yolo_model()
        
        # Load hand detection model
        await self._load_hand_model()
        
        # Vision model will be loaded lazily when needed
        self.models_loaded = True
        print("Models loaded successfully")
    
    def _load_prompts(self):
        """Load prompts from config file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', self.CONFIG_PATH)
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.prompts = yaml.safe_load(f)
            else:
                # Default prompts if config not found
                self.prompts = {
                    'activity_guide': {
                        'object_extraction': "From the user's request: '{goal}', identify the single, primary physical object that is being acted upon. Respond ONLY with a Python list of names for it.",
                        'guidance_system': "You are an AI assistant for a blind person. Your instructions must be safe, clear, concise, and based on their perspective.",
                        'guidance_user': "The user's hand is {hand_location}. The '{primary_target}' is at {object_location}. Guide their hand towards the object."
                    },
                    'scene_description': {
                        'summarization_system': "You are a motion analysis expert. Infer the single most likely action that connects observations.",
                        'summarization_user': "Observations: {observations}",
                        'safety_alert_user': "Analyze for potential harm, distress, or accidents. Respond with only 'HARMFUL' if it contains events like falling, crashing, fire, or injury. Otherwise, respond only 'SAFE'. Event: '{summary}'"
                    }
                }
        except Exception as e:
            print(f"Error loading prompts: {e}")
            self.prompts = {}
    
    async def _load_yolo_model(self):
        """Load YOLO object detection model - optimized for macOS ARM (M1/M2)"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), '..', self.YOLO_MODEL_PATH)
            if os.path.exists(model_path):
                self.yolo_model = YOLO(model_path)
            else:
                # Try to download or use default
                self.yolo_model = YOLO('yolov8s.pt')
            
            # Verify model is actually loaded by doing a test inference
            import numpy as np
            import torch
            test_frame = np.zeros((640, 640, 3), dtype=np.uint8)
            
            # Try MPS first on Mac M1/M2, with fallback to CPU
            device = 'cpu'  # Default
            if torch.backends.mps.is_available():
                try:
                    # Test MPS availability
                    _ = self.yolo_model.predict(test_frame, verbose=False, device='mps')
                    device = 'mps'
                    print(f"YOLO model loaded and verified (using MPS - Apple Silicon GPU)")
                except Exception as mps_error:
                    # MPS might have issues with certain operations, fallback to CPU
                    print(f"MPS test failed: {mps_error}")
                    print("Falling back to CPU for YOLO inference")
                    try:
                        _ = self.yolo_model.predict(test_frame, verbose=False, device='cpu')
                        device = 'cpu'
                        print(f"YOLO model loaded and verified (using CPU)")
                    except Exception as cpu_error:
                        print(f"CPU test also failed: {cpu_error}")
                        raise cpu_error
            else:
                # No MPS available, use CPU
                _ = self.yolo_model.predict(test_frame, verbose=False, device='cpu')
                device = 'cpu'
                print(f"YOLO model loaded and verified (using CPU)")
            
            # Store the working device for later use
            self.yolo_device = device
            
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            import traceback
            traceback.print_exc()
            self.yolo_model = None
            self.yolo_device = 'cpu'
    
    async def _load_hand_model(self):
        """Load MediaPipe hand detection model with aggressive M1 Mac compatibility fixes"""
        import io
        import numpy as np
        import sys
        import os
        from contextlib import redirect_stderr, redirect_stdout
        
        # Set environment variables to potentially help with M1 compatibility
        os.environ.setdefault('GLOG_minloglevel', '2')  # Suppress glog warnings
        
        mp_hands = mp.solutions.hands
        
        # List of strategies to try, ordered by likelihood of success on M1
        strategies = [
            {
                'name': 'model_complexity=0, static_image_mode=False',
                'config': {
                    'static_image_mode': False,
                    'max_num_hands': 2,
                    'min_detection_confidence': 0.5,
                    'min_tracking_confidence': 0.5,
                    'model_complexity': 0
                }
            },
            {
                'name': 'model_complexity=0, static_image_mode=True',
                'config': {
                    'static_image_mode': True,
                    'max_num_hands': 2,
                    'min_detection_confidence': 0.5,
                    'min_tracking_confidence': 0.5,
                    'model_complexity': 0
                }
            },
            {
                'name': 'model_complexity=1, static_image_mode=False',
                'config': {
                    'static_image_mode': False,
                    'max_num_hands': 2,
                    'min_detection_confidence': 0.5,
                    'min_tracking_confidence': 0.5,
                    'model_complexity': 1
                }
            },
            {
                'name': 'minimal config (single hand)',
                'config': {
                    'static_image_mode': False,
                    'max_num_hands': 1,
                    'min_detection_confidence': 0.3,
                    'min_tracking_confidence': 0.3,
                    'model_complexity': 0
                }
            }
        ]
        
        for strategy in strategies:
            try:
                # Completely suppress stderr and stdout during initialization
                # MediaPipe's internal validation errors on M1 are often false positives
                stderr_buffer = io.StringIO()
                stdout_buffer = io.StringIO()
                
                # Create a custom stderr that filters out MediaPipe validation errors
                class FilteredStderr:
                    def __init__(self, original):
                        self.original = original
                        self.buffer = io.StringIO()
                    
                    def write(self, text):
                        # Filter out known MediaPipe validation errors that are false positives on M1
                        if any(keyword in text.lower() for keyword in [
                            'validatedgraphconfig',
                            'imagetotensorcalculator',
                            'constantsidepacketcalculator',
                            'splittensorvectorcalculator',
                            'ret_check failure',
                            'output tensor range is required'
                        ]):
                            # These are often false positives on Apple Silicon
                            return
                        self.original.write(text)
                    
                    def flush(self):
                        self.original.flush()
                
                # Temporarily replace stderr with filtered version
                original_stderr = sys.stderr
                filtered_stderr = FilteredStderr(original_stderr)
                sys.stderr = filtered_stderr
                
                try:
                    # Try to initialize MediaPipe Hands
                    self.hand_model = mp_hands.Hands(**strategy['config'])
                    
                    # Test if it actually works by processing a dummy frame
                    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    test_rgb = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
                    
                    # Process with error handling
                    result = self.hand_model.process(test_rgb)
                    
                    # If we get here without exception, the model works!
                    print(f"✓ Hand detection model loaded successfully ({strategy['name']})")
                    return
                    
                finally:
                    # Restore original stderr
                    sys.stderr = original_stderr
                    
            except Exception as e:
                # Clean up if model was partially created
                if self.hand_model is not None:
                    try:
                        self.hand_model.close()
                    except:
                        pass
                    self.hand_model = None
                
                # Continue to next strategy
                error_msg = str(e)
                # Don't print validation errors - they're expected on M1
                if 'ValidatedGraphConfig' not in error_msg and 'ImageToTensorCalculator' not in error_msg:
                    print(f"  Strategy '{strategy['name']}' failed: {error_msg[:100]}")
                continue
        
        # If all strategies failed, try one more time with complete error suppression
        # Sometimes MediaPipe works despite throwing initialization errors
        print("Attempting final initialization with complete error suppression...")
        try:
            # Create a null device to completely discard output
            class NullDevice:
                def write(self, s):
                    pass
                def flush(self):
                    pass
            
            original_stderr = sys.stderr
            sys.stderr = NullDevice()
            
            try:
                self.hand_model = mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                    model_complexity=0
                )
                
                # Test with a real frame-like input
                test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                test_rgb = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
                result = self.hand_model.process(test_rgb)
                
                print("✓ Hand detection model loaded (despite initialization warnings)")
                return
            finally:
                sys.stderr = original_stderr
                
        except Exception as final_error:
            if self.hand_model is not None:
                try:
                    self.hand_model.close()
                except:
                    pass
            self.hand_model = None
        
        # All strategies failed
        print("\n⚠️  Could not initialize MediaPipe hand tracking model")
        print("   This is a known compatibility issue on Apple Silicon (M1/M2) Macs")
        print("   The app will continue to work, but hand tracking features will be disabled")
        print("   Activity Guide mode will still work with object detection only")
        print("\n   To try fixing this manually:")
        print("   1. Try: pip install --upgrade mediapipe")
        print("   2. Or try: pip install mediapipe-silicon (if available)")
        print("   3. Check MediaPipe GitHub issues for latest M1 fixes")
        self.hand_model = None
    
    def _get_device(self) -> str:
        """Get the best available device for inference"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"  # Use MPS on Mac M1/M2 for better performance
        else:
            return "cpu"
    
    async def load_vision_model(self) -> Tuple[BlipProcessor, BlipForConditionalGeneration, str]:
        """Load BLIP vision model (lazy loading)"""
        if self.vision_model is not None:
            return self.vision_processor, self.vision_model, self.device
        
        print("Initializing BLIP vision model...")
        self.device = self._get_device()
        
        print(f"BLIP using device: {self.device}")
        self.vision_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        self.vision_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-large"
        ).to(self.device)
        
        return self.vision_processor, self.vision_model, self.device
    
    def get_yolo_model(self) -> Optional[YOLO]:
        """Get YOLO model"""
        return self.yolo_model
    
    def get_hand_model(self) -> Optional[mp.solutions.hands.Hands]:
        """Get hand detection model"""
        return self.hand_model
    
    def get_yolo_device(self) -> str:
        """Get the device YOLO should use for inference"""
        return getattr(self, 'yolo_device', 'cpu')
    
    def get_prompts(self) -> dict:
        """Get prompts configuration"""
        return self.prompts
    
    def are_models_loaded(self) -> bool:
        """Check if models are loaded"""
        # YOLO is required, hand model is optional (for Activity Guide)
        return self.models_loaded and self.yolo_model is not None
    
    async def cleanup(self):
        """Cleanup model resources"""
        if self.vision_model is not None:
            del self.vision_model
            del self.vision_processor
            self.vision_model = None
            self.vision_processor = None
        
        if self.hand_model is not None:
            self.hand_model.close()
            self.hand_model = None
        
        self.yolo_model = None
        self.models_loaded = False

