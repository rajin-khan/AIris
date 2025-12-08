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
| **Scene Description** | 🔄 Testing | Continuous environment analysis with safety alerts |

## Architecture

```
AIris-System/
├── backend/
│   ├── api/                  # FastAPI routes
│   │   └── routes.py         # REST and WebSocket endpoints
│   ├── services/             # Core AI services
│   │   ├── activity_guide_service.py   # Object guidance logic
│   │   ├── scene_description_service.py # Scene analysis
│   │   ├── camera_service.py           # Camera handling
│   │   ├── model_service.py            # YOLO, MediaPipe, BLIP
│   │   ├── tts_service.py              # Text-to-speech
│   │   └── stt_service.py              # Speech-to-text (Whisper)
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
- **Camera** — Laptop webcam for testing (ESP32-CAM for production)

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

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Hardware Integration (In Progress)

The software currently uses laptop webcam/mic for testing. Production hardware:

| Component | Connection | Status |
|:----------|:-----------|:------:|
| ESP32-CAM | WiFi → Server | 🔄 In Progress |
| Arduino (Mic/Speaker) | Bluetooth → Server | 🔄 In Progress |

The frontend serves as a proof-of-concept GUI. The final device will be fully usable by blind users through physical buttons and audio feedback.

## Environment Variables

### Backend (.env)
```bash
GROQ_API_KEY=your_groq_api_key    # Required
YOLO_MODEL_PATH=yolo26s.pt        # Optional, auto-downloads
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000  # Optional, default shown
```

## Tech Stack

| Component | Technology |
|:----------|:-----------|
| Backend | FastAPI, Python 3.10+ |
| Object Detection | YOLO26 (Ultralytics) |
| Hand Tracking | MediaPipe |
| Image Captioning | BLIP |
| LLM Reasoning | Groq API (Llama 3) |
| Speech-to-Text | Whisper |
| Text-to-Speech | pyttsx3 |
| Frontend | React, TypeScript, Vite |
| Styling | Tailwind CSS v4 |

## License

MIT
