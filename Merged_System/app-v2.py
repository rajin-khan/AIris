# --- START OF FILE app-v2.py ---

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
import re
import yaml
import base64

# --- 0. Page Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(page_title="AIris Unified Platform", layout="wide")

# --- 1. Configuration & Initialization ---
load_dotenv()

@st.cache_data
def load_prompts(filepath='config.yaml'):
    try:
        with open(filepath, 'r') as file: 
            return yaml.safe_load(file)
    except Exception as e:
        st.error(f"Error loading config.yaml: {e}. Please ensure it exists and is valid.")
        return {}

PROMPTS = load_prompts()

# --- Model & File Paths & Constants ---
YOLO_MODEL_PATH = 'yolov8s.pt'
FONT_PATH = 'RobotoCondensed-Regular.ttf'
RECORDINGS_DIR = 'recordings'
os.makedirs(RECORDINGS_DIR, exist_ok=True)
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.15
GUIDANCE_UPDATE_INTERVAL_SEC = 3
RECORDING_SPAN_MINUTES = 30
FRAME_ANALYSIS_INTERVAL_SEC = 10
SUMMARIZATION_BUFFER_SIZE = 3

# --- Initialize Groq Client ---
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    st.error(f"Failed to initialize Groq client. Is your GROQ_API_KEY set? Error: {e}")
    groq_client = None

# --- 2. Model Loading (Cached for Performance) ---
@st.cache_resource
def load_yolo_model(model_path):
    try: 
        return YOLO(model_path)
    except Exception as e: 
        st.error(f"Error loading YOLO model: {e}")
        return None

@st.cache_resource
def load_hand_model():
    mp_hands = mp.solutions.hands
    return mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2)

@st.cache_resource
def load_font(font_path, size=24):
    try: 
        return ImageFont.truetype(font_path, size)
    except IOError:
        st.warning(f"Font file not found at {font_path}. Using default font.")
        return ImageFont.load_default()

@st.cache_resource
def load_vision_model():
    print("Initializing BLIP vision model...")
    if torch.cuda.is_available(): 
        device = "cuda"
    elif torch.backends.mps.is_available(): 
        device = "mps"
    else: 
        device = "cpu"
    print(f"BLIP using device: {device}")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)
    return processor, model, device

# --- 3. Helper and LLM Functions ---
def get_groq_response(prompt, system_prompt="You are a helpful assistant.", model="openai/gpt-oss-120b"):
    if not groq_client: 
        return "LLM Client not initialized."
    try:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        chat_completion = groq_client.chat.completions.create(messages=messages, model=model)
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling Groq API: {e}")
        return f"Error: {e}"

def text_to_speech(text):
    """Generate TTS and store as base64 in session state"""
    if text:
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            audio_file = "temp_audio.mp3"
            tts.save(audio_file)
            
            # Read the file and convert to base64 immediately
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            
            # Store base64 in session state
            st.session_state.audio_base64 = audio_base64
            st.session_state.audio_ready = True
            
            # Clean up temp file immediately
            try:
                os.remove(audio_file)
            except:
                pass
                
        except Exception as e:
            st.error(f"TTS failed: {e}")

def describe_location_detailed(box, frame_shape):
    h, w = frame_shape[:2]
    center_x, center_y = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    h_pos = "to your left" if center_x < w / 3 else "to your right" if center_x > 2 * w / 3 else "in front of you"
    v_pos = "in the upper part" if center_y < h / 3 else "in the lower part" if center_y > 2 * h / 3 else "at chest level"
    relative_area = ((box[2] - box[0]) * (box[3] - box[1])) / (w * h)
    dist = "and appears very close" if relative_area > 0.1 else "and appears to be within reach" if relative_area > 0.03 else "and seems a bit further away"
    return f"{v_pos} and {h_pos}, {dist}" if h_pos != "in front of you" else f"{h_pos}, {v_pos}, {dist}"

def get_box_center(box):
    """Calculate center of a bounding box"""
    return [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]

def draw_guidance_on_frame(frame, text, font):
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    if text:
        try:
            text_bbox = draw.textbbox((0,0), text, font=font)
            text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)
        draw.rectangle([10, 10, 20 + text_width, 20 + text_height], fill="black")
        draw.text((15, 15), text, font=font, fill="white")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def calculate_iou(boxA, boxB):
    if not all(isinstance(i, (int, float)) for i in boxA + boxB): 
        return 0
    xA, yA = max(boxA[0], boxB[0]), max(boxA[1], boxB[1])
    xB, yB = min(boxA[2], boxB[2]), min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    denominator = float(boxAArea + boxBArea - interArea)
    return interArea / denominator if denominator != 0 else 0

