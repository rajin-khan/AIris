"""
Camera Service - Handles camera operations
"""

import cv2
import asyncio
from typing import Optional
import time
from collections import deque

class CameraService:
    def __init__(self):
        self.vid_cap: Optional[cv2.VideoCapture] = None
        self.is_running_flag = False
        self.last_frame = None
        self.last_timestamp = None
        self.source_type = "webcam"  # "webcam" or "esp32"
        self.ip_address = ""
        # Frame buffer for ESP32 to smooth out frame rate
        self.frame_buffer = deque(maxlen=2)  # Keep last 2 frames
    
    async def set_config(self, source_type: str, ip_address: str = ""):
        """Set camera configuration"""
        self.source_type = source_type
        self.ip_address = ip_address
        # If running, we should stop so the next start uses the new config
        if self.is_running():
            await self.stop()
    
    async def start(self) -> bool:
        """Start the camera"""
        if self.is_running():
            return True
        
        if self.source_type == "esp32":
            if not self.ip_address:
                print("ESP32 IP not set")
                return False
            
            # ESP32-CAM stream URL
            stream_url = f"http://{self.ip_address}:80/stream"
            print(f"Connecting to ESP32 stream: {stream_url}")
            
            try:
                # Run blocking VideoCapture in a thread
                loop = asyncio.get_event_loop()
                self.vid_cap = await loop.run_in_executor(None, cv2.VideoCapture, stream_url)
                
                if self.vid_cap.isOpened():
                    # Optimize ESP32 stream settings for better performance
                    # Set buffer size to 1 to reduce latency (always get latest frame)
                    self.vid_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    # Set frame width/height if needed (ESP32 typically sends QVGA)
                    # Don't set these as ESP32 controls the resolution
                    
                    # Give it a moment to connect and read first frame
                    await asyncio.sleep(0.5)
                    
                    ret, test_frame = self.vid_cap.read()
                    if ret and test_frame is not None:
                        self.is_running_flag = True
                        self.frame_buffer.clear()
                        print("Successfully connected to ESP32 stream")
                        # Start background frame reader for ESP32
                        asyncio.create_task(self._esp32_frame_reader())
                        return True
                    else:
                        print("Connected to stream but failed to read frame")
                        self.vid_cap.release()
                else:
                    print("Failed to open ESP32 stream")
            except Exception as e:
                print(f"Error connecting to ESP32: {e}")
                if self.vid_cap:
                    self.vid_cap.release()
            
            return False
            
        else:
            # Try multiple camera indices (Webcam mode)
            for camera_index in [0, 1, 2]:
                print(f"Trying webcam index {camera_index}...")
                self.vid_cap = cv2.VideoCapture(camera_index)
                await asyncio.sleep(0.5)  # Give camera time to initialize
                
                if self.vid_cap.isOpened():
                    ret, test_frame = self.vid_cap.read()
                    if ret and test_frame is not None:
                        self.is_running_flag = True
                        print(f"Successfully connected to webcam {camera_index}")
                        return True
                    else:
                        self.vid_cap.release()
            
            return False
    
    async def stop(self):
        """Stop the camera"""
        self.is_running_flag = False
        if self.vid_cap is not None:
            self.vid_cap.release()
            self.vid_cap = None
        self.last_frame = None
        self.frame_buffer.clear()
    
    async def _esp32_frame_reader(self):
        """Background task to continuously read frames from ESP32 stream"""
        while self.is_running() and self.source_type == "esp32" and self.vid_cap is not None:
            try:
                # Read frame in executor to avoid blocking
                ret, frame = await asyncio.get_event_loop().run_in_executor(
                    None, self.vid_cap.read
                )
                if ret and frame is not None:
                    # Update buffer and last frame (no lock needed for simple append)
                    self.frame_buffer.append((frame, time.time()))
                    self.last_frame = frame
                    self.last_timestamp = time.time()
                # Small delay to prevent CPU spinning and allow other tasks
                await asyncio.sleep(0.01)  # ~100 FPS max read rate
            except Exception as e:
                print(f"Error reading ESP32 frame: {e}")
                await asyncio.sleep(0.1)
    
    async def get_frame(self) -> Optional:
        """Get the latest frame from camera"""
        if not self.is_running():
            return None
        
        # For ESP32, use buffered frames for smoother playback
        if self.source_type == "esp32":
            if self.frame_buffer:
                # Get the most recent frame from buffer
                frame, timestamp = self.frame_buffer[-1]
                self.last_frame = frame
                self.last_timestamp = timestamp
                return frame
            # Fallback to direct read if buffer is empty
            if self.vid_cap:
                ret, frame = await asyncio.get_event_loop().run_in_executor(
                    None, self.vid_cap.read
                )
                if ret and frame is not None:
                    self.last_frame = frame
                    self.last_timestamp = time.time()
                    return frame
            return None
        else:
            # For webcam, read directly
            ret, frame = await asyncio.get_event_loop().run_in_executor(
                None, self.vid_cap.read
            )
            if ret and frame is not None:
                self.last_frame = frame
                self.last_timestamp = time.time()
                return frame
            return None
    
    def is_running(self) -> bool:
        """Check if camera is running"""
        return self.is_running_flag and self.vid_cap is not None and self.vid_cap.isOpened()
    
    def is_available(self) -> bool:
        """Check if camera is available"""
        if self.source_type == "esp32":
            # For ESP32, availability depends on IP being set
            return bool(self.ip_address)
        
        # Try to open a test capture for webcam
        test_cap = cv2.VideoCapture(0)
        if test_cap.isOpened():
            test_cap.release()
            return True
        return False
    
    def get_timestamp(self) -> float:
        """Get the timestamp of the last frame"""
        return self.last_timestamp or time.time()
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.stop()

