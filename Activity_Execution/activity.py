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

# --- Configuration & Initialization ---
load_dotenv()

MODEL_PATH = 'yolov8n.pt'
FONT_PATH = 'RobotoCondensed-Regular.ttf'
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.1
GUIDANCE_UPDATE_INTERVAL = 2 # seconds

# --- Load API Key and Initialize Groq Client ---
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    st.error(f"Failed to initialize Groq client. Is your GROQ_API_KEY set in the .env file? Error: {e}")
    groq_client = None

# --- Model Loading (Cached) ---

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

# --- Helper & LLM Functions ---

def get_llm_response(prompt):
    if not groq_client: return "LLM Client not initialized."
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling Groq API: {e}"); return f"Error: {e}"

def describe_location(box, frame_width):
    center_x = (box[0] + box[2]) / 2
    if center_x < frame_width / 3: return "on your left"
    elif center_x > 2 * frame_width / 3: return "on your right"
    else: return "in front of you"

def calculate_iou(boxA, boxB):
    if boxA is None or boxB is None: return 0
    xA = max(boxA[0], boxB[0]); yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2]); yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    denominator = float(boxAArea + boxBArea - interArea)
    return interArea / denominator if denominator != 0 else 0

def draw_guidance_on_frame(frame, text, font):
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    draw.rectangle([10, 10, 710, 50], fill="black")
    draw.text((15, 15), text, font=font, fill="white")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def update_instruction(new_instruction):
    """Updates the current instruction and adds it to the history if it's new."""
    st.session_state.current_instruction = new_instruction
    if not st.session_state.instruction_history or st.session_state.instruction_history[-1] != new_instruction:
        st.session_state.instruction_history.append(new_instruction)

# --- Main Application Logic ---

def run_guidance_system(source_path):
    yolo_model = load_yolo_model(MODEL_PATH)
    hand_model = load_hand_model()
    custom_font = load_font(FONT_PATH)
    mp_drawing = mp.solutions.drawing_utils

    vid_cap = cv2.VideoCapture(source_path)
    if not vid_cap.isOpened():
        st.error(f"Error opening camera source '{source_path}'.")
        st.session_state.run_camera = False; return

    FRAME_WINDOW = st.empty()
    while vid_cap.isOpened() and st.session_state.run_camera:
        success, frame = vid_cap.read()
        if not success:
            st.warning("Stream ended."); break

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

        stage = st.session_state.guidance_stage
        
        if stage == 'IDLE':
            update_instruction("Camera is on. Enter a task below to begin.")
        elif stage == 'FINDING_OBJECT':
            target_options = st.session_state.target_objects
            detected_objects = {yolo_model.names[int(cls)]: box.cpu().numpy().astype(int) 
                                for box, cls in zip(yolo_results[0].boxes.xyxy, yolo_results[0].boxes.cls)}
            
            found_target = None
            for target in target_options:
                if target in detected_objects:
                    found_target = target
                    break
            
            if found_target:
                target_box = detected_objects[found_target]
                # --- SMART CHECK: Is the task already being performed? ---
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
                elif time.time() - st.session_state.last_guidance_time > GUIDANCE_UPDATE_INTERVAL:
                    prompt = f"""
                    A visually impaired user is trying to grab a '{st.session_state.target_objects[0]}'.
                    The object is located {describe_location(target_box, frame.shape[1])}.
                    Their hand is currently {describe_location(hand_box, frame.shape[1])}.
                    Give a very short, clear, one-sentence instruction to guide their hand to the object.
                    Example: 'Move your hand slightly to the right.'
                    """
                    llm_guidance = get_llm_response(prompt)
                    update_instruction(llm_guidance)
                    st.session_state.last_guidance_time = time.time()
            else:
                update_instruction("I can't see your hand. Please bring it into view.")

        elif stage == 'DONE':
            if not st.session_state.get('task_done_displayed', False):
                update_instruction("Task Completed Successfully!")
                st.balloons()
                st.session_state.task_done_displayed = True
        
        final_frame = draw_guidance_on_frame(annotated_frame, st.session_state.current_instruction, custom_font)
        FRAME_WINDOW.image(cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB))

    vid_cap.release()

# --- Streamlit UI Setup ---

st.set_page_config(page_title="LLM Activity Guide", layout="wide")
st.title("AI Guide for Activity Execution")

# --- Initialize Session State ---
if 'run_camera' not in st.session_state: st.session_state.run_camera = False
if 'guidance_stage' not in st.session_state: st.session_state.guidance_stage = "IDLE"
if 'current_instruction' not in st.session_state: st.session_state.current_instruction = "Start the camera and enter a task."
if 'instruction_history' not in st.session_state: st.session_state.instruction_history = []
if 'target_objects' not in st.session_state: st.session_state.target_objects = []
if 'found_object_location' not in st.session_state: st.session_state.found_object_location = None
if 'last_guidance_time' not in st.session_state: st.session_state.last_guidance_time = 0

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Controls")
    source_selection = st.radio("Select Camera Source", ["Webcam", "DroidCam URL"])
    source_path = 0 if source_selection == "Webcam" else st.text_input("DroidCam IP URL", "http://192.168.1.5:4747/video")

    if st.button("Start Camera"): st.session_state.run_camera = True
    if st.button("Stop Camera"): st.session_state.run_camera = False

# --- Main Content Area ---
video_placeholder = st.empty()
if not st.session_state.run_camera:
    video_placeholder.info("Camera is off. Use the sidebar to start the camera feed.")

col1, col2 = st.columns(2)

def start_task():
    if not st.session_state.run_camera:
        st.toast("Please start the camera first!", icon="📷"); return
    
    goal = st.session_state.user_goal_input
    if not goal:
        st.toast("Please enter a task description.", icon="✍️"); return
    
    # Reset states for the new task
    st.session_state.instruction_history = []
    st.session_state.task_done_displayed = False
    update_instruction(f"Okay, processing your request to: '{goal}'...")
    
    prompt = f"""
    A user wants to perform the task: '{goal}'. What single, primary physical object do they need to find first?
    Respond with a Python list of possible string names for that object. Keep it simple.
    Examples:
    - User wants to 'drink water': ['bottle', 'cup', 'mug']
    - User wants to 'read a book': ['book']
    - User wants to 'call someone': ['cell phone']
    """
    response = get_llm_response(prompt)
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

# --- Run the main loop if the camera state is active ---
if st.session_state.run_camera:
    video_placeholder.empty() 
    run_guidance_system(source_path)