def update_instruction(new_instruction, speak=False):
    st.session_state.last_guidance_time = time.time()
    if st.session_state.current_instruction != new_instruction:
        st.session_state.current_instruction = new_instruction
        st.session_state.instruction_history.append(new_instruction)
        if speak:
            text_to_speech(new_instruction)

def save_log_to_json(log_data, filename):
    filepath = os.path.join(RECORDINGS_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(log_data, f, indent=4)
    print(f"Log saved to {filepath}")

# --- 4. Core Logic for Both Modes ---
def run_activity_guide(frame, yolo_model, hand_model):
    custom_font = load_font(FONT_PATH)
    yolo_results = yolo_model.track(frame, persist=True, conf=CONFIDENCE_THRESHOLD, verbose=False)
    annotated_frame = yolo_results[0].plot(line_width=2)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_results = hand_model.process(rgb_frame)
    detected_hands = []
    if mp_results.multi_hand_landmarks:
        for hand_landmarks in mp_results.multi_hand_landmarks:
            h, w, _ = frame.shape
            coords = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
            x_min, y_min = np.min(coords, axis=0)
            x_max, y_max = np.max(coords, axis=0)
            current_hand_box = [int(x_min * w), int(y_min * h), int(x_max * w), int(y_max * h)]
            detected_hands.append({'box': current_hand_box})
            mp.solutions.drawing_utils.draw_landmarks(
                annotated_frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
    
    stage = st.session_state.guidance_stage
    primary_target = st.session_state.target_objects[0] if st.session_state.target_objects else None
    
    if time.time() - st.session_state.last_guidance_time > GUIDANCE_UPDATE_INTERVAL_SEC and stage not in ['IDLE', 'DONE', 'AWAITING_FEEDBACK']:
        if stage == 'FINDING_OBJECT':
            detected_objects = {yolo_model.names[int(cls)]: box.cpu().numpy().tolist() for box, cls in zip(yolo_results[0].boxes.xyxy, yolo_results[0].boxes.cls)}
            found_target_name = next((target for target in st.session_state.target_objects if target in detected_objects), None)
            if found_target_name:
                st.session_state.found_object_location = detected_objects[found_target_name]
                verification_needed = (primary_target, found_target_name) in st.session_state.verification_pairs
                if verification_needed:
                    instruction = f"I see something that could be the {primary_target}, but it looks like a {found_target_name}. I will guide you to it for verification."
                    update_instruction(instruction, speak=True)
                    st.session_state.next_stage_after_guiding = 'VERIFYING_OBJECT'
                    st.session_state.guidance_stage = 'GUIDING_TO_PICKUP'
                else:
                    location_desc = describe_location_detailed(st.session_state.found_object_location, frame.shape)
                    instruction = f"Great, I see the {primary_target} {location_desc}. I will now guide your hand to it."
                    update_instruction(instruction, speak=True)
                    st.session_state.next_stage_after_guiding = 'CONFIRMING_PICKUP'
                    st.session_state.guidance_stage = 'GUIDING_TO_PICKUP'
            else: 
                update_instruction(f"I am looking for the {primary_target}. Please scan the area.")
        elif stage == 'GUIDING_TO_PICKUP':
            target_box = st.session_state.found_object_location
            if not detected_hands:
                update_instruction("I can't see your hand. Please bring it into view.", speak=True)
            else:
                target_center = get_box_center(target_box)
                closest_hand = min(detected_hands, key=lambda h: np.linalg.norm(np.array(target_center) - np.array(get_box_center(h['box']))))
                if calculate_iou(closest_hand['box'], target_box) > IOU_THRESHOLD:
                    st.session_state.guidance_stage = st.session_state.next_stage_after_guiding
                else:
                    system_prompt = PROMPTS['activity_guide']['guidance_system']
                    user_prompt = PROMPTS['activity_guide']['guidance_user'].format(
                        hand_location=describe_location_detailed(closest_hand['box'], frame.shape), 
                        primary_target=primary_target, 
                        object_location=describe_location_detailed(target_box, frame.shape)
                    )
                    llm_guidance = get_groq_response(user_prompt, system_prompt)
                    update_instruction(llm_guidance, speak=True)

    if st.session_state.found_object_location and stage == 'GUIDING_TO_PICKUP':
        box = st.session_state.found_object_location
        cv2.rectangle(annotated_frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 255), 3)

    if stage in ['CONFIRMING_PICKUP', 'VERIFYING_OBJECT']:
        instruction = f"Your hand is at the {'object' if stage == 'VERIFYING_OBJECT' else primary_target}. Can you confirm if this is correct? Please use the Yes or No buttons."
        update_instruction(instruction, speak=True)
        st.session_state.guidance_stage = 'AWAITING_FEEDBACK'
    
    if stage == 'DONE' and not st.session_state.get('task_done_displayed', False):
        update_instruction("Task Completed Successfully!", speak=True)
        st.balloons()
        st.session_state.task_done_displayed = True
        
    return draw_guidance_on_frame(annotated_frame, st.session_state.current_instruction, custom_font)

def run_scene_description(frame, vision_processor, vision_model, device):
    if time.time() - st.session_state.recording_start_time > RECORDING_SPAN_MINUTES * 60:
        st.session_state.is_recording = False
        save_log_to_json(st.session_state.current_session_log, st.session_state.log_filename)
        st.toast(f"Recording session ended. Log saved to {st.session_state.log_filename}")
        st.session_state.current_session_log = {}
        return frame
    if time.time() - st.session_state.last_frame_analysis_time > FRAME_ANALYSIS_INTERVAL_SEC:
        st.session_state.last_frame_analysis_time = time.time()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_frame)
        inputs = vision_processor(images=image, return_tensors="pt").to(device)
        generated_ids = vision_model.generate(**inputs, max_length=50)
        description = vision_processor.decode(generated_ids[0], skip_special_tokens=True).strip()
        st.session_state.frame_description_buffer.append(description)
        if len(st.session_state.frame_description_buffer) >= SUMMARIZATION_BUFFER_SIZE:
            descriptions = list(set(st.session_state.frame_description_buffer))
            system_prompt = PROMPTS['scene_description']['summarization_system']
            user_prompt = PROMPTS['scene_description']['summarization_user'].format(observations=". ".join(descriptions))
            summary = get_groq_response(user_prompt, system_prompt=system_prompt)
            safety_prompt = PROMPTS['scene_description']['safety_alert_user'].format(summary=summary)
            is_harmful = "HARMFUL" in get_groq_response(safety_prompt).strip().upper()
            log_entry = {
                "timestamp": datetime.now().isoformat(), 
                "summary": summary, 
                "raw_descriptions": descriptions, 
                "flag": "SAFETY_ALERT" if is_harmful else "None"
            }
            st.session_state.current_session_log["events"].append(log_entry)
            st.session_state.frame_description_buffer = []
            if is_harmful: 
                st.toast("⚠️ Safety Alert Triggered!", icon="🚨")
    font = load_font(FONT_PATH, 20)
    status_text = f"🔴 RECORDING... | Session ends in {RECORDING_SPAN_MINUTES - (time.time() - st.session_state.recording_start_time)/60:.1f} mins"
    return draw_guidance_on_frame(frame, status_text, font)

