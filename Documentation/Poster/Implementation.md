# Architecture & Implementation

### Technical Stack
*   **Core Backend:** FastAPI (Python 3.10+) - Async high-concurrency server with WebSocket support.
*   **Frontend:** React + TypeScript with Web Speech API for native browser STT/TTS.
*   **Vision Engine:** YOLO26s (Ultralytics) for object detection + MediaPipe for hand tracking (21 landmarks).
*   **Scene Analysis:** BLIP (Transformers) for image captioning and semantic understanding.
*   **Reasoning Core:** GPT OSS120B via Groq API (ultra-fast inference, <500ms response) for object extraction (Activity Guide) and summarization (Scene Description). Guidance generation uses a novel rule-based algorithm (no LLM) for real-time performance.
*   **Audio Pipeline:** Web Speech API (native browser STT/TTS) for handsfree operation - no server-side audio processing required.
*   **Safety System:** Proprietary multi-method fall detection algorithm (static frame detection, transition analysis, risk scoring) + Email service (aiosmtplib) for guardian alerts.
*   **Hardware (Optional):** Custom ESP32-CAM with 3D-printed casing for wireless video, Bluetooth headset for audio I/O.

### Data Flow Implementation

**Activity Guide Mode:**
1.  **Voice Input:** Web Speech API STT captures user command (e.g., "Find my phone").
2.  **Object Extraction:** GPT OSS120B (Groq) extracts target object from natural language goal.
3.  **Frame Capture:** Video frame from source (built-in webcam or optional ESP32-CAM via WiFi).
4.  **Parallel Inference:** Frame processed asynchronously by YOLO26s (object detection) and MediaPipe (hand tracking with 21 landmarks).
5.  **Vector Calculation:** Geometric algorithm calculates 3D spatial vector: $V = P_{object\_center} - P_{hand\_centroid}$.
6.  **Depth Estimation:** Bounding box size ratio analysis estimates relative depth between hand and object.
7.  **Rule-Based Guidance:** Novel algorithm (no LLM) converts vector and depth to natural language directional commands in real-time.
8.  **Audio Output:** Web Speech API TTS speaks instruction to user.
9.  **Distance Check:** Proximity and depth analysis confirms hand-object contact.

**Scene Description Mode:**
1.  **Frame Capture:** Video frames sampled at 2 FPS from source.
2.  **Scene Captioning:** BLIP generates semantic captions for each frame.
3.  **Quick Risk Assessment:** Keyword-based analysis for fast frame-level risk detection.
4.  **Static Frame Detection:** Pattern matching detects wall/floor/ceiling views (fall indicators).
5.  **Transition Detection:** Frame comparison detects abrupt changes between frames.
6.  **Buffer Accumulation:** Frame descriptions accumulated in buffer (5-10 frames).
7.  **LLM Summarization:** GPT OSS120B (Groq) analyzes buffer and generates contextual summary.
8.  **Risk Scoring:** Multi-factor analysis calculates risk score (0.0-1.0) based on keywords, static frames, and transitions.
9.  **Fall Detection:** Multi-method analysis triggers alert if risk score exceeds threshold.
10. **Email Alert:** Guardian system sends automated email notification with cooldown protection.
11. **Audio Output:** Web Speech API TTS speaks scene description to user.
