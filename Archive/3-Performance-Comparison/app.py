import gradio as gr
import torch
import cv2
import os
import numpy as np
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import List, Tuple, Dict
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# --- 1. Model and Processor Initialization ---
print("Initializing models...")
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# Vision Model (BLIP)
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-large",
    torch_dtype=torch.float16 if device == "mps" else torch.float32
).to(device)
print("BLIP vision model loaded successfully.")

# NEW: Sentence Transformer Model for Similarity
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Sentence Transformer model loaded successfully.")


# --- 2. Securely Initialize Groq Client ---
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

# NEW: List of LLM models to compare
LLM_MODELS_TO_COMPARE = [
    "llama-3.3-70b-versatile",         # <model no 1> by meta
    "llama-3.1-8b-instant",        # <model no 2> by meta
    "gemma2-9b-it",            # <model no 3> by google 
]

# --- 3. Core Functions ---

def summarize_with_groq(descriptions: List[str], model_name: str) -> str:
    """
    Sends a list of descriptions to the Groq API using a specific model.
    """
    if not groq_client:
        return "Error: Groq client is not configured."

    prompt_content = ". ".join(descriptions)
    system_prompt = (
       "You are a motion analysis expert AI. Your purpose is to describe what is HAPPENING, not just what is THERE. "
        "I will provide a sequence of static observations. Your task is to infer the single most likely action or movement that connects them. "
        "Deduce the verb or action that describes the transition. "
        "Example 1: ['a person is standing', 'a person is lifting their foot'] -> 'A person is starting to walk.' "
        "Example 2: ['a car is on the left', 'the same car is now in the center'] -> 'A car is moving across the road.' "        
        "Your response MUST follow these strict rules:"
        "1.  Provide ONLY the summary sentence describing the action. "
        "2.  Do NOT include any greetings, preambles, or follow-up text (e.g., 'Here is the summary:', 'Certainly,', 'I hope this helps.'). "
        "3.  The summary must be precise and should not exceed two sentences. "
        "Your output must be the raw summary text and nothing else."
    )

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_content},
            ],
            model=model_name,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred with the Groq API for model {model_name}: {e}")
        return f"Error: Could not generate summary via Groq for model {model_name}. Details: {e}"

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

def rank_models_by_similarity(ground_truth: str, generated_summaries: Dict[str, str]) -> str:
    """
    NEW: Calculates similarity scores and ranks models.
    """
    if not ground_truth:
        return "Cannot calculate similarity without a ground truth description."
    if not generated_summaries:
        return "No generated summaries to compare."

    # Separate models and their summaries
    model_names = list(generated_summaries.keys())
    summaries = list(generated_summaries.values())

    # Generate embeddings
    ground_truth_embedding = similarity_model.encode([ground_truth])
    summary_embeddings = similarity_model.encode(summaries)

    # Calculate cosine similarity
    similarities = cosine_similarity(ground_truth_embedding, summary_embeddings)[0]

    # Create a list of (model_name, score) tuples
    ranked_results = sorted(zip(model_names, similarities), key=lambda item: item[1], reverse=True)

    # Format the output string
    output_str = "🏆 Model Ranking (by similarity to your Ground Truth):\n\n"
    for i, (model, score) in enumerate(ranked_results):
        output_str += f"{i+1}. {model}\n   Similarity Score: {score:.4f}\n\n"
    
    return output_str


# --- 4. Main Processing Pipeline for Gradio ---

def process_video_and_compare(video_path: str, ground_truth: str, frames_per_sec: int) -> Tuple[str, str, str]:
    """
    The main pipeline function that processes video, generates summaries from multiple models,
    and ranks them based on similarity to a ground truth.
    Returns three strings: raw descriptions, all generated summaries, and the final ranking.
    """
    if video_path is None:
        return "Please upload a video file.", "", ""
    if not ground_truth:
        return "Please provide a Ground Truth description.", "", ""

    print(f"Processing video: {video_path}")
    key_frames = extract_key_frames(video_path, frames_per_sec)
    if not key_frames:
        return "Could not extract frames from the video.", "", ""

    descriptions = [describe_frame(frame) for frame in key_frames]
    
    # Simple de-duplication
    unique_descriptions = []
    if descriptions:
        seen = set()
        for desc in descriptions:
            if desc not in seen:
                unique_descriptions.append(desc)
                seen.add(desc)

    raw_descriptions_str = "\n".join(f"- {desc}" for desc in unique_descriptions)
    if not unique_descriptions:
        return "No unique descriptions generated from video frames.", "", ""

    # Generate summaries from all models
    print(f"Generating summaries from {len(LLM_MODELS_TO_COMPARE)} models...")
    generated_summaries = {}
    all_summaries_str = ""
    for model_name in LLM_MODELS_TO_COMPARE:
        summary = summarize_with_groq(unique_descriptions, model_name)
        generated_summaries[model_name] = summary
        all_summaries_str += f"--- Description by {model_name} ---\n{summary}\n\n"
    
    # Rank models based on similarity
    print("Ranking models by similarity to ground truth...")
    ranking_results = rank_models_by_similarity(ground_truth, generated_summaries)

    metadata = f"\n\n(Analysis based on {len(key_frames)} frames.)"
    return raw_descriptions_str + metadata, all_summaries_str.strip(), ranking_results


# --- 5. Gradio UI Definition ---

description_md = """
# AIris - Action Derivation & Model Comparison
### Enhanced Capstone Project Prototype
This tool analyzes a video, asks multiple AI models to describe the primary action, and then ranks them by comparing their descriptions to your "Ground Truth".

**How to Use:**
1.  **Upload a Video:** Choose a short video clip.
2.  **Provide Ground Truth:** Write a single, clear sentence describing the main action in the video. This is the reference for comparison.
3.  **Analyze:** The system will extract frames, generate descriptions from 4 different LLMs, and then score and rank them for you.
"""

iface = gr.Interface(
    fn=process_video_and_compare,
    inputs=[
        gr.Video(label="Upload Video Clip"),
        gr.Textbox(label="Ground Truth Description", info="Enter a single sentence describing the main action in the video (e.g., 'A car is driving down a road.')"),
        gr.Slider(minimum=1, maximum=5, value=2, step=1, label="Frames to Analyze per Second"),
    ],
    outputs=[
        gr.Textbox(label="Raw Frame Descriptions (from BLIP)", lines=10),
        gr.Textbox(label="Model-Generated Descriptions (from Groq LLMs)", lines=12),
        gr.Textbox(label="Model Ranking & Similarity Scores", lines=10)
    ],
    title="AIris: Action Derivation Model Benchmarking",
    description=description_md,
    allow_flagging="never",
    examples=[
        ["custom_test/16835003-hd_1280_720_24fps.mp4", "A car is driving down a winding road in a forest.", 2],
        ["custom_test/4185375-hd_720_1366_24fps.mp4", "A person is pouring coffee from a pot into a white mug.", 3],
    ]
)

if __name__ == "__main__":
    iface.launch()