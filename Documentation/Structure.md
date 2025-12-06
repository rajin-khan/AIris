# AIris Project Structure

<div align="center">

![Project](https://img.shields.io/badge/Project-AIris-blue?style=for-the-badge&logo=eye)
![Phase](https://img.shields.io/badge/Phase-CSE%20499A/B-orange?style=for-the-badge&logo=folder)

**Complete repository organization and file structure**

</div>

---

## Repository Overview

```
AIRIS/
│
├── 📁 AIris-System/          # ⭐ MAIN APPLICATION
├── 📁 Hardware/              # ESP32 & Arduino code
├── 📁 Documentation/         # Project docs
├── 📁 Archive/               # Archived experiments
│
├── 📄 README.md              # Project overview
├── 📄 To-Do.md               # Current tasks
└── 📄 Log.md                 # Development log
```

---

## AIris-System/ *(Main Application)*

The current, working version of the AIris software.

```
AIris-System/
├── 📁 backend/
│   ├── 📁 api/
│   │   ├── __init__.py
│   │   └── routes.py              # REST & WebSocket endpoints
│   │
│   ├── 📁 services/
│   │   ├── __init__.py
│   │   ├── activity_guide_service.py   # Object guidance logic
│   │   ├── scene_description_service.py # Environment analysis
│   │   ├── camera_service.py           # Video feed handling
│   │   ├── model_service.py            # YOLO, MediaPipe, BLIP
│   │   ├── tts_service.py              # Text-to-speech
│   │   └── stt_service.py              # Speech-to-text
│   │
│   ├── 📁 models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   │
│   ├── 📁 utils/
│   │   ├── __init__.py
│   │   └── frame_utils.py         # Image processing helpers
│   │
│   ├── 📄 main.py                 # FastAPI entry point
│   ├── 📄 requirements.txt        # Python dependencies
│   └── 📄 yolov8s.pt              # YOLO model weights
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 components/         # React components
│   │   ├── 📁 services/           # API client
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── main.tsx
│   │   └── index.css
│   │
│   ├── 📄 package.json
│   ├── 📄 vite.config.ts
│   ├── 📄 tsconfig.json
│   └── 📄 RESTART.md              # Troubleshooting
│
├── 📄 README.md                   # Setup instructions
└── 📄 QUICKSTART.md               # Quick start guide
```

---

## Hardware/ *(Device Firmware)*

ESP32-CAM and Arduino code for the physical device.

```
Hardware/
└── 📁 esp32-cam-test/
    ├── 📄 cam_app.py              # Python test client
    └── 📁 esp32-cam-test/
        └── esp32-cam-test.ino     # ESP32 Arduino sketch
```

---

## Documentation/ *(Project Docs)*

All project documentation and planning materials.

```
Documentation/
├── 📄 PRD.md                      # Product Requirements Document
├── 📄 Idea.md                     # Project vision and concept
├── 📄 Plan.md                     # Development roadmap
├── 📄 Structure.md                # This file
├── 📄 UseCases.md                 # Core assistive scenarios
├── 📄 Vision.md                   # Visual identity guide
├── 📄 EvaluationReport.md         # Performance benchmarks
├── 📄 GroundTruth.md              # Test evaluation data
│
├── 📁 Images/
│   ├── AIrisBan.png               # Full banner
│   ├── AIrisBantiny.png           # Small banner
│   └── ...                        # Other assets
│
├── 📁 Info/
│   ├── TechKnowledge.md           # Technology stack details
│   └── Budget.md                  # Hardware costs
│
├── 📁 LitReview/
│   ├── LitReview0.md
│   ├── LitReview1.md
│   └── *.pdf                      # Research papers
│
├── 📁 Class/
│   └── class1.md                  # Course materials
│
└── 📁 499APaper/
    ├── main.tex                   # LaTeX paper
    └── *.png                      # Paper figures
```

---

## Archive/ *(Archived Experiments)*

Development history — experiments and prototypes that led to the current implementation.

```
Archive/
├── 📁 0-Inference-Experimental/   # Early BLIP experiments
├── 📁 1-Inference-LLM/            # LLM integration tests
├── 📁 2-Benchmarking/             # Ollama performance tests
├── 📁 3-Performance-Comparision/  # Model comparison
├── 📁 AIris-Core-System/          # Previous core implementation
├── 📁 AIris-Final-App-Old/        # Previous app version
├── 📁 AIris-Prototype/            # Early React prototype
├── 📁 Merged_System/              # Integration experiments
├── 📁 RSPB/                       # Real-time system prototype
├── 📁 RSPB-2/                     # Improved RSPB
├── 📁 Activity_Execution/         # Activity detection tests
├── 📁 Mockup/                     # UI mockups
└── 📁 Website/                    # Project website
```

> **Note**: These folders are preserved for reference and academic documentation. Active development happens in `AIris-System/`.

---

## Key Files

| File | Location | Purpose |
|:-----|:---------|:--------|
| `main.py` | AIris-System/backend/ | Backend entry point |
| `routes.py` | AIris-System/backend/api/ | API endpoints |
| `App.tsx` | AIris-System/frontend/src/ | Frontend entry |
| `README.md` | Root | Project overview |
| `QUICKSTART.md` | AIris-System/ | Setup guide |

---

## Development Checklist

### Completed ✅
- [x] Backend architecture (FastAPI)
- [x] Object detection (YOLOv8)
- [x] Hand tracking (MediaPipe)
- [x] LLM integration (Groq)
- [x] Speech I/O (Whisper, pyttsx3)
- [x] Frontend GUI (React)
- [x] Active Guidance mode
- [x] Scene Description mode (core)

### In Progress 🔄
- [ ] ESP32-CAM WiFi streaming
- [ ] Arduino Bluetooth audio
- [ ] Guardian alert system

### Pending ⏳
- [ ] Physical button controls
- [ ] Wearable enclosure
- [ ] User field testing

---

<div align="center">

*This structure reflects the current state of the AIris project*

</div>
