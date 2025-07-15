# WEEK 0: AIris Prototype: Local Video Description Pipeline

**Status:** `Functional Prototype` | **Phase:** `Core Software Development` | **Project:** `CSE 499A/B`

> A Tangible Local Inference Pipeline for Real-Time Video Description. This prototype serves as the foundational software component for the AIris project, demonstrating the core capability of transforming video input into narrative text descriptions entirely on a local machine.

---

## 1. Project Overview & Connection to Research

The AIris project aims to create a wearable, real-time scene description system for the visually impaired. This software prototype is the first major milestone, establishing a robust, offline-first inference pipeline that forms the "brain" of the final hardware device.

Our approach is directly informed by the project's literature review, addressing key challenges identified in existing assistive technologies:

*   **Addressing Latency and Cloud Dependency:** Many assistive tools rely on the cloud, introducing latency and privacy concerns (as noted in survey papers like "AI-Powered Assistive Technologies for Visual Impairment"). This prototype runs **100% locally** on a MacBook Air M1, using the MPS backend for GPU acceleration, proving the feasibility of an edge-first design.
*   **Leveraging State-of-the-Art Vision Models:** Inspired by research into models like **LLaVA** and **BLIP-2**, we use a powerful pre-trained image captioning model (`Salesforce/blip-image-captioning-large`). This provides high-quality descriptions that go beyond simple object lists.
*   **A Practical Approach to Video Analysis:** Instead of computationally expensive video-LLMs, we adopt a more "lightweight" and practical approach discussed in papers on edge devices. We treat video as a sequence of key frames, analyzing each individually. This makes real-time performance achievable on consumer hardware, a critical factor for a wearable device.

### Core Features of this Prototype

*   **Video-to-Text Pipeline:** Ingests a video file and outputs a synthesized text description.
*   **Local Inference:** The entire AI model runs on-device, requiring no internet connection after the initial setup.
*   **Adjustable Analysis Granularity:** Users can control the number of frames analyzed per second, trading off speed for detail.
*   **Interactive Web UI:** A simple Gradio interface allows for easy testing and demonstration.
*   **Apple Silicon Accelerated:** Utilizes PyTorch's MPS backend for fast inference on M1/M2/M3 chips.

---

## 2. Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Core Language** | Python 3.10+ | Main development language. |
| **AI Framework** | PyTorch | For running the deep learning model. |
| **Model Hub** | Hugging Face Transformers | To easily download and use pre-trained models. |
| **Video Processing** | OpenCV | For extracting frames from video files. |
| **Web Interface** | Gradio | To create a simple, interactive UI for demonstration. |
| **Dependencies** | Conda | For environment management and isolation. |

---

## 3. Setup and Installation Guide

Follow these steps to get the pipeline running on your machine.

### Prerequisites

