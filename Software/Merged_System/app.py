# /AIris_Unified_Platform/unified_app.py

import cv2
import streamlit as st
from ultralytics import YOLO
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv
from groq import Groq
import ast
import time
import json
from datetime import datetime
from gtts import gTTS
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# --- 1. Configuration & Initialization ---
load_dotenv()

# --- Model & File Paths ---
YOLO_MODEL_PATH = 'yolov8n.pt'
FONT_PATH = 'RobotoCondensed-Regular.ttf'
RECORDINGS_DIR = 'recordings'
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# --- Activity Guide Constants ---
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.1
GUIDANCE_UPDATE_INTERVAL_SEC = 2 

# --- Scene Description Constants ---
RECORDING_SPAN_MINUTES = 30 # Duration of each recording session
FRAME_ANALYSIS_INTERVAL_SEC = 10 # How often to describe a frame
SUMMARIZATION_BUFFER_SIZE = 3 # Number of frame descriptions to collect before summarizing

# --- Initialize Groq Client ---
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    st.error(f"Failed to initialize Groq client. Is your GROQ_API_KEY set in the .env file? Error: {e}")
    groq_client = None

# --- 2. Model Loading (Cached for Performance) ---
@st.cache_resource
def load_yolo_model(model_path):
    try: return YOLO(model_path)
    except Exception as e: st.error(f"Error loading YOLO model: {e}"); return None

@st.cache_resource
def load_hand_model():
    mp_hands = mp.solutions.hands
    return mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=1)

@st.cache_resource
def load_font(font_path, size=24):
    try: return ImageFont.truetype(font_path, size)
    except IOError:
        st.error(f"Font file not found at {font_path}. Using default font.")
        return ImageFont.load_default()

@st.cache_resource
def load_vision_model():
    """Loads the BLIP model for image captioning."""
    print("Initializing BLIP vision model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-large"
    ).to(device)
    print("BLIP vision model loaded successfully.")
    return processor, model, device

# --- 3. Helper and LLM Functions ---
def get_groq_response(prompt, model="openai/gpt-oss-120b"):
    if not groq_client: return "LLM Client not initialized."
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling Groq API: {e}"); return f"Error: {e}"

def text_to_speech(text):
    """Converts text to speech and plays it in the Streamlit app."""
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("temp_audio.mp3")
        st.audio("temp_audio.mp3", autoplay=True)
        os.remove("temp_audio.mp3")
    except Exception as e:
        st.error(f"TTS failed: {e}")

def save_log_to_json(log_data, filename):
    """Saves the recording log to a JSON file."""
    filepath = os.path.join(RECORDINGS_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(log_data, f, indent=4)
    print(f"Log saved to {filepath}")
    
# --- 4. Activity Guide Mode ---
# (This section is mostly from the original activity.py, adapted for the unified app)

def run_activity_guide(frame, yolo_model, hand_model):
    """Main logic for the Activity Guide mode for a single frame."""
    custom_font = load_font(FONT_PATH)
    mp_drawing = mp.solutions.drawing_utils
    
    yolo_results = yolo_model.track(frame, persist=True, conf=CONFIDENCE_THRESHOLD, verbose=False)
    annotated_frame = yolo_results[0].plot(line_width=2)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_results = hand_model.process(rgb_frame)
    hand_box = None
    if mp_results.multi_hand_landmarks:
        for hand_landmarks in mp_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(annotated_frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape
            coords = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
            x_min, y_min = np.min(coords, axis=0); x_max, y_max = np.max(coords, axis=0)
            hand_box = [int(x_min * w), int(y_min * h), int(x_max * w), int(y_max * h)]

    # --- State Machine Logic (same as original) ---
    stage = st.session_state.guidance_stage
    
    if stage == 'IDLE':
        update_instruction("Camera is on. Enter a task below to begin.")
    elif stage == 'FINDING_OBJECT':
        target_options = st.session_state.target_objects
        detected_objects = {yolo_model.names[int(cls)]: box.cpu().numpy().astype(int) 
                            for box, cls in zip(yolo_results[0].boxes.xyxy, yolo_results[0].boxes.cls)}
        
        found_target = next((target for target in target_options if target in detected_objects), None)
        
        if found_target:
            target_box = detected_objects[found_target]
            if calculate_iou(hand_box, target_box) > IOU_THRESHOLD:
                update_instruction(f"It looks like you're already holding the {found_target}. Task complete!")
                st.session_state.guidance_stage = 'DONE'
            else:
                st.session_state.found_object_location = target_box
                location_desc = describe_location(target_box, frame.shape[1])
                update_instruction(f"Great, I see the {found_target} {location_desc}. Please move your hand towards it.")
                st.session_state.guidance_stage = 'GUIDING_HAND'
        else:
            update_instruction(f"I am looking for a {target_options[0]}. Please scan the area.")
    
    elif stage == 'GUIDING_HAND':
        target_box = st.session_state.found_object_location
        cv2.rectangle(annotated_frame, (target_box[0], target_box[1]), (target_box[2], target_box[3]), (0, 255, 255), 3)

        if hand_box is not None:
            if calculate_iou(hand_box, target_box) > IOU_THRESHOLD:
                st.session_state.guidance_stage = 'DONE'
            elif time.time() - st.session_state.last_guidance_time > GUIDANCE_UPDATE_INTERVAL_SEC:
                prompt = f"""A visually impaired user is trying to grab a '{st.session_state.target_objects[0]}'. The object is located {describe_location(target_box, frame.shape[1])}. Their hand is currently {describe_location(hand_box, frame.shape[1])}. Give a very short, clear, one-sentence instruction to guide their hand to the object. Example: 'Move your hand slightly to the right.'"""
                llm_guidance = get_groq_response(prompt)
                update_instruction(llm_guidance)
                st.session_state.last_guidance_time = time.time()
        else:
            update_instruction("I can't see your hand. Please bring it into view.")

    elif stage == 'DONE':
        if not st.session_state.get('task_done_displayed', False):
            update_instruction("Task Completed Successfully!")
            st.balloons()
            st.session_state.task_done_displayed = True
    
    # Draw instruction on frame and return
    final_frame = draw_guidance_on_frame(annotated_frame, st.session_state.current_instruction, custom_font)
    return final_frame

def update_instruction(new_instruction):
    st.session_state.current_instruction = new_instruction
    if not st.session_state.instruction_history or st.session_state.instruction_history[-1] != new_instruction:
        st.session_state.instruction_history.append(new_instruction)

def calculate_iou(boxA, boxB):
    if boxA is None or boxB is None: return 0
    xA = max(boxA[0], boxB[0]); yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2]); yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    denominator = float(boxAArea + boxBArea - interArea)
    return interArea / denominator if denominator != 0 else 0