# --- 5. Main Application ---
st.title("👁️ AIris: Unified Assistance Platform")

# Initialize session state for BOTH modes
for key, default_value in [
    ('mode', "Activity Guide"), ('run_camera', False),
    ('guidance_stage', "IDLE"), ('current_instruction', "Start the camera and enter a task."),
    ('instruction_history', []), ('target_objects', []), ('found_object_location', None),
    ('last_guidance_time', 0), ('audio_base64', None), ('audio_ready', False),
    ('verification_pairs', []), ('next_stage_after_guiding', ''), ('task_done_displayed', False),
    ('is_recording', False), ('recording_start_time', 0), ('last_frame_analysis_time', 0),
    ('current_session_log', {}), ('log_filename', ""), ('frame_description_buffer', [])
]:
    if key not in st.session_state: 
        st.session_state[key] = default_value

if 'vid_cap' not in st.session_state:
    st.session_state.vid_cap = None

# --- UI Setup ---
with st.sidebar:
    st.header("Mode Selection")
    st.radio("Select Mode", ["Activity Guide", "Scene Description"], key="mode",
             disabled=(st.session_state.guidance_stage not in ['IDLE', 'DONE'] and st.session_state.mode == "Activity Guide"))
    st.divider()
    st.header("Camera Controls")
    if st.button("Start Camera", disabled=st.session_state.run_camera):
        st.session_state.run_camera = True
        st.rerun()
    if st.button("Stop Camera", disabled=not st.session_state.run_camera):
        st.session_state.run_camera = False
        if st.session_state.vid_cap:
            st.session_state.vid_cap.release()
            st.session_state.vid_cap = None
        st.rerun()
    st.divider()

    if st.session_state.mode == "Activity Guide":
        st.header("Task Input")
        OBJECT_ALIASES = {"cell phone": ["remote"], "watch": ["clock"], "bottle": ["cup", "mug"]}
        VERIFICATION_PAIRS = [("cell phone", "remote"), ("watch", "clock")]
        def start_task():
            if not st.session_state.run_camera:
                st.toast("Please start the camera first!")
                return
            goal = st.session_state.user_goal_input
            if not goal: 
                return
            st.session_state.instruction_history, st.session_state.task_done_displayed = [], False
            update_instruction(f"Okay, processing: '{goal}'...")
            prompt = PROMPTS['activity_guide']['object_extraction'].format(goal=goal)
            response = get_groq_response(prompt)
            try:
                match = re.search(r"\[.*?\]", response)
                if match:
                    target_list = ast.literal_eval(match.group(0))
                    if isinstance(target_list, list) and target_list:
                        primary_target = target_list[0]
                        st.session_state.verification_pairs = VERIFICATION_PAIRS
                        if primary_target in OBJECT_ALIASES:
                            target_list.extend(OBJECT_ALIASES[primary_target])
                        st.session_state.target_objects = list(set(target_list))
                        st.session_state.guidance_stage = "FINDING_OBJECT"
                        update_instruction(f"Okay, let's find the {primary_target}.", speak=True)
                    else: 
                        update_instruction("Sorry, I couldn't determine an object for that task.", speak=True)
                else: 
                    update_instruction("Sorry, I couldn't parse the object from the response.", speak=True)
            except (ValueError, SyntaxError): 
                update_instruction("Sorry, I had trouble understanding the task.", speak=True)
        st.text_input("Enter a task:", key="user_goal_input", on_change=start_task, 
                     disabled=(st.session_state.guidance_stage not in ['IDLE', 'DONE']))
        st.button("Start Task", on_click=start_task, 
                 disabled=(st.session_state.guidance_stage not in ['IDLE', 'DONE']))
        st.divider()
        st.header("Guidance Log")
        log_container = st.container(height=300)

    elif st.session_state.mode == "Scene Description":
        st.header("Recording Controls")
        if st.button("▶️ Start Recording", disabled=st.session_state.is_recording):
            if not st.session_state.run_camera: 
                st.toast("Please start the camera first!")
            else:
                st.session_state.is_recording = True
                st.session_state.recording_start_time = time.time()
                st.session_state.last_frame_analysis_time = time.time()
                st.session_state.log_filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                st.session_state.current_session_log = {"session_start": datetime.now().isoformat(), "events": []}
                st.toast(f"Recording started.")
        if st.button("⏹️ Stop & Save", disabled=not st.session_state.is_recording):
            st.session_state.is_recording = False
            if st.session_state.current_session_log:
                st.session_state.current_session_log["session_end"] = datetime.now().isoformat()
                save_log_to_json(st.session_state.current_session_log, st.session_state.log_filename)
                st.toast(f"Log saved to {st.session_state.log_filename}")
                st.session_state.current_session_log = {}
        if st.button("📊 Hear Last Description"):
            if st.session_state.current_session_log.get('events'):
                last_summary = next((e["summary"] for e in reversed(st.session_state.current_session_log["events"]) if "summary" in e), "No summary yet.")
                text_to_speech(last_summary)
            else: 
                st.toast("No descriptions recorded yet.")

