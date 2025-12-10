# AIris System

The main application for AIris — an AI-powered vision assistant for the visually impaired.

## Overview

This folder contains the **current, working version** of the AIris software. It includes:

- **FastAPI Backend** — AI services, WebSocket streaming, REST API
- **React Frontend** — Development/testing interface (proof of concept)

### Features

| Mode | Status | Description |
|:-----|:------:|:------------|
| **Active Guidance** | ✅ Working | Guides user to find and reach objects via audio instructions |
| **Scene Description** | ✅ Working | Continuous environment analysis with safety alerts and fall detection |
| **Handsfree Mode** | ✅ Working | Full voice control — no screen interaction required |
| **Guardian Alerts** | ✅ Working | Email notifications for safety events and daily/weekly summaries |

## Architecture

```
AIris-System/
├── backend/
│   ├── api/                  # FastAPI routes
│   │   └── routes.py         # REST and WebSocket endpoints
│   ├── services/             # Core AI services
│   │   ├── activity_guide_service.py   # Object guidance logic
│   │   ├── scene_description_service.py # Scene analysis with fall detection
│   │   ├── camera_service.py           # Camera handling (webcam/ESP32)
│   │   ├── model_service.py            # YOLO26, MediaPipe, BLIP
│   │   ├── tts_service.py              # Text-to-speech
│   │   ├── stt_service.py              # Speech-to-text (Whisper)
│   │   └── email_service.py             # Guardian alerts and summaries
│   ├── models/               # Pydantic schemas
│   ├── utils/                # Helper utilities
│   ├── main.py               # FastAPI entry point
│   └── requirements.txt      # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/       # React components
    │   ├── services/         # API client
    │   └── App.tsx           # Main application
    ├── package.json
    └── vite.config.ts
```

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Groq API Key** — Get free at [console.groq.com](https://console.groq.com)
- **Computer with webcam and microphone** — Built-in hardware works perfectly
- **Optional:** ESP32-CAM and Bluetooth mic/headphone for wireless operation

## Quick Setup

See [QUICKSTART.md](./QUICKSTART.md) for step-by-step instructions.

### Backend

```bash
cd backend

# Create environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# Run server
python main.py
```

Backend runs at `http://localhost:8000`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at `http://localhost:5173`

## Usage

1. Start the backend server
2. Start the frontend dev server
3. Open `http://localhost:5173` in your browser
4. Click "Start Camera" to enable video feed
5. Choose a mode:
   - **Activity Guide**: Enter an object to find (e.g., "water bottle")
   - **Scene Description**: Click "Start Recording" for continuous analysis

### Handsfree Mode

Enable **Voice-Only Mode** for hands-free operation:
- Click the microphone icon in the header to enable
- Use voice commands to control the system:
  - "Switch to activity guide" / "Switch to scene description"
  - "Turn on camera" / "Turn off camera"
  - "Input task" (to enter a task via voice)
  - "Start task" (to begin the task)
  - "Yes" / "No" (for feedback prompts)
- All instructions and descriptions are automatically spoken
- Perfect for blind users — no screen interaction needed

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Hardware Accessories

The software runs entirely on your computer. We've designed a **custom ESP32-CAM with protective casing** for enhanced handsfree operation:

| Component | Connection | Status | Purpose |
|:----------|:-----------|:------:|:--------|
| **Custom ESP32-CAM** ⭐ | WiFi → Computer | ✅ Recommended | Custom camera with 3D-printed casing |
| **Bluetooth Mic** | Bluetooth → Computer | 🔄 Optional | Wireless microphone input |
| **Bluetooth Headphone** | Bluetooth → Computer | 🔄 Optional | Wireless audio output |

**Recommended Setup:** Our **custom ESP32-CAM with AIris-designed casing** (see `Hardware/cam-casing/`) provides the best handsfree experience with wireless camera positioning.

**Default Setup:** The system works perfectly with your computer's built-in webcam and speakers/microphone. No external hardware is required — we've made this the default option for maximum accessibility and ease of use.

**Handsfree Mode:** Enable Voice-Only Mode in the interface to control everything via voice commands — no screen interaction needed. Perfect for blind users.

## Environment Variables

### Backend (.env)
```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional - Model Configuration
YOLO_MODEL_PATH=yolo26s.pt        # Default: yolo26s.pt (auto-downloads if missing)

# Optional - Email/Guardian Features
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=guardian@example.com
EMAIL_DAILY_HOUR=3                # Daily summary at 3 AM (default)
EMAIL_WEEKLY_DAY=friday           # Weekly report day (default)
EMAIL_WEEKLY_HOUR=0                # Weekly report hour (default: midnight)
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000  # Optional, default shown
```

## Tech Stack

| Component | Technology |
|:----------|:-----------|
| Backend | FastAPI, Python 3.10+ |
| Object Detection | YOLO26s (Ultralytics) |
| Hand Tracking | MediaPipe |
| Image Captioning | BLIP |
| LLM Reasoning | Groq API (GPT OSS 120B) |
| Speech-to-Text | Whisper (offline) |
| Text-to-Speech | pyttsx3 (native) |
| Email Notifications | aiosmtplib (Gmail SMTP) |
| Frontend | React, TypeScript, Vite |
| Styling | Tailwind CSS v4 |

## Key Features

### 🎯 Active Guidance Mode
- **Object Detection**: YOLO26s for real-time object detection
- **Hand Tracking**: MediaPipe for precise hand position tracking
- **Audio Guidance**: Step-by-step instructions to reach objects
- **Voice Control**: Full handsfree operation with voice commands

### 🔍 Scene Description Mode
- **Continuous Analysis**: Real-time environment understanding
- **Fall Detection**: Advanced algorithm detects falls and collisions
- **Safety Alerts**: Automatic guardian email notifications
- **Risk Scoring**: Configurable sensitivity for alert thresholds

### 📧 Guardian Features
- **Email Alerts**: Immediate notifications for safety events
- **Daily Summaries**: Scheduled activity summaries
- **Weekly Reports**: Comprehensive weekly activity reports
- **Risk Threshold**: Adjustable sensitivity (0.1 - 0.5)
- **Cooldown Protection**: Prevents email spam with smart cooldowns

## License

MIT
