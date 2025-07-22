import gradio as gr
import torch
import cv2
import os
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import List, Tuple
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# --- 1. Model and Processor Initialization ---
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-large",
    torch_dtype=torch.float16 if device == "mps" else torch.float32
).to(device)

print("Model and processor loaded successfully.")

# --- 2. Securely Initialize Groq Client from Environment Variable ---
groq_client = None
try:
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        groq_client = Groq(api_key=api_key)
        print("Groq client initialized successfully from .env file.")
    else:
        print("Warning: GROQ_API_KEY not found in .env file or environment.")
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    groq_client = None


def summarize_with_groq(descriptions: List[str]) -> str:
    """
    Sends a list of chronological descriptions to the Groq API to generate a narrative summary.
    """
    if not groq_client:
        return "Error: Groq client is not configured. Please check your .env file for the GROQ_API_KEY."

    # Concatenate descriptions into a single string for the prompt
    prompt_content = ". ".join(descriptions)

    system_prompt = (
        "You are a motion analysis expert for an assistive AI. Your purpose is to describe what is HAPPENING, not just what is THERE. "
        "I will provide a sequence of pre-filtered, consistent, and time-ordered static observations. "
        "Your task is to infer the single most likely action or movement that connects these static frames. "
        "Do NOT simply rephrase one of the observations. Instead, deduce the verb or action that describes the transition between them. "
        "For example, if the observations are ['a person is standing', 'a person is lifting their foot', 'a person is moving forward'], the correct output is 'A person is starting to walk.' "
        "If the observations are ['a car is on the left', 'the same car is now in the center'], the correct output is 'A car is moving across the road.' "
        "The final output must be a single, concise sentence focused on the derived action."
    )

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_content},
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred with the Groq API: {e}")
        return f"Error: Could not generate summary via Groq. Details: {e}"

def summarize_with_ollama(descriptions: List[str]) -> str:
    """
    Placeholder for future Ollama integration.
    """
    print("Ollama summarization requested (not implemented yet).")
    return "Ollama summarization is not yet implemented. This is a placeholder for future development."

def extract_key_frames(video_path: str, frames_per_sec: int) -> List[Image.Image]:
    """Extracts frames from a video file at a specified rate."""
    key_frames = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return key_frames
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    capture_interval = video_fps / frames_per_sec
    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        if frame_count % capture_interval < 1:
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
    return caption

def process_video_and_describe(video_path: str, frames_per_sec: int, summarizer_choice: str) -> Tuple[str, str]:
    """
    The main pipeline function that now includes a summarization step.
    Returns two strings: raw descriptions and the final summary.
    """
    if video_path is None:
        return "Please upload a video file.", ""
    print(f"Processing video: {video_path} with {summarizer_choice}")
    key_frames = extract_key_frames(video_path, frames_per_sec)
    if not key_frames:
        return "Could not extract frames from the video.", ""
    descriptions = [describe_frame(frame) for frame in key_frames]
    unique_descriptions = []
    if descriptions:
        unique_descriptions.append(descriptions[0])
        for i in range(1, len(descriptions)):
            if descriptions[i] not in descriptions[i-1] and descriptions[i-1] not in descriptions[i]:
                 unique_descriptions.append(descriptions[i])
    raw_descriptions_str = "\n".join(f"- {desc}" for desc in unique_descriptions)
    final_narrative = ""
    if summarizer_choice == "Groq API":
        final_narrative = summarize_with_groq(unique_descriptions)
    elif summarizer_choice == "Ollama (Local)":
        final_narrative = summarize_with_ollama(unique_descriptions)
    metadata = f"\n\n(Summary based on analyzing {len(key_frames)} frames.)"
    return raw_descriptions_str, final_narrative + metadata

description_md = """
# AIris - Video Narrative Generation Pipeline 📹
### Enhanced Capstone Project Prototype
Upload a short video, select a summarization engine, and the AI will generate a narrative story of the events.
1.  **Frame Analysis:** The system extracts key frames from the video.
2.  **Scene Description:** Each frame is described individually using a local Vision model (BLIP).
3.  **Narrative Synthesis:** The descriptions are sent to a powerful LLM (Groq or Ollama) to be woven into a cohesive story.
"""
iface = gr.Interface(
    fn=process_video_and_describe,
    inputs=[
        gr.Video(label="Upload Video Clip"),
        gr.Slider(minimum=1, maximum=5, value=2, step=1, label="Frames to Analyze per Second"),
        gr.Radio(
            ["Groq API", "Ollama (Local)"], 
            label="Summarization Engine", 
            value="Groq API",
            info="Choose how the final narrative is generated. Groq is fast and requires an API key. Ollama will run locally."
        )
    ],
    outputs=[
        gr.Textbox(label="Raw Frame Descriptions", lines=8),
        gr.Textbox(label="AI-Generated Narrative Summary", lines=8)
    ],
    title="AIris Video Description & Summarization",
    description=description_md,
    allow_flagging="never",
    examples=[
        ["custom_test/16835003-hd_1280_720_24fps.mp4", 2, "Groq API"],
        ["custom_test/4185375-hd_720_1366_24fps.mp4", 3, "Groq API"],
    ]
)

if __name__ == "__main__":
    iface.launch()