# Create persistent placeholders OUTSIDE of any container context
if 'feedback_placeholder' not in st.session_state:
    st.session_state.feedback_placeholder = st.empty()

if 'frame_placeholder' not in st.session_state:
    st.session_state.frame_placeholder = st.empty()

# Main content area
main_area = st.container()
with main_area:
    # Handle feedback section in persistent placeholder
    if st.session_state.mode == "Activity Guide":
        if st.session_state.guidance_stage == 'AWAITING_FEEDBACK':
            with st.session_state.feedback_placeholder.container():
                st.warning("Waiting for your response...")
                fb_col1, fb_col2 = st.columns(2)
                with fb_col1:
                    if st.button("✅ Yes", use_container_width=True):
                        update_instruction(f"Great, task complete!", speak=True)
                        st.session_state.guidance_stage = 'DONE'
                        st.session_state.feedback_placeholder.empty()
                        st.rerun()
                with fb_col2:
                    if st.button("❌ No", use_container_width=True):
                        update_instruction("Okay, let's try again. I will scan for the object.", speak=True)
                        st.session_state.guidance_stage = 'FINDING_OBJECT'
                        st.session_state.found_object_location = None
                        st.session_state.feedback_placeholder.empty()
                        st.rerun()
        else:
            st.session_state.feedback_placeholder.empty()

    elif st.session_state.mode == "Scene Description":
        st.header("Live Recording Log")
        log_display = st.container(height=400)
        if st.session_state.is_recording:
            log_display.json(st.session_state.current_session_log)

