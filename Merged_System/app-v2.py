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
RECORDING_SPAN_MINUTES = 30
FRAME_ANALYSIS_INTERVAL_SEC = 10
SUMMARIZATION_BUFFER_SIZE = 3

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
    # <--- MODIFICATION: Allow detection of up to 2 hands --->
    return mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2)

@st.cache_resource
def load_font(font_path, size=24):
    try: return ImageFont.truetype(font_path, size)
    except IOError:
        st.error(f"Font file not found at {font_path}. Using default font.")
        return ImageFont.load_default()

@st.cache_resource
def load_vision_model():
    print("Initializing BLIP vision model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)
    print("BLIP vision model loaded successfully.")
    return processor, model, device

# --- 3. Helper and LLM Functions ---
def draw_enhanced_hand_landmarks(image, hand_landmarks):
    LANDMARK_COLOR = (0, 255, 255)
    CONNECTION_COLOR = (255, 191, 0)
    overlay = image.copy()
    for connection in mp.solutions.hands.HAND_CONNECTIONS:
        start_idx, end_idx = connection
        h, w, _ = image.shape
        start_point = (int(hand_landmarks.landmark[start_idx].x * w), int(hand_landmarks.landmark[start_idx].y * h))
        end_point = (int(hand_landmarks.landmark[end_idx].x * w), int(hand_landmarks.landmark[end_idx].y * h))
        cv2.line(overlay, start_point, end_point, CONNECTION_COLOR, 3)
    for landmark in hand_landmarks.landmark:
        h, w, _ = image.shape
        cx, cy = int(landmark.x * w), int(landmark.y * h)
        cv2.circle(overlay, (cx, cy), 6, LANDMARK_COLOR, cv2.FILLED)
        cv2.circle(overlay, (cx, cy), 6, (0,0,0), 1)
    alpha = 0.7
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

# <--- NEW HELPER FUNCTION --->
def get_box_center(box):
    """Calculates the center coordinates of a bounding box."""
    return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2

def get_groq_response(prompt, model="llama-3.1-8b-instant"):
    if not groq_client: return "LLM Client not initialized."
    try:
        chat_completion = groq_client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=model)
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling Groq API: {e}"); return f"Error: {e}"

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("temp_audio.mp3")
        st.audio("temp_audio.mp3", autoplay=True)
        os.remove("temp_audio.mp3")
    except Exception as e:
        st.error(f"TTS failed: {e}")

