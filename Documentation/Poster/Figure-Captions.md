# Figure Captions for AIris Poster

## Figure 1: System Architecture Diagram

**Figure 1.** Complete system architecture of AIris showing three-tiered design: Frontend (Web Speech API for voice I/O), FastAPI Backend (vision models, Activity Guide pipeline, Scene Description pipeline, and output services), and Groq API cloud inference (GPT OSS120B for object extraction and summarization). The diagram illustrates data flow between components, with Activity Guide (green) and Scene Description (red) pipelines clearly separated.

---

## Figure 2: Active Guidance Mode Flowchart

**Figure 2.** Active Guidance mode decision loop flowchart. The system processes voice commands through GPT OSS120B for object extraction, performs YOLO26s object detection and MediaPipe hand tracking, calculates spatial vectors and depth estimates, and generates real-time directional guidance using a novel rule-based algorithm (no LLM). The loop continues until hand-object contact is confirmed, providing step-by-step audio instructions to guide users to target objects.

---

## Figure 3: Scene Description Mode Flowchart

**Figure 3.** Scene Description mode continuous monitoring flowchart. The system captures and captions frames at 2 FPS using BLIP, performs multi-method risk assessment (keywords, static frame detection, transition analysis), accumulates frames in a buffer (5-10 frames), and processes them through GPT OSS120B for summarization and risk scoring. The system branches into normal operation (TTS output) or alert path (fall detection → guardian email) based on risk threshold, then loops back for continuous monitoring.

---

## Figure 4: Fall Detection Algorithm Flow

**Figure 4.** Multi-method fall detection algorithm flowchart. Three parallel analysis paths (static frame detection, transition pattern analysis, and risk score calculation) process BLIP-generated captions. All paths converge to GPT OSS120B for summary generation and risk scoring. When risk exceeds threshold, the system triggers fall alerts, sends automated guardian email notifications, and implements cooldown protection to prevent spam.

---

## Figure 5: AIris System Strengths Radar Chart

**Figure 5.** Octagonal radar chart displaying AIris system strengths across eight key dimensions: Real-Time Performance (95%, <2s latency), Accuracy (90%, >85% success), Privacy (100%, local-first), Accessibility (100%, handsfree), Safety (95%, fall detection), Innovation (100%, novel algorithm), Cost-Effectiveness (90%, Web Speech API), and Reliability (95%, 7x faster). The chart demonstrates comprehensive system capabilities with near-maximum performance across critical accessibility metrics.

---

## Figure 6: Hardware Components and Software Interface

**Figure 6.** (A) Custom-designed ESP32-CAM hardware components: 3D-printed protective casing with "AIRIS" branding, ESP32-CAM-MB module, and mounting clip. (B) Real-time software interface showing object detection (cell phone at 56% confidence, person at 93% confidence), MediaPipe hand tracking with 21-landmark skeletal overlay, and interactive guidance system providing step-by-step instructions for object interaction. The interface demonstrates handsfree operation with voice input and audio feedback capabilities.

---

## Figure 7: Latency Comparison Bar Chart

**Figure 7.** Performance comparison between prototype and final system. The prototype (BLIP+GPT) achieved 14.1s average latency, while the final system (YOLO26s+GPT OSS120B) achieves 1.8s latency—representing a 7x speed improvement. The dashed line indicates the real-time threshold (2s), demonstrating that the final system operates within acceptable real-time constraints for assistive technology applications.

---

## Notes for Poster Layout

- **Figure numbering:** Use sequential numbering (Figure 1, Figure 2, etc.) as they appear on the poster
- **Caption style:** Georgia font, 10-12pt, left-aligned below each figure
- **Format:** "**Figure X.** [Description]" followed by detailed explanation
- **Placement:** Captions should be positioned directly below their corresponding figures
- **Consistency:** All captions follow the same format and style guidelines