# Use the persistent frame placeholder
FRAME_WINDOW = st.session_state.frame_placeholder

# Audio player - using a placeholder container that only renders when audio is ready
if 'audio_placeholder' not in st.session_state:
    st.session_state.audio_placeholder = st.empty()

if st.session_state.audio_ready and st.session_state.audio_base64:
    with st.session_state.audio_placeholder.container():
        audio_html = f"""
            <audio autoplay style="display:none">
                <source src="data:audio/mp3;base64,{st.session_state.audio_base64}" type="audio/mpeg">
            </audio>
        """
        st.components.v1.html(audio_html, height=0)
    
    # Reset audio state after playing
    st.session_state.audio_ready = False
    st.session_state.audio_base64 = None

if st.session_state.mode == "Activity Guide":
    for i, instruction in enumerate(reversed(st.session_state.instruction_history)):
        log_container.markdown(f"**{len(st.session_state.instruction_history)-i}.** {instruction}")

# The "Virtual Loop" for real-time processing
if st.session_state.run_camera:
    # Initialize camera if not already initialized
    if st.session_state.vid_cap is None:
        with st.spinner("Initializing camera..."):
            st.session_state.vid_cap = cv2.VideoCapture(0)
            # Give camera time to initialize
            time.sleep(0.5)
            if not st.session_state.vid_cap.isOpened():
                st.error("Failed to open camera. Please check your camera connection.")
                st.session_state.run_camera = False
                st.session_state.vid_cap = None
                st.stop()
        # Camera just initialized, rerun to start processing
        st.rerun()
    
    yolo_model, hand_model = load_yolo_model(YOLO_MODEL_PATH), load_hand_model()
    vision_processor, vision_model, device = None, None, None

    success, frame = st.session_state.vid_cap.read()
    if success:
        if st.session_state.mode == "Activity Guide":
            processed_frame = run_activity_guide(frame, yolo_model, hand_model)
        elif st.session_state.mode == "Scene Description":
            if vision_model is None:
                vision_processor, vision_model, device = load_vision_model()
            if st.session_state.is_recording:
                processed_frame = run_scene_description(frame, vision_processor, vision_model, device)
            else:
                processed_frame = draw_guidance_on_frame(frame, "Scene Description: Recording Paused", load_font(FONT_PATH))
        else:
            processed_frame = frame
        
        # Convert to RGB for display
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        
        # Update the persistent image placeholder (no blinking!)
        FRAME_WINDOW.image(rgb_frame, channels="RGB", width='stretch')
        
        time.sleep(0.03)  # Smooth frame rate
        st.rerun()
    else:
        st.warning("Failed to read frame from camera. Please restart the camera.")
        st.session_state.run_camera = False
        if st.session_state.vid_cap:
            st.session_state.vid_cap.release()
        st.session_state.vid_cap = None
        st.rerun()
else:
    # Camera is off - clean up if needed
    if st.session_state.vid_cap is not None:
        st.session_state.vid_cap.release()
        st.session_state.vid_cap = None
    FRAME_WINDOW.empty()
    with FRAME_WINDOW.container():
        st.info("Camera is off. Use the sidebar to start the camera feed.")