def save_log_to_json(log_data, filename):
    filepath = os.path.join(RECORDINGS_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(log_data, f, indent=4)
    print(f"Log saved to {filepath}")

# --- 4. Activity Guide Mode ---
# <--- THIS ENTIRE FUNCTION IS REFACTORED FOR TWO-HAND LOGIC --->
def run_activity_guide(frame, yolo_model, hand_model):
    custom_font = load_font(FONT_PATH)
    yolo_results = yolo_model.track(frame, persist=True, conf=CONFIDENCE_THRESHOLD, verbose=False)
    annotated_frame = yolo_results[0].plot(line_width=2)
    
    # Process frame for hand detection
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_results = hand_model.process(rgb_frame)
    
    # Store detected hands information (box and label)
    detected_hands = []
    if mp_results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(mp_results.multi_hand_landmarks):
            # Draw skeleton for each detected hand
            annotated_frame = draw_enhanced_hand_landmarks(annotated_frame, hand_landmarks)
            
            # Calculate bounding box for the current hand
            h, w, _ = frame.shape
            coords = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
            x_min, y_min = np.min(coords, axis=0); x_max, y_max = np.max(coords, axis=0)
            current_hand_box = [int(x_min * w), int(y_min * h), int(x_max * w), int(y_max * h)]
            
            # Get handedness (Left/Right)
            label = mp_results.multi_handedness[idx].classification[0].label
            detected_hands.append({'box': current_hand_box, 'label': label})

    # This will be the hand used for guidance (the one closer to the target)
    active_hand_box = None
    
    stage = st.session_state.guidance_stage
    if stage == 'IDLE': 
        update_instruction("Camera is on. Enter a task below to begin.")
    
    elif stage in ['FINDING_OBJECT', 'GUIDING_HAND']:
        target_box = None
        if stage == 'FINDING_OBJECT':
            target_options = st.session_state.target_objects
            detected_objects = {yolo_model.names[int(cls)]: box.cpu().numpy().astype(int) for box, cls in zip(yolo_results[0].boxes.xyxy, yolo_results[0].boxes.cls)}
            found_target = next((target for target in target_options if target in detected_objects), None)
            
            if found_target:
                target_box = detected_objects[found_target]
                st.session_state.found_object_location = target_box # Save for guiding stage
            else:
                update_instruction(f"I am looking for a {target_options[0]}. Please scan the area.")
        else: # GUIDING_HAND stage
            target_box = st.session_state.found_object_location

        # If a target is visible, determine the active hand
        if target_box is not None:
            cv2.rectangle(annotated_frame, (target_box[0], target_box[1]), (target_box[2], target_box[3]), (0, 255, 255), 3) # Highlight target
            
            if len(detected_hands) == 1:
                active_hand_box = detected_hands[0]['box']
            elif len(detected_hands) == 2:
                # Find which hand is closer to the target object
                target_center = get_box_center(target_box)
                dist1 = np.linalg.norm(np.array(target_center) - np.array(get_box_center(detected_hands[0]['box'])))
                dist2 = np.linalg.norm(np.array(target_center) - np.array(get_box_center(detected_hands[1]['box'])))
                active_hand_box = detected_hands[0]['box'] if dist1 < dist2 else detected_hands[1]['box']
            # If no hands, active_hand_box remains None

        # Now, use the active_hand_box for logic
        if stage == 'FINDING_OBJECT' and target_box is not None:
            if active_hand_box and calculate_iou(active_hand_box, target_box) > IOU_THRESHOLD:
                update_instruction(f"It looks like you're already holding the {found_target}. Task complete!")
                st.session_state.guidance_stage = 'DONE'
            else:
                location_desc = describe_location(target_box, frame.shape[1])
                update_instruction(f"Great, I see the {found_target} {location_desc}. Please move your hand towards it.")
                st.session_state.guidance_stage = 'GUIDING_HAND'

        elif stage == 'GUIDING_HAND':
            if active_hand_box is not None:
                if calculate_iou(active_hand_box, target_box) > IOU_THRESHOLD:
                    st.session_state.guidance_stage = 'DONE'
                elif time.time() - st.session_state.last_guidance_time > GUIDANCE_UPDATE_INTERVAL_SEC:
                    prompt = f"""A user is trying to grab a '{st.session_state.target_objects[0]}'. The object is {describe_location(target_box, frame.shape[1])}. Their hand is {describe_location(active_hand_box, frame.shape[1])}. Give a short, one-sentence instruction to guide their hand to the object."""
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
            
    return draw_guidance_on_frame(annotated_frame, st.session_state.current_instruction, custom_font)

def update_instruction(new_instruction):
    st.session_state.current_instruction = new_instruction
    if not st.session_state.instruction_history or st.session_state.instruction_history[-1] != new_instruction:
        st.session_state.instruction_history.append(new_instruction)

def calculate_iou(boxA, boxB):
    if boxA is None or boxB is None: return 0
    xA, yA = max(boxA[0], boxB[0]), max(boxA[1], boxB[1])
    xB, yB = min(boxA[2], boxB[2]), min(boxA[3], boxB[3])
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
# (This section is unchanged)
def describe_frame_with_blip(frame, processor, model, device):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb_frame)
    inputs = processor(images=image, return_tensors="pt").to(device)
    generated_ids = model.generate(**inputs, max_length=50)
    return processor.decode(generated_ids[0], skip_special_tokens=True).strip()

def summarize_descriptions(descriptions):
    prompt_content = ". ".join(descriptions)
    system_prompt = "You are a motion analysis expert. I will provide a sequence of static observations. Infer the single most likely action that connects them. Deduce the verb or action. Your response MUST be ONLY the summary sentence, with no preamble. Example: ['a person is standing', 'a person is lifting their foot'] -> 'A person is starting to walk.'"
    return get_groq_response(f"{system_prompt}\n\nObservations: {prompt_content}\n\nSummary:")

def check_for_safety_alert(summary):
    prompt = f"Analyze for potential harm, distress, or accidents. Respond with only 'HARMFUL' if it contains events like falling, crashing, fire, or injury. Otherwise, respond only 'SAFE'.\n\nEvent: '{summary}'"
    return "HARMFUL" in get_groq_response(prompt, model="llama-3.1-8b-instant").strip().upper()

def run_scene_description(frame, vision_processor, vision_model, device):
    if time.time() - st.session_state.recording_start_time > RECORDING_SPAN_MINUTES * 60:
        st.session_state.is_recording = False
        save_log_to_json(st.session_state.current_session_log, st.session_state.log_filename)
        st.toast(f"Recording session ended. Log saved to {st.session_state.log_filename}")
        st.session_state.current_session_log, st.session_state.log_filename, st.session_state.frame_description_buffer = {}, "", []
        return frame
    if time.time() - st.session_state.last_frame_analysis_time > FRAME_ANALYSIS_INTERVAL_SEC:
        st.session_state.last_frame_analysis_time = time.time()
        st.session_state.frame_description_buffer.append(describe_frame_with_blip(frame, vision_processor, vision_model, device))
        if len(st.session_state.frame_description_buffer) >= SUMMARIZATION_BUFFER_SIZE:
            descriptions = list(set(st.session_state.frame_description_buffer))
            summary = summarize_descriptions(descriptions)
            is_harmful = check_for_safety_alert(summary)
            log_entry = {"timestamp": datetime.now().isoformat(), "summary": summary, "raw_descriptions": descriptions, "flag": "SAFETY_ALERT" if is_harmful else "None"}
            st.session_state.current_session_log["events"].append(log_entry)
            st.session_state.frame_description_buffer = []
            if is_harmful: st.toast("⚠️ Safety Alert Triggered!", icon="🚨")
    font = load_font(FONT_PATH, 20)
    status_text = f"🔴 RECORDING... | Session ends in {RECORDING_SPAN_MINUTES - (time.time() - st.session_state.recording_start_time)/60:.1f} mins"
    return draw_guidance_on_frame(frame, status_text, font)

# --- 6. Main Application UI and Execution Loop ---
# (This section is unchanged)
st.set_page_config(page_title="AIris Unified Platform", layout="wide")
st.title("👁️ AIris: Unified Assistance Platform")

for key, default_value in [('run_camera', False), ('mode', "Activity Guide"), ('guidance_stage', "IDLE"),
                           ('current_instruction', "Start the camera and enter a task."), ('instruction_history', []),
                           ('target_objects', []), ('found_object_location', None), ('last_guidance_time', 0),
                           ('is_recording', False), ('recording_start_time', 0), ('last_frame_analysis_time', 0),
                           ('current_session_log', {}), ('log_filename', ""), ('frame_description_buffer', []),
                           ('source_path', 0)]:
    if key not in st.session_state: st.session_state[key] = default_value

with st.sidebar:
    st.header("Mode Selection")
    st.radio("Select Mode", ["Activity Guide", "Scene Description"], key="mode")
    st.divider()
    st.header("Camera Controls")
    source_selection = st.radio("Select Camera Source", ["Webcam", "DroidCam URL"], key="source_selector")
    if source_selection == "Webcam":
        st.session_state.source_path = 0
        st.info("Using device webcam (index 0).")
    else:
        droidcam_url = st.text_input("DroidCam IP URL", "http://192.168.1.5:4747/video")
        st.session_state.source_path = droidcam_url
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Camera"): st.session_state.run_camera = True
    with col2:
        if st.button("Stop Camera"):
            st.session_state.run_camera = False
            if st.session_state.get('is_recording', False):
                st.session_state.current_session_log["events"].append({"timestamp": datetime.now().isoformat(), "event": "recording_paused", "reason": "Camera turned off by user."})
                st.toast("Recording paused.")