*   A macOS machine with an Apple Silicon (M1/M2/M3) chip.
*   [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed.
*   [Homebrew](https://brew.sh/) installed for system dependencies.

### Step-by-Step Instructions

1.  **Install System Dependencies:**
    Open your terminal and install `wget`, which we'll use for robustly downloading dataset samples.
    ```bash
    brew install wget
    ```

2.  **Create and Activate Conda Environment:**
    ```bash
    # Create a new environment named 'airis_pipeline'
    conda create -n airis_pipeline python=3.10 -y

    # Activate the environment
    conda activate airis_pipeline
    ```

3.  **Install Python Libraries:**
    Install all necessary libraries, including the Apple Silicon-compatible version of PyTorch.
    ```bash
    # Install PyTorch with MPS support
    pip install torch torchvision torchaudio

    # Install the core application libraries
    pip install transformers opencv-python-headless gradio sentencepiece requests rarfile
    
    # Install the library for interacting with the Hugging Face Hub
    pip install huggingface_hub
    ```

4.  **One-Time Model Download:**
    The first time you run the application, the `transformers` library will automatically download the pre-trained BLIP model (~1.88 GB). This is a **one-time download**. The model will be cached locally in `~/.cache/huggingface/hub/` for all future runs.

---

## 4. How to Get Test Data

You have two options to get sample videos for testing.

### Option A: Download Random Royalty-Free Videos (Recommended for Quick Start)

This is the fastest way to start testing.
1.  Visit a site like **[Pexels Videos](https://www.pexels.com/videos/)** or **[Pixabay Videos](https://pixabay.com/videos/)**.
2.  Search for simple actions ("person walking", "car driving") and download 3-5 short clips.
3.  Create a folder named `my_test_videos` in your project directory and place the clips inside.

### Option B: Download a Curated Sample from the Kinetics Dataset

This provides a more structured set of test clips. Save the following code as `setup_kinetics_samples.py` in your project folder.

#### `setup_kinetics_samples.py`
```python
import os
import requests
import random
import tarfile
import shutil
import subprocess

# --- Configuration ---
K400_VAL_URL_LIST = "https://s3.amazonaws.com/kinetics/400/val/k400_val_path.txt"
TEMP_DOWNLOAD_DIR = "kinetics_temp_downloads"
EXTRACT_DIR = "kinetics_full_extracted"
SAMPLES_DIR = "kinetics_samples"
NUM_ARCHIVES_TO_DOWNLOAD = 3
MAX_CLIPS_FINAL = 15

def check_dependencies():
    """Checks if wget is installed."""
    if not shutil.which('wget'):
        print("\n[ERROR] 'wget' command not found. Please run 'brew install wget'")
        return False
    print("✅ 'wget' command found.")
    return True

def setup_kinetics_samples():
    """Downloads and extracts a small, random sample from the Kinetics-400 dataset using wget."""
    print("--- AIris Kinetics-400 Sampler (Robust Wget Edition) ---")
    
    if not check_dependencies():
        return

    print(f"\n[1/5] 📥 Fetching the list of video archives...")
    try:
        response = requests.get(K400_VAL_URL_LIST)
        response.raise_for_status()
        archive_urls = response.text.strip().split('\n')
        print(f"✅ Found {len(archive_urls)} total archives.")
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch the URL list. Details: {e}")
        return

    selected_urls = random.sample(archive_urls, NUM_ARCHIVES_TO_DOWNLOAD)
    print(f"\n[2/5] 🎲 Randomly selected {len(selected_urls)} archives to download.")
    
    os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    
    print("\n[3/5] 📦 Downloading and extracting archives with wget...")
    all_extracted_videos = []

    for url in selected_urls:
        filename = os.path.basename(url)
        archive_path = os.path.join(TEMP_DOWNLOAD_DIR, filename)
        
        try:
            print(f"  -> Downloading {filename}...")
            subprocess.run(['wget', '-c', '-P', TEMP_DOWNLOAD_DIR, url], check=True, capture_output=True)
            
            print(f"  -> Extracting {filename}...")
            with tarfile.open(archive_path, "r:gz") as tar:
                for member in tar.getmembers():
                    if member.isfile() and any(member.name.lower().endswith(ext) for ext in ['.mp4', '.avi']):
                        all_extracted_videos.append(os.path.join(EXTRACT_DIR, member.name))
                tar.extractall(path=EXTRACT_DIR)

            os.remove(archive_path)
            print(f"  ✅ Extracted and cleaned up {filename}.")
        except Exception as e:
            print(f"  [ERROR] Failed to process {filename}. Skipping. Details: {e}")

    shutil.rmtree(TEMP_DOWNLOAD_DIR, ignore_errors=True)

    if not all_extracted_videos:
        print("[ERROR] No videos extracted.")
        return

    print(f"\n[4/5] ✨ Selecting final {MAX_CLIPS_FINAL} clips...")
    if os.path.exists(SAMPLES_DIR):
        shutil.rmtree(SAMPLES_DIR)
    os.makedirs(SAMPLES_DIR)
    final_clips = random.sample(all_extracted_videos, min(len(all_extracted_videos), MAX_CLIPS_FINAL))
    
    print(f"\n[5/5] 🚚 Copying samples to '{SAMPLES_DIR}'...")
    for video_path in final_clips:
        if os.path.exists(video_path):
            shutil.copy(video_path, SAMPLES_DIR)
            
    print("\n--- Sample Setup Complete! ---")
    print(f"✅ Created a sample set of {len(os.listdir(SAMPLES_DIR))} clips in '{SAMPLES_DIR}/'.")

if __name__ == "__main__":
    setup_kinetics_samples()
```
**To run it:** `python setup_kinetics_samples.py`

---

## 5. The Application Code

Save the main application code as `app.py`.

#### `app.py`
```python
import gradio as gr
import torch
import cv2
import os
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import List

# --- Model Initialization ---
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-large", 
    torch_dtype=torch.float16 if device == "mps" else torch.float32
).to(device)

print("Model and processor loaded successfully.")

# --- Backend Logic ---
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
    # A simple narrative prefix for context
    return "The scene shows " + caption if not caption.lower().startswith(("a man", "a woman")) else caption

def process_video_and_describe(video_path: str, frames_per_sec: int) -> str:
    """The main pipeline function for Gradio."""
    if video_path is None:
        return "Please upload a video file."

    key_frames = extract_key_frames(video_path, frames_per_sec)
    if not key_frames:
        return "Could not extract frames from the video."
        
    descriptions = [describe_frame(frame) for frame in key_frames]
    
    # Simple synthesis: remove similar consecutive descriptions
    unique_descriptions = []
    if descriptions:
        unique_descriptions.append(descriptions[0])
        for i in range(1, len(descriptions)):
            # A basic check to avoid stuttering descriptions
            if descriptions[i] not in descriptions[i-1] and descriptions[i-1] not in descriptions[i]:
                 unique_descriptions.append(descriptions[i])
    
    final_description = ". ".join(unique_descriptions)
    final_description += f"\n\n(This summary is based on analyzing {len(key_frames)} frames from the video.)"
    
    return final_description

# --- Gradio Frontend ---
description_md = """
# AIris - Local Video Description Pipeline 📹
### A Tangible Capstone Project Prototype
Upload a short video clip, and the AI will describe what's happening.
"""

iface = gr.Interface(
    fn=process_video_and_describe,
    inputs=[
        gr.Video(label="Upload Video Clip"),
        gr.Slider(minimum=1, maximum=5, value=2, step=1, label="Frames to Analyze per Second")
    ],
    outputs=gr.Textbox(label="AI-Generated Description", lines=10),
    title="AIris Video Description Prototype",
    description=description_md,
    allow_flagging="never",
)

if __name__ == "__main__":
    iface.launch()
```

---

## 6. Running the Application

1.  Make sure the `airis` environment is active (install dependencies and create a conda environment using the requirements.txt file).
2.  Run the application from your terminal:
    ```bash
    python app.py
    ```
3.  The terminal will display a local URL (e.g., `http://127.0.0.1:7860`). Open this in your browser.
4.  Upload a video, adjust the slider, and click **Submit**.

---

## 7. Tentative Next Steps: Creating a Coherent Narrative

The current prototype generates a series of descriptions. The next critical step is to synthesize these into a single, fluid narrative. This requires a Language Model (LLM).

**The Goal:** Transform `["A dog is running on grass.", "A person is throwing a frisbee.", "The dog is catching the frisbee."]` into `"A person is playing with a dog on the grass, throwing a frisbee which the dog then catches."`

Here are two paths to achieve this:

### Path 1: Local LLM with Ollama (Privacy-First)

**Ollama** allows you to run powerful LLMs like Llama 3 locally. This keeps the entire pipeline offline.

**Conceptual Implementation:**

1.  [Install Ollama](https://ollama.com/) on your Mac.
2.  Pull a small, fast model: `ollama pull llama3:8b`
3.  Add a summarization function to `app.py`:
    ```python
    # Conceptual code - requires 'ollama' library (pip install ollama)
    import ollama

    def summarize_descriptions(descriptions: List[str]) -> str:
        prompt = (
            "You are a concise scene describer for a visually impaired user. "
            "Combine the following sequence of events into a single, fluid paragraph. "
            "Focus on the main actions and the relationship between objects. "
            f"Events: {'. '.join(descriptions)}"
        )
        
        response = ollama.chat(
            model='llama3:8b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']

    # In process_video_and_describe, replace the .join() with:
    # final_description = summarize_descriptions(unique_descriptions)
    ```

### Path 2: High-Speed Cloud LLM with Groq API (Performance-First)

**Groq** provides the world's fastest LLM inference via an API. This is a great choice for a real-time feel if an internet connection is available.

**Conceptual Implementation:**

1.  Get a free API key from [Groq](https://console.groq.com/keys).
2.  Install the client: `pip install groq`
3.  Add a similar summarization function:
    ```python
    # Conceptual code
    from groq import Groq

    client = Groq(api_key="YOUR_GROQ_API_KEY")

    def summarize_with_groq(descriptions: List[str]) -> str:
        prompt = "..." # Same prompt as above
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    ```