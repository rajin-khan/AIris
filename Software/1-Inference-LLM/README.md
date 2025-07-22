# AIris Prototype: The Action Derivation Pipeline

**Status:** `Advanced Prototype` | **Phase:** `Core Software Development` | **Project:** `CSE 499A/B`

> This prototype has evolved from a simple video descriptor into an intelligent **Action Derivation Engine**. It demonstrates the core innovation of the AIris project: the ability to analyze a sequence of visual data, reason about the context, and infer the single most important **action** occurring in a scene.

---

## 1. This Week's Evolution: From Naive Summarization to Intelligent Inference

Our initial goal was to use a Large Language Model (LLM) to summarize frame-by-frame descriptions into a cohesive narrative. However, through rigorous testing, we discovered two fundamental challenges that required a significant pivot in our approach, moving from simple summarization to a more complex task of inference.

### Challenge 1: The Descriptive Bias of LLMs
We found that LLMs are naturally biased towards *describing* scenes rather than *interpreting actions*. Early attempts resulted in passive, list-like summaries that were not useful for an assistive device.

### Challenge 2: The Anomaly Problem
Even in static videos, the vision model produced minor inconsistencies (e.g., describing a floor as "ground" in one frame and a "gray surface" in another). A naive LLM would interpret these anomalies as actual events, creating a false narrative of movement (e.g., "a chair moved to a gray surface and back").

Our solution was a dedicated process of **prompt engineering**, where we iteratively refined our instructions to the LLM to overcome these challenges.

---

## 2. The Journey of Prompt Engineering

Our key breakthrough was realizing that the LLM needed to be treated as a reasoning engine, not just a text summarizer. We evolved our system prompt through several versions to achieve the desired result.

#### Prompt V1: The Simple Summarizer
```
"Combine the following sequence of events into a single, fluid paragraph."
```
*   **Result:** The LLM produced a long, descriptive paragraph. It failed to identify the primary action and was too verbose for real-time assistance.

#### Prompt V2: The Inconsistency Handler
```
"Synthesize these observations into a single, clear paragraph. Be consistent and focus on the most frequent description."
```
*   **Result:** This reduced the impact of anomalies but still produced a static description of the scene's most common state. It described the *what*, but not the *what's happening*.

#### Prompt V3: The Motion Analysis Expert (Current)
```python
"You are a motion analysis expert for an assistive AI. Your purpose is to describe what is HAPPENING, not just what is THERE. I will provide a sequence of pre-filtered, consistent, and time-ordered static observations. Your task is to infer the single most likely action or movement that connects these static frames. Do NOT simply rephrase one of the observations. Instead, deduce the verb or action that describes the transition between them..."
```
*   **Result:** **Success.** This detailed, role-playing prompt forces the LLM to perform inference. It correctly deduces the underlying action from the sequence of static frames, producing a concise and highly useful output like "A car is moving across the road."

---

## 3. Key Findings and Insights

*   **More Data, Better Inference:** We observed a direct correlation between the number of frames analyzed per second and the quality of the final derived action. A higher frame rate provides a richer sequence of observations for the LLM to analyze, leading to more accurate inference.
*   **Reasoning Models Excel:** The task of deriving action from static frames is a reasoning task, not a summarization task. We found that larger, more capable reasoning models performed significantly better. Our best and most consistent results were achieved using **`llama-3.3-70b-versatile`** via the Groq API.

---

## 4. The Current Pipeline

Our current system is a 2-stage pipeline that combines local analysis with high-speed cloud inference:

1.  **Stage 1: Local Vision Analysis**
    The `Salesforce/blip-image-captioning-large` model runs entirely on-device, extracting key frames from the video and generating a raw description for each. A simple de-duplication filter is applied.

2.  **Stage 2: Cloud-Based Action Derivation**
    The sequence of descriptions is sent to the Groq API, where the powerful Llama 3 70B model uses our specialized prompt to infer and generate a single, concise sentence describing the primary action.

---

## 5. Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Core Language** | Python 3.10+ | Main development language. |
| **AI Framework** | PyTorch | For running the local BLIP vision model. |
| **Video Processing** | OpenCV | For extracting frames from video files. |
| **Action Derivation LLM** | **Groq API (Llama 3 70B)** | For ultra-low-latency inference to derive the action. |
| **Web Interface** | Gradio | To create a simple, interactive UI for demonstration. |
| **Dependencies** | Conda | For environment management and isolation. |

---

## 6. Setup and Installation

### Prerequisites

*   A machine capable of running PyTorch.
*   [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed.
*   A Groq API Key.

### Instructions

1.  **Set Your API Key:** Open the `app.py` file and paste your Groq API key into the `GROQ_API_KEY` variable.
2.  **Create & Activate Environment:**
    ```bash
    conda create -n airis_pipeline python=3.10 -y
    conda activate airis_pipeline
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Application:**
    ```bash
    python app.py
    ```
5.  Open the local URL provided in your browser to start testing.

---

## 7. Next Steps: Benchmarking and Validation

With a robust and intelligent pipeline established, the next critical phase is to quantitatively measure its performance and curate a relevant dataset for validation.

### 7.1. Establish Benchmarking Metrics

Our "action derivation" task is a novel approach. Therefore, we will establish a custom metric: **Action Derivation Accuracy (ADA)**.

*   **Process:**
    1.  **Create a Curated Test Set:** Manually select 20-30 short video clips depicting clear, simple actions (walking, opening a door, pouring water).
    2.  **Establish Ground Truth:** For each video, manually write the ideal, single-sentence action description (e.g., "A person is opening a refrigerator.").
    3.  **Run the Pipeline:** Process each video through our AIris pipeline.
    4.  **Evaluate:** Compare the AI-generated sentence to the ground truth. We can score this on a 0-2 scale (0=Incorrect, 1=Partially Correct, 2=Fully Correct) to calculate an overall ADA score.

### 7.2. Research and Curate Relevant Datasets

Our current test videos are generic. To align with the project's goal, we need data that simulates the experience of a visually impaired user.

*   **Objective:** Find and curate video datasets with an ego-centric (first-person) point of view, focusing on daily activities.
*   **Search Keywords:** "Ego-centric video dataset," "first-person activity recognition," "assistive technology video dataset," "daily life activities dataset."
*   **Potential Datasets to Investigate:**
    *   **Ego4D:** A massive-scale dataset of daily life activity video.
    *   **EPIC-KITCHENS:** Focused on first-person interactions in a kitchen environment.
    *   **Charades-Ego:** An ego-centric version of the Charades dataset, focusing on activities.

### 7.3. Continued Development

*   **Implement Robust Anomaly Filtering:** While our prompt engineering helps, the next logical code improvement is to implement the statistical anomaly filtering discussed previously to provide an even cleaner input to the LLM.
*   **Implement Ollama Backend:** Complete the work on the `summarize_with_ollama` function to enable a fully offline version of this advanced pipeline.
*   **Transition to Real-Time Feed:** Begin adapting the `app.py` logic to accept a live webcam feed as input, preparing for the final hardware integration.