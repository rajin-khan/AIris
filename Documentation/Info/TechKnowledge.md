<div align="center">

# AIris Technology Stack Guide

**Technical foundation for AIris development**

---

## Overview

AIris combines **Computer Vision**, **Natural Language Processing**, **Wireless Communication**, and **Embedded Systems** to create an AI-powered vision assistant. This document covers the key technologies used.

---

</div>

## Software Stack

### Backend (Python)

```yaml
Framework:
  - FastAPI           # Async web framework
  - Uvicorn           # ASGI server
  - WebSocket         # Real-time streaming

AI/ML:
  - PyTorch           # Deep learning framework
  - Ultralytics       # YOLOv8 object detection
  - MediaPipe         # Hand tracking
  - Transformers      # BLIP image captioning
  - OpenAI Whisper    # Speech-to-text

APIs:
  - Groq SDK          # LLM inference (Llama 3)
  - pyttsx3           # Text-to-speech

Utilities:
  - OpenCV            # Image processing
  - Pillow            # Image handling
  - NumPy             # Numerical operations
```

### Frontend (TypeScript)

```yaml
Framework:
  - React 18          # UI library
  - TypeScript        # Type safety
  - Vite              # Build tool

Styling:
  - Tailwind CSS v4   # Utility-first CSS

Libraries:
  - Axios             # HTTP client
  - Lucide React      # Icons
```

---

## Hardware Components

### ESP32-CAM

```yaml
Specifications:
  - Chip: ESP32-S with WiFi/Bluetooth
  - Camera: OV2640 (2MP)
  - Flash: 4MB
  - RAM: 520KB SRAM + 4MB PSRAM

Capabilities:
  - WiFi 802.11 b/g/n
  - MJPEG streaming
  - Programmable via Arduino IDE

Use in AIris:
  - Captures video feed
  - Streams over WiFi to server
  - Compact, wearable form factor
```

### Arduino (Audio Module)

```yaml
Components:
  - Arduino board (Nano/Uno)
  - Bluetooth module (HC-05/HC-06)
  - Microphone module
  - Speaker/amplifier

Capabilities:
  - Bluetooth audio streaming
  - Serial communication
  - Low power consumption

Use in AIris:
  - Receives audio from server
  - Captures voice commands
  - Plays TTS responses
```

---

## AI Models

### YOLOv8 (Object Detection)

```yaml
Model: YOLOv8s (small variant)
Size: ~25MB
Speed: Real-time (<50ms)
Accuracy: mAP 44.9%

Purpose:
  - Detect objects in camera feed
  - Return bounding boxes and labels
  - Enable object guidance feature
```

### MediaPipe (Hand Tracking)

```yaml
Model: Hand Landmarks
Points: 21 landmarks per hand
Speed: Real-time

Purpose:
  - Track user's hand position
  - Enable guidance to objects
  - Determine when hand reaches target
```

### BLIP (Image Captioning)

```yaml
Model: Salesforce/blip-image-captioning-large
Size: ~1.5GB
Purpose:
  - Generate scene descriptions
  - Provide context for LLM reasoning
```

### Groq API (LLM)

```yaml
Model: Llama 3 (70B via API)
Speed: Ultra-fast inference
Purpose:
  - Generate guidance instructions
  - Synthesize scene descriptions
  - Natural language responses
```

### Whisper (Speech-to-Text)

```yaml
Model: OpenAI Whisper (base)
Size: ~75MB
Accuracy: High quality transcription
Purpose:
  - Convert voice commands to text
  - Enable hands-free operation
```

---

## Communication Protocols

### WiFi (ESP32 to Server)

```yaml
Protocol: HTTP/WebSocket
Format: MJPEG frames
Latency: ~100-200ms
Range: Typical WiFi range
```

### Bluetooth (Arduino to Server)

```yaml
Protocol: Serial over Bluetooth
Baud Rate: 9600-115200
Range: ~10 meters
Use: Audio data transfer
```

---

## Development Environment

### Requirements

```bash
# Python
Python 3.10+
pip or conda

# Node.js
Node.js 18+
npm

# Hardware Development
Arduino IDE
ESP32 board support
```

### Setup

```bash
# Backend
cd AIris-System/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd AIris-System/frontend
npm install
npm run dev

# ESP32
# Install Arduino IDE
# Add ESP32 board manager URL
# Install ESP32 board support
```

---

## Performance Considerations

### Latency Optimization

| Component | Target | Strategy |
|:----------|:-------|:---------|
| Object detection | <100ms | Use YOLOv8s (small model) |
| Hand tracking | <50ms | MediaPipe optimized |
| LLM response | <500ms | Groq API (fast inference) |
| Total round-trip | <2s | Parallel processing |

### Memory Management

```yaml
Backend:
  - Models loaded once at startup
  - Lazy loading for optional models
  - Frame buffer management

Frontend:
  - Efficient canvas rendering
  - WebSocket streaming (no buffering)
```

---

## Security Considerations

```yaml
Privacy:
  - All processing on local server
  - No cloud upload of images
  - Groq API sees only text (not images)

Network:
  - Local WiFi only (ESP32)
  - Bluetooth pairing required (Arduino)
  - No external API calls except Groq
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|:------|:---------|
| ESP32 not connecting | Check WiFi credentials, restart |
| Bluetooth pairing fails | Re-pair, check baud rate |
| Models slow to load | First run downloads models |
| MediaPipe not initializing | Upgrade mediapipe package |
| YOLO not detecting | Check model path in .env |

---

<div align="center">

*For setup instructions, see [QUICKSTART.md](../../AIris-System/QUICKSTART.md)*

</div>