def describe_location(box, frame_width):
    center_x = (box[0] + box[2]) / 2
    if center_x < frame_width / 3: return "on your left"
    elif center_x > 2 * frame_width / 3: return "on your right"
    else: return "in front of you"

def draw_guidance_on_frame(frame, text, font):
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    text_bbox = draw.textbbox((0,0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    draw.rectangle([10, 10, 20 + text_width, 20 + text_height], fill="black")
    draw.text((15, 15), text, font=font, fill="white")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

# --- 5. Scene Description Mode ---
# (This section contains the new logic based on your requirements)

def describe_frame_with_blip(frame, processor, model, device):
    """Generates a caption for a single image frame using BLIP."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb_frame)
    inputs = processor(images=image, return_tensors="pt").to(device)
    generated_ids = model.generate(**inputs, max_length=50)
    caption = processor.decode(generated_ids[0], skip_special_tokens=True)
    return caption.strip()

def summarize_descriptions(descriptions):
    """Uses Groq LLM to summarize a sequence of frame descriptions into a single action."""
    prompt_content = ". ".join(descriptions)
    system_prompt = (
        "You are a motion analysis expert AI. Your purpose is to describe what is HAPPENING, not just what is THERE. "
        "I will provide a sequence of static observations. Your task is to infer the single most likely action or movement that connects them. "
        "Deduce the verb or action that describes the transition. Your response MUST be ONLY the summary sentence describing the action, with no preamble. "
        "Example: ['a person is standing', 'a person is lifting their foot'] -> 'A person is starting to walk.'"
    )
    full_prompt = f"{system_prompt}\n\nObservations: {prompt_content}\n\nSummary:"
    return get_groq_response(full_prompt)

def check_for_safety_alert(summary):
    """Uses an LLM to flag potentially harmful events."""
    prompt = (
        f"Analyze the following event description for potential harm, distress, or accidents involving a person. "
        f"Respond with only the word 'HARMFUL' if it contains events like falling, crashing, fire, injury, shouting for help, or any dangerous situation. "
        f"Otherwise, respond with only the word 'SAFE'.\n\nEvent: '{summary}'"
    )
    response = get_groq_response(prompt, model="openai/gpt-oss-120b").strip().upper()
    return "HARMFUL" in response

def run_scene_description(frame, vision_processor, vision_model, device):
    """Main logic for the Scene Description mode for a single frame."""
    
    # Check if it's time to end the current recording session
    if time.time() - st.session_state.recording_start_time > RECORDING_SPAN_MINUTES * 60:
        st.session_state.is_recording = False
        save_log_to_json(st.session_state.current_session_log, st.session_state.log_filename)
        st.toast(f"Recording session ended. Log saved to {st.session_state.log_filename}")
        # Reset for a potential new session
        st.session_state.current_session_log = {}
        st.session_state.log_filename = ""
        st.session_state.frame_description_buffer = []
        return frame # Return original frame as we are no longer processing

    # Check if it's time to analyze a new frame
    if time.time() - st.session_state.last_frame_analysis_time > FRAME_ANALYSIS_INTERVAL_SEC:
        st.session_state.last_frame_analysis_time = time.time()
        
        # 1. Get raw description from BLIP
        description = describe_frame_with_blip(frame, vision_processor, vision_model, device)
        st.session_state.frame_description_buffer.append(description)
        
        # 2. If buffer is full, summarize and log
        if len(st.session_state.frame_description_buffer) >= SUMMARIZATION_BUFFER_SIZE:
            descriptions_to_summarize = list(set(st.session_state.frame_description_buffer)) # Deduplicate
            
            summary = summarize_descriptions(descriptions_to_summarize)
            is_harmful = check_for_safety_alert(summary)
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "summary": summary,
                "raw_descriptions": descriptions_to_summarize,
                "flag": "SAFETY_ALERT" if is_harmful else "None"
            }
            
            st.session_state.current_session_log["events"].append(log_entry)
            st.session_state.frame_description_buffer = [] # Clear buffer
            
            if is_harmful:
                st.toast("⚠️ Safety Alert Triggered!", icon="🚨")

    # Display status on frame
    font = load_font(FONT_PATH, 20)
    status_text = f"🔴 RECORDING... | Session ends in {RECORDING_SPAN_MINUTES - (time.time() - st.session_state.recording_start_time)/60:.1f} mins"
    annotated_frame = draw_guidance_on_frame(frame, status_text, font)
    return annotated_frame


# --- 6. Main Application UI and Execution Loop ---
st.set_page_config(page_title="AIris Unified Platform", layout="wide")
st.title("👁️ AIris: Unified Assistance Platform")

# --- Initialize Session State ---
# General state
if 'run_camera' not in st.session_state: st.session_state.run_camera = False
if 'mode' not in st.session_state: st.session_state.mode = "Activity Guide"

# Activity Guide State
if 'guidance_stage' not in st.session_state: st.session_state.guidance_stage = "IDLE"
if 'current_instruction' not in st.session_state: st.session_state.current_instruction = "Start the camera and enter a task."
if 'instruction_history' not in st.session_state: st.session_state.instruction_history = []
if 'target_objects' not in st.session_state: st.session_state.target_objects = []
if 'found_object_location' not in st.session_state: st.session_state.found_object_location = None
if 'last_guidance_time' not in st.session_state: st.session_state.last_guidance_time = 0

# Scene Description State
if 'is_recording' not in st.session_state: st.session_state.is_recording = False
if 'recording_start_time' not in st.session_state: st.session_state.recording_start_time = 0
if 'last_frame_analysis_time' not in st.session_state: st.session_state.last_frame_analysis_time = 0
if 'current_session_log' not in st.session_state: st.session_state.current_session_log = {}
if 'log_filename' not in st.session_state: st.session_state.log_filename = ""
if 'frame_description_buffer' not in st.session_state: st.session_state.frame_description_buffer = []

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Mode Selection")
    st.radio("Select Mode", ["Activity Guide", "Scene Description"], key="mode")
    
    st.divider()
    
    st.header("Camera Controls")
    source_selection = st.radio("Select Camera Source", ["Webcam", "DroidCam URL"])
    source_path = 0 if source_selection == "Webcam" else st.text_input("DroidCam IP URL", "http://192.168.1.5:4747/video")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Camera"): 
            st.session_state.run_camera = True
    with col2:
        if st.button("Stop Camera"): 
            st.session_state.run_camera = False
            # If we were recording, log the interruption
            if st.session_state.get('is_recording', False):
                st.session_state.current_session_log["events"].append({
                    "timestamp": datetime.now().isoformat(),
                    "event": "recording_paused",
                    "reason": "Camera turned off by user."
                })
                st.toast("Recording paused.")

# --- Main Content Area based on Mode ---
video_placeholder = st.empty()

if st.session_state.mode == "Activity Guide":
    # UI for Activity Guide
    st.header("Activity Guide")
    col1, col2 = st.columns([2, 3])

    def start_task():
        if not st.session_state.run_camera:
            st.toast("Please start the camera first!", icon="📷"); return
        goal = st.session_state.user_goal_input
        if not goal:
            st.toast("Please enter a task description.", icon="✍️"); return
        
        st.session_state.instruction_history = []
        st.session_state.task_done_displayed = False
        update_instruction(f"Okay, processing your request to: '{goal}'...")
        
        prompt = f"""A user wants to perform the task: '{goal}'. What single, primary physical object do they need to find first? Respond with a Python list of possible string names for that object. Keep it simple. Examples: 'drink water' -> ['bottle', 'cup', 'mug']. 'read a book' -> ['book']. 'call someone' -> ['cell phone']"""
        response = get_groq_response(prompt)
        try:
            target_list = ast.literal_eval(response)
            if isinstance(target_list, list) and len(target_list) > 0:
                st.session_state.target_objects = target_list
                st.session_state.guidance_stage = "FINDING_OBJECT"
                update_instruction(f"Okay, let's find the {target_list[0]}.")
            else:
                update_instruction("Sorry, I couldn't determine the object for that task. Please rephrase.")
        except (ValueError, SyntaxError):
            update_instruction(f"Sorry, I had trouble understanding the task. Response: {response}")

    with col1:
        st.text_input("Enter the task you want to perform:", key="user_goal_input", on_change=start_task)
        st.button("Start Task", on_click=start_task)

    with col2:
        st.subheader("Guidance Log")
        log_container = st.container(height=200)
        for i, instruction in enumerate(st.session_state.instruction_history):
            log_container.markdown(f"**{i+1}.** {instruction}")
            
elif st.session_state.mode == "Scene Description":
    # UI for Scene Description
    st.header("Scene Description Logger")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("▶️ Start Recording", disabled=st.session_state.is_recording):
            if not st.session_state.run_camera:
                st.toast("Please start the camera first!", icon="📷")
            else:
                st.session_state.is_recording = True
                st.session_state.recording_start_time = time.time()
                st.session_state.last_frame_analysis_time = time.time() # Start analyzing immediately
                filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                st.session_state.log_filename = filename
                st.session_state.current_session_log = {
                    "session_start": datetime.now().isoformat(),
                    "duration_minutes": RECORDING_SPAN_MINUTES,
                    "events": []
                }
                # Log if recording was resumed
                if st.session_state.get('log_filename', ''): # Check if there was a previous session
                     st.session_state.current_session_log["events"].append({
                        "timestamp": datetime.now().isoformat(), "event": "recording_resumed"
                     })
                st.toast(f"Recording started. Session will last {RECORDING_SPAN_MINUTES} minutes.")

    with col2:
        if st.button("⏹️ Stop & Save Recording", disabled=not st.session_state.is_recording):
            st.session_state.is_recording = False
            st.session_state.current_session_log["session_end"] = datetime.now().isoformat()
            save_log_to_json(st.session_state.current_session_log, st.session_state.log_filename)
            st.toast(f"Recording stopped. Log saved to {st.session_state.log_filename}")
            st.session_state.current_session_log = {}
    
    with col3:
        if st.button("🔊 Hear Last Description"):
            if st.session_state.get('current_session_log', {}).get('events'):
                # Mark trigger in log
                st.session_state.current_session_log["events"].append({"timestamp": datetime.now().isoformat(), "event": "description_triggered"})
                
                # Find the last summary
                last_summary = "No summary has been generated yet."
                for event in reversed(st.session_state.current_session_log["events"]):
                    if "summary" in event:
                        last_summary = event["summary"]
                        break
                text_to_speech(last_summary)
                
                # Mark end in log
                st.session_state.current_session_log["events"].append({"timestamp": datetime.now().isoformat(), "event": "description_ended"})
            else:
                st.toast("No descriptions have been recorded yet.")
    
    # Display the current log
    st.subheader("Live Recording Log")
    log_display = st.container(height=300)
    if st.session_state.get('is_recording', False):
        log_display.json(st.session_state.current_session_log)


# --- Main Execution Loop ---
if st.session_state.run_camera:
    video_placeholder.empty()
    FRAME_WINDOW = st.image([])
    
    # Load models only when camera is on
    yolo_model = load_yolo_model(YOLO_MODEL_PATH)
    hand_model = load_hand_model()
    vision_processor, vision_model, device = load_vision_model()

    vid_cap = cv2.VideoCapture(source_path)
    if not vid_cap.isOpened():
        st.error(f"Error opening camera source '{source_path}'.")
        st.session_state.run_camera = False
    
    while vid_cap.isOpened() and st.session_state.run_camera:
        success, frame = vid_cap.read()
        if not success:
            st.warning("Stream ended."); break

        # Route frame to the correct processing function based on mode
        if st.session_state.mode == "Activity Guide":
            processed_frame = run_activity_guide(frame, yolo_model, hand_model)
        elif st.session_state.mode == "Scene Description" and st.session_state.is_recording:
            processed_frame = run_scene_description(frame, vision_processor, vision_model, device)
        else:
            processed_frame = frame # If not recording, show the raw frame
        
        # Display the processed frame
        FRAME_WINDOW.image(cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB))
    
    vid_cap.release()
else:
    video_placeholder.info("Camera is off. Use the sidebar to start the camera feed.")