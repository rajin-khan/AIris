import cv2
import streamlit as st
from ultralytics import YOLO
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
MODEL_PATH = 'yolov8n.pt'  # Nano model for performance
FONT_PATH = 'RobotoCondensed-Regular.ttf' # Make sure this font file is in the same directory
CONFIDENCE_THRESHOLD = 0.4
IOU_THRESHOLD = 0.1 # Intersection over Union threshold for hand-object interaction
# ---------------------

# --- Model Loading ---

@st.cache_resource
def load_yolo_model(model_path):
    """ Loads the YOLOv8 model using st.cache_resource for efficiency. """
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        st.error(f"Error loading YOLO model: {e}")
        return None

@st.cache_resource
def load_hand_model():
    """ Loads the MediaPipe Hands model using st.cache_resource. """
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2)
    return hands

@st.cache_resource
def load_font(font_path, size=30):
    """ Loads the custom font using st.cache_resource. """
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        st.error(f"Font file not found at {font_path}. Using default font.")
        return ImageFont.load_default() # Fallback to default font

# --- Helper & Logic Functions ---

def calculate_iou(boxA, boxB):
    """ Calculates Intersection over Union (IoU) between two bounding boxes. """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    
    denominator = float(boxAArea + boxBArea - interArea)
    if denominator == 0:
        return 0.0
    
    iou = interArea / denominator
    return iou

def detect_activity(detected_objects_with_boxes, hand_boxes, iou_thresh):
    """
    Enhanced rule-based logic to determine activity based on hand-object interactions.
    """
    interacting_objects = set()
    detected_object_names = set(item[0] for item in detected_objects_with_boxes)
    activity = "No specific activity detected"

    if hand_boxes:
        for hand_box in hand_boxes:
            for obj_name, obj_box in detected_objects_with_boxes:
                if calculate_iou(hand_box, obj_box) > iou_thresh:
                    interacting_objects.add(obj_name)

    if 'cell phone' in interacting_objects:
        activity = "Using Phone"
    elif 'cup' in interacting_objects or 'bottle' in interacting_objects:
        activity = "Drinking"
    elif 'book' in interacting_objects:
        activity = "Reading"
    elif 'toothbrush' in interacting_objects:
        activity = "Brushing Teeth"
    elif 'laptop' in interacting_objects or 'keyboard' in interacting_objects or 'mouse' in interacting_objects:
        activity = "Interacting with Computer"
    elif 'scissors' in interacting_objects:
        activity = "Using Scissors / Crafting"

    elif activity == "No specific activity detected":
        if 'laptop' in detected_object_names or 'keyboard' in detected_object_names:
            activity = "Working / On Computer"
        elif 'tv' in detected_object_names:
            activity = "Watching TV"
            
    return activity

def draw_activity_on_frame_pil(frame_bgr, activity, font):
    """ Draws text on the frame using Pillow for custom font support. """
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(frame_rgb)
    draw = ImageDraw.Draw(pil_img)
    
    text = f"Activity: {activity}"
    
    try:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)

    x, y = 10, 10
    draw.rectangle([x, y, x + text_width + 10, y + text_height + 10], fill="black")
    draw.text((x + 5, y + 5), text, font=font, fill="white")
    
    # --- THIS IS THE FIX ---
    # Convert back to OpenCV BGR format from Pillow's RGB format
    # The correct constant is cv2.COLOR_RGB2BGR
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

# --- Main Application Logic ---

def run_detection_loop(source_path, conf_slider, iou_slider):
    """
    The main loop for capturing video, running detection, and displaying results.
    """
    yolo_model = load_yolo_model(MODEL_PATH)
    hand_model = load_hand_model()
    custom_font = load_font(FONT_PATH)
    mp_drawing = mp.solutions.drawing_utils

    if not yolo_model or not hand_model:
        st.error("Models failed to load. Cannot start detection.")
        return

    vid_cap = cv2.VideoCapture(source_path)
    if not vid_cap.isOpened():
        st.error(f"Error: Could not open camera source '{source_path}'.")
        return

    FRAME_WINDOW = st.empty()

    while vid_cap.isOpened() and st.session_state.run:
        success, frame = vid_cap.read()
        if not success:
            st.warning("Stream ended or camera disconnected.")
            break

        yolo_results = yolo_model.track(frame, persist=True, conf=conf_slider, verbose=False)
        annotated_frame = yolo_results[0].plot(line_width=2)

        detected_objects_with_boxes = []
        if yolo_results[0].boxes.id is not None:
            boxes = yolo_results[0].boxes.xyxy.cpu().numpy().astype(int)
            class_ids = yolo_results[0].boxes.cls.cpu().numpy().astype(int)
            for i in range(len(boxes)):
                class_name = yolo_model.names[class_ids[i]]
                box = boxes[i]
                detected_objects_with_boxes.append((class_name, box))

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_results = hand_model.process(rgb_frame)
        
        hand_boxes = []
        if mp_results.multi_hand_landmarks:
            for hand_landmarks in mp_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(annotated_frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                
                h, w, _ = frame.shape
                x_coords = [lm.x for lm in hand_landmarks.landmark]
                y_coords = [lm.y for lm in hand_landmarks.landmark]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                hand_box = [int(x_min * w), int(y_min * h), int(x_max * w), int(y_max * h)]
                hand_boxes.append(hand_box)
                cv2.rectangle(annotated_frame, (hand_box[0], hand_box[1]), (hand_box[2], hand_box[3]), (0, 255, 0), 2)

        current_activity = detect_activity(detected_objects_with_boxes, hand_boxes, iou_slider)
        final_frame = draw_activity_on_frame_pil(annotated_frame, current_activity, custom_font)
        FRAME_WINDOW.image(cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB))
    
    vid_cap.release()
    st.info("Detection stopped and camera released.")


# --- Streamlit UI Setup ---

st.set_page_config(page_title="First-Person Activity Detection", layout="wide")
st.title("First-Person Activity Detection with Hand Interaction")
st.markdown("This app uses YOLOv8 and MediaPipe to infer activities from a live feed.")

if 'run' not in st.session_state:
    st.session_state.run = False

with st.sidebar:
    st.header("Configuration")
    source_selection = st.radio("Select Camera Source", ["Webcam", "DroidCam URL"])
    
    source_path = 0
    if source_selection == "DroidCam URL":
        source_path = st.text_input("Enter DroidCam IP URL", "http://192.168.1.5:4747/video")

    confidence_slider = st.slider("Detection Confidence", 0.0, 1.0, CONFIDENCE_THRESHOLD, 0.05)
    iou_slider = st.slider("Hand-Object Interaction IoU", 0.0, 1.0, IOU_THRESHOLD, 0.05)

    if st.button("Start Detection"):
        st.session_state.run = True

    if st.button("Stop Detection"):
        st.session_state.run = False

if st.session_state.run:
    run_detection_loop(source_path, confidence_slider, iou_slider)
else:
    st.info("Click 'Start Detection' to begin.")