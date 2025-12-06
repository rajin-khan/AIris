"""
Frame utility functions for drawing annotations
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def load_font(font_path: str = None, size: int = 24) -> ImageFont.FreeTypeFont:
    """Load font for text rendering"""
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except IOError:
            pass
    return ImageFont.load_default()

def draw_guidance_on_frame(frame: np.ndarray, text: str, font: ImageFont.FreeTypeFont = None) -> np.ndarray:
    """Draw guidance text on frame with black background"""
    if font is None:
        font = load_font()
    
    # Convert BGR to RGB for PIL
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    if text:
        try:
            # Try modern textbbox method
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            # Fallback to older textsize method
            text_width, text_height = draw.textsize(text, font=font)
        
        # Draw black background rectangle
        draw.rectangle([10, 10, 20 + text_width, 20 + text_height], fill="black")
        # Draw white text
        draw.text((15, 15), text, font=font, fill="white")
    
    # Convert back to BGR for OpenCV
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

