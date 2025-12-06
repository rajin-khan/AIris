# pipeline.py
import torch
import cv2
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import List

print("Initializing vision model...")
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-large",
    torch_dtype=torch.float16 if device == "mps" else torch.float32
).to(device)
print("BLIP vision model loaded successfully.")

def extract_key_frames(video_path: str, frames_per_sec: int) -> List[Image.Image]:
    """Extracts frames from a video file at a specified rate."""
    key_frames = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return key_frames
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    capture_interval = int(video_fps / frames_per_sec) if frames_per_sec > 0 else int(video_fps)
    if capture_interval == 0: capture_interval = 1

    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        if frame_count % capture_interval == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            key_frames.append(Image.fromarray(rgb_frame))
        frame_count += 1
    cap.release()
    print(f"Extracted {len(key_frames)} key frames.")
    return key_frames

def describe_frame(image: Image.Image) -> str:
    """Generates a caption for a single image frame."""
    inputs = processor(images=image, return_tensors="pt").to(device, torch.float16 if device == "mps" else torch.float32)
    generated_ids = model.generate(pixel_values=inputs.pixel_values, max_length=50)
    caption = processor.decode(generated_ids[0], skip_special_tokens=True)
    return caption.strip()