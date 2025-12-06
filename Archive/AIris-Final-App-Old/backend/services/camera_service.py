"""
Camera Service - Handles camera operations
"""

import cv2
import asyncio
from typing import Optional
import time

class CameraService:
    def __init__(self):
        self.vid_cap: Optional[cv2.VideoCapture] = None
        self.is_running_flag = False
        self.last_frame = None
        self.last_timestamp = None
    
    async def start(self) -> bool:
        """Start the camera"""
        if self.is_running():
            return True
        
        # Try multiple camera indices
        for camera_index in [0, 1, 2]:
            self.vid_cap = cv2.VideoCapture(camera_index)
            await asyncio.sleep(0.5)  # Give camera time to initialize
            
            if self.vid_cap.isOpened():
                ret, test_frame = self.vid_cap.read()
                if ret and test_frame is not None:
                    self.is_running_flag = True
                    return True
                else:
                    self.vid_cap.release()
        
        return False
    
    async def stop(self):
        """Stop the camera"""
        if self.vid_cap is not None:
            self.vid_cap.release()
            self.vid_cap = None
        self.is_running_flag = False
        self.last_frame = None
    
    async def get_frame(self) -> Optional:
        """Get the latest frame from camera"""
        if not self.is_running():
            return None
        
        ret, frame = self.vid_cap.read()
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
        # Try to open a test capture
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