video_placeholder = st.empty()
if st.session_state.mode == "Activity Guide":
    st.header("Activity Guide")
    col1, col2 = st.columns([2, 3])
    def start_task():
        if not st.session_state.run_camera: st.toast("Please start the camera first!", icon="📷"); return
        goal = st.session_state.user_goal_input
        if not goal: st.toast("Please enter a task description.", icon="✍️"); return
        st.session_state.instruction_history, st.session_state.task_done_displayed = [], False
        update_instruction(f"Okay, processing your request to: '{goal}'...")
        prompt = f"""A user wants to perform: '{goal}'. What single, primary object do they need first? Respond with a Python list of names for it. Examples: 'drink water' -> ['bottle', 'cup', 'mug']. 'read a book' -> ['book']."""
        response = get_groq_response(prompt)
        try:
            target_list = ast.literal_eval(response)
            if isinstance(target_list, list) and target_list:
                st.session_state.target_objects, st.session_state.guidance_stage = target_list, "FINDING_OBJECT"
                update_instruction(f"Okay, let's find the {target_list[0]}.")
            else: update_instruction("Sorry, I couldn't determine the object for that task.")
        except (ValueError, SyntaxError): update_instruction(f"Sorry, I had trouble understanding the task. Response: {response}")
    with col1:
        st.text_input("Enter the task you want to perform:", key="user_goal_input", on_change=start_task)
        st.button("Start Task", on_click=start_task)
    with col2:
        st.subheader("Guidance Log")
        log_container = st.container(height=200)
        for i, instruction in enumerate(st.session_state.instruction_history):
            log_container.markdown(f"**{i+1}.** {instruction}")
elif st.session_state.mode == "Scene Description":
    st.header("Scene Description Logger")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶️ Start Recording", disabled=st.session_state.is_recording):
            if not st.session_state.run_camera: st.toast("Please start the camera first!", icon="📷")
            else:
                st.session_state.is_recording, st.session_state.recording_start_time, st.session_state.last_frame_analysis_time = True, time.time(), time.time()
                st.session_state.log_filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                st.session_state.current_session_log = {"session_start": datetime.now().isoformat(), "duration_minutes": RECORDING_SPAN_MINUTES, "events": []}
                if st.session_state.get('log_filename', ''): st.session_state.current_session_log["events"].append({"timestamp": datetime.now().isoformat(), "event": "recording_resumed"})
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
                st.session_state.current_session_log["events"].append({"timestamp": datetime.now().isoformat(), "event": "description_triggered"})
                last_summary = next((event["summary"] for event in reversed(st.session_state.current_session_log["events"]) if "summary" in event), "No summary yet.")
                text_to_speech(last_summary)
                st.session_state.current_session_log["events"].append({"timestamp": datetime.now().isoformat(), "event": "description_ended"})
            else: st.toast("No descriptions recorded yet.")
    st.subheader("Live Recording Log")
    log_display = st.container(height=300)
    if st.session_state.get('is_recording', False): log_display.json(st.session_state.current_session_log)

if st.session_state.run_camera:
    video_placeholder.empty()
    FRAME_WINDOW = st.image([])
    yolo_model, hand_model = load_yolo_model(YOLO_MODEL_PATH), load_hand_model()
    vision_processor, vision_model, device = load_vision_model()
    vid_cap = cv2.VideoCapture(st.session_state.source_path)
    if not vid_cap.isOpened():
        st.error(f"Error opening camera source '{st.session_state.source_path}'. Check camera permissions or URL.")
        st.session_state.run_camera = False
    while vid_cap.isOpened() and st.session_state.run_camera:
        success, frame = vid_cap.read()
        if not success: st.warning("Stream ended."); break
        if st.session_state.mode == "Activity Guide":
            processed_frame = run_activity_guide(frame, yolo_model, hand_model)
        elif st.session_state.mode == "Scene Description" and st.session_state.is_recording:
            processed_frame = run_scene_description(frame, vision_processor, vision_model, device)
        else:
            processed_frame = frame
        FRAME_WINDOW.image(cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR))
    vid_cap.release()
else:
    video_placeholder.info("Camera is off. Use the sidebar to start the camera feed.")