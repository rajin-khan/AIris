import gradio as gr
import torch
import cv2
import os
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import List

# --- 1. Model and Processor Initialization ---
# We load the model and processor once to avoid reloading on every request.
# This is crucial for performance.

# Check for MPS (Apple Silicon GPU) availability, fall back to CPU if not found
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# Load the pre-trained model and processor from Hugging Face.
# We use float16 for faster inference and lower memory usage on MPS.
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
if device == "mps":
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large", torch_dtype=torch.float16).to(device)
else:
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)

print("Model and processor loaded successfully.")


# --- 2. Backend Logic: Video Processing and Description ---

def extract_key_frames(video_path: str, frames_per_sec: int) -> List[Image.Image]:
    """
    Extracts frames from a video file at a specified rate.
    
    Args:
        video_path (str): The path to the video file.
        frames_per_sec (int): How many frames to extract per second of video.
        
    Returns:
        List[Image.Image]: A list of frames as PIL Images.
    """
    key_frames = []
    if not os.path.exists(video_path):
        print(f"Video file not found at: {video_path}")
        return key_frames
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return key_frames

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps == 0:
        print("Warning: Could not determine video FPS. Defaulting to 30.")
        video_fps = 30 # A reasonable default

    # Calculate the interval at which to capture frames
    capture_interval = video_fps / frames_per_sec
    frame_count = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        # Check if the current frame is one we want to capture
        if frame_count % capture_interval < 1:
            # Convert the frame from BGR (OpenCV format) to RGB (PIL format)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            key_frames.append(pil_image)
            
        frame_count += 1
        
    cap.release()
    print(f"Extracted {len(key_frames)} key frames from the video.")
    return key_frames

def describe_frame(image: Image.Image) -> str:
    """
    Generates a caption for a single image frame using the BLIP model.
    
    Args:
        image (Image.Image): The input image.
        
    Returns:
        str: The generated text description.
    """
    # Prepare the image for the model
    # Use float16 for MPS device
    if device == "mps":
        inputs = processor(images=image, return_tensors="pt").to(device, torch.float16)
    else:
        inputs = processor(images=image, return_tensors="pt").to(device)

    # Generate the caption
    pixel_values = inputs.pixel_values
    generated_ids = model.generate(pixel_values=pixel_values, max_length=50)
    
    # Decode the generated IDs to a string
    caption = processor.decode(generated_ids[0], skip_special_tokens=True)
    
    # A simple way to make descriptions more narrative for the AIris context
    # This is a placeholder for a more advanced summarization step.
    if not caption.lower().startswith("a woman") and not caption.lower().startswith("a man"):
         caption = "The scene shows " + caption

    return caption


def process_video_and_describe(video_path: str, frames_per_sec: int) -> str:
    """
    The main function that orchestrates the entire pipeline.
    This is the function that Gradio will call.
    
    Args:
        video_path (str): Path to the uploaded video.
        frames_per_sec (int): Number of frames to process per second.
        
    Returns:
        str: A synthesized description of the video content.
    """
    if video_path is None:
        return "Please upload a video file."
    
    print(f"Processing video: {video_path}")
    print(f"Frames per second to analyze: {frames_per_sec}")

    # Step 1: Extract key frames from the video
    key_frames = extract_key_frames(video_path, frames_per_sec)
    
    if not key_frames:
        return "Could not extract any frames from the video. Please check the file."
        
    # Step 2: Describe each key frame
    descriptions = []
    for i, frame in enumerate(key_frames):
        print(f"Describing frame {i+1}/{len(key_frames)}...")
        desc = describe_frame(frame)
        descriptions.append(desc)
        print(f"  > Description: {desc}")
        
    # Step 3: Synthesize the descriptions into a final summary
    # For this simple pipeline, we will join them.
    # A more advanced approach would use another LLM to summarize these points.
    # We can also remove duplicate-like descriptions to make it more concise.
    unique_descriptions = []
    for desc in descriptions:
        # A simple way to avoid very similar descriptions
        if not any(d in desc for d in unique_descriptions) and not any(desc in d for d in unique_descriptions):
            unique_descriptions.append(desc)

    final_description = " ".join(unique_descriptions)

    # Add a concluding sentence.
    final_description += f"\n\nThis summary is based on analyzing {len(key_frames)} frames from the video."
    
    return final_description


# --- 3. Gradio Frontend ---
# This section creates the web UI.

# A brief description in Markdown for the UI.
description = """
# AIris - Local Video Description Pipeline 📹
### A Tangible Capstone Project Prototype

Upload a short video clip, and the AI will describe what's happening. 
This pipeline runs entirely on your local machine. It works by extracting key frames from the video, 
describing each frame, and then combining the descriptions into a summary.

**You can control how many frames per second the AI analyzes.** 
- **Higher value:** More detailed, but slower.
- **Lower value:** Faster, but might miss quick actions.
"""

# Create the Gradio Interface
iface = gr.Interface(
    fn=process_video_and_describe,
    inputs=[
        gr.Video(label="Upload Video Clip"),
        gr.Slider(minimum=1, maximum=5, value=2, step=1, label="Frames to Analyze per Second")
    ],
    outputs=gr.Textbox(label="AI-Generated Description", lines=10),
    title="AIris Video Description Prototype",
    description=description,
    allow_flagging="never",
    examples=[
        # You can add example video paths here if you have them locally
        # ["path/to/your/example1.mp4", 2],
        # ["path/to/your/example2.mp4", 3],
    ]
)

# Launch the web server
if __name__ == "__main__":
    iface.launch()