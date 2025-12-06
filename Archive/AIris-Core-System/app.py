# app.py
import gradio as gr
import time
import os
from typing import Tuple

# Import our refactored logic
import prompts
from pipeline import extract_key_frames, describe_frame
from llm_integrations import get_llm_response

# --- GROUND TRUTH DATA (for demo and evaluation) ---
# This dictionary maps the example video filenames to their ideal "ground truth" descriptions.
GROUND_TRUTH_MAP = {
    "indoor_nav_01.mp4": "You are in a bedroom. A bed is directly in front of you. There is a clear path to the left around the bed. A window is right in front of you.",
    "object_find_01.mp4": "You are at a table. A white coffee mug is on your right, next to a silver laptop.",
    "dynamic_hazard_01.mp4": "A person is walking away from you from at the end of the road, approximately 15 feet away. The path is otherwise clear."
}

# --- ASSISTIVE MODE TO PROMPT MAPPING ---
PROMPT_MAP = {
    "Indoor Navigation": prompts.NAVIGATION_PROMPT,
    "Object Finder": prompts.OBJECT_FINDER_PROMPT,
    "Environmental Awareness": prompts.ENVIRONMENTAL_AWARENESS_PROMPT,
    "Dynamic Hazard Detection": prompts.DYNAMIC_HAZARD_PROMPT,
}

def airis_pipeline(video_path: str, mode: str, frames_per_sec: int) -> Tuple[str, str, str, str]:
    """
    The complete AIris pipeline. It now returns the ground truth for direct comparison.
    """
    if not video_path:
        return "Please upload a video.", "", "", ""

    start_time = time.time()
    
    # Check for ground truth based on the video's filename
    video_filename = os.path.basename(video_path)
    ground_truth_text = GROUND_TRUTH_MAP.get(video_filename, "N/A for this custom video.")

    # 1. Vision Pipeline: Extract key frames and generate raw descriptions
    key_frames = extract_key_frames(video_path, frames_per_sec)
    if not key_frames:
        return "Could not extract frames.", "", ground_truth_text, ""
        
    descriptions = [describe_frame(frame) for frame in key_frames]
    unique_descriptions = list(dict.fromkeys(descriptions)) # Preserve order while removing duplicates
    
    raw_observations = "\n".join(f"- {desc}" for desc in unique_descriptions)

    # 2. LLM Reasoning Pipeline: Summarize observations into an actionable description
    system_prompt = PROMPT_MAP.get(mode, prompts.NAVIGATION_PROMPT)
    assistive_output = get_llm_response(unique_descriptions, system_prompt)
    
    end_time = time.time()
    latency = end_time - start_time
    
    metadata = f"Latency: {latency:.2f} seconds\nFrames Analyzed: {len(key_frames)}\nMode: {mode}"

    return raw_observations, assistive_output, ground_truth_text, metadata

# --- Gradio UI Definition ---
description_md = """
# AIris Core System: Evaluation Interface
### A purpose-built assistive AI for navigation and interaction.
This interface allows for direct comparison between the **AI's live output** and the **pre-defined Ground Truth** for our test videos.
"""

iface = gr.Interface(
    fn=airis_pipeline,
    inputs=[
        gr.Video(label="Upload Evaluation Video"),
        gr.Dropdown(
            choices=list(PROMPT_MAP.keys()),
            value="Indoor Navigation",
            label="Select Assistive Mode"
        ),
        gr.Slider(minimum=1, maximum=5, value=2, step=1, label="Analysis Detail (Frames per Second)")
    ],
    outputs=[
        gr.Textbox(label="Stage 1: Raw Visual Observations", lines=5),
        gr.Textbox(label="✅ Stage 2: Final AI Output (Summarized)", lines=5),
        gr.Textbox(label="🎯 Ground Truth (The Benchmark)", lines=5),
        gr.Textbox(label="Performance Metrics", lines=3)
    ],
    title="AIris: Assistive AI Evaluation Dashboard",
    description=description_md,
    allow_flagging="never",
    # IMPORTANT: Update these paths to your test videos for easy one-click demos
    examples=[
        ["../evaluation_dataset/indoor_nav_01.mp4", "Indoor Navigation", 2],
        ["../evaluation_dataset/object_find_01.mp4", "Object Finder", 3],
        ["../evaluation_dataset/dynamic_hazard_01.mp4", "Dynamic Hazard Detection", 2],
    ]
)

if __name__ == "__main__":
    iface.launch()