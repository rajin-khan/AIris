# AIris Product Requirements Document (PRD)

## Document Information
- **Product Name**: AIris — AI-Powered Vision Assistant
- **Version**: 2.0
- **Date**: December 2025
- **Project Phase**: CSE 499A/B Academic Project

---

## Product Overview

### Vision Statement
AIris is a wearable AI-powered vision assistant that helps visually impaired users navigate their environment and locate objects through real-time audio feedback.

### Problem Statement
Current visual assistance solutions suffer from:
- High latency (>5 seconds response time)
- Cloud dependency and privacy concerns
- Smartphone-dependent interfaces not accessible to blind users
- Lack of active guidance for object localization
- Limited real-time capabilities

### Solution
A computer-based software system providing:
- **Active Guidance** — Audio instructions to find and reach specific objects
- **Scene Description** — Continuous environment awareness with safety alerts
- **Hands-Free Operation** — Voice commands via Handsfree Mode, no screen interaction required
- **Optional Accessories** — ESP32 camera (WiFi) + Bluetooth mic/headphone for wireless operation
- **Privacy-First** — All AI processing on user's local computer

---

## System Architecture

### Hardware Components

| Component | Specification | Purpose |
|:----------|:--------------|:--------|
| **Camera** | Built-in webcam (default) or ESP32-CAM (optional) | Video capture |
| **Audio Input** | Built-in mic (default) or Bluetooth Microphone (optional) | Voice commands from user |
| **Audio Output** | Built-in speakers (default) or Bluetooth Headphone (optional) | Audio feedback delivery |
| **Processing** | Computer/Server | AI inference, backend services |
| **Controls** | Voice Commands (Handsfree Mode) | Mode selection, activation |

### Software Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AIris Software Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Backend Services (FastAPI)                            │ │
│  │  ├── Camera Service      — Video feed handling         │ │
│  │  ├── Model Service       — YOLO26s, MediaPipe, BLIP   │ │
│  │  ├── Activity Guide      — Object localization logic   │ │
│  │  ├── Scene Description   — Environment analysis + fall detection │ │
│  │  ├── STT Service         — Whisper speech recognition  │ │
│  │  ├── TTS Service         — Audio response generation   │ │
│  │  └── Email Service       — Guardian alerts & summaries │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  AI Models                                              │ │
│  │  ├── YOLO26s            — Real-time object detection  │ │
│  │  ├── MediaPipe           — Hand tracking               │ │
│  │  ├── BLIP                — Image captioning            │ │
│  │  ├── Groq API            — LLM reasoning (Llama 3)     │ │
│  │  └── Whisper             — Speech-to-text              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Frontend (React) — Development GUI                    │ │
│  │  Note: Proof of concept only. Final device uses        │ │
│  │  handsfree voice commands, no screen required.         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Functional Requirements

### FR-1: Active Guidance Mode

**Description**: Guide user to locate and reach a specified object.

**Requirements**:
- User speaks object name (e.g., "find my water bottle")
- System detects object using YOLO
- System tracks user's hand using MediaPipe
- LLM generates directional instructions ("move left", "reach forward")
- Audio feedback continues until hand reaches object

**Acceptance Criteria**:
- ✅ Object detection accuracy >85%
- ✅ Hand tracking works reliably
- ✅ Audio instructions are clear and actionable
- ✅ System confirms when object is reached

### FR-2: Scene Description Mode

**Description**: Provide continuous environment awareness.

**Requirements**:
- Analyze video feed using BLIP vision model
- Generate contextual descriptions via LLM
- Prioritize safety-relevant information
- Advanced fall detection algorithm
- Automatic guardian email notifications

**Acceptance Criteria**:
- ✅ Descriptions are contextually relevant
- ✅ Safety hazards are identified and prioritized
- ✅ Fall detection with email alerts (working)
- ✅ Guardian email system (complete)

### FR-3: Voice Interaction

**Description**: Hands-free voice command and response.

**Requirements**:
- Speech-to-text using Whisper (offline)
- Text-to-speech for audio responses (native)
- Full handsfree/voice-only mode
- Support via Bluetooth microphone/headphone

**Acceptance Criteria**:
- ✅ Voice commands recognized accurately
- ✅ Audio responses are clear
- ✅ Handsfree mode fully functional
- 🔄 Bluetooth audio integration (in progress)

### FR-4: Wireless Operation

**Description**: Cable-free wearable design.

**Requirements**:
- System runs on computer with built-in webcam/mic (default)
- Optional: ESP32-CAM for wireless video streaming
- Optional: Bluetooth microphone/headphone for wireless audio
- Voice commands via Handsfree Mode for all controls

**Acceptance Criteria**:
- ✅ Core system functional with built-in hardware
- ✅ Handsfree mode provides full voice control
- 🔄 Optional ESP32-CAM WiFi streaming (in progress)
- 🔄 Optional Bluetooth mic/headphone pairing (in progress)

---

## Technical Requirements

### TR-1: Software Dependencies

```yaml
Backend:
  - Python 3.10+
  - FastAPI
  - PyTorch
  - Ultralytics (YOLOv8)
  - MediaPipe
  - Transformers (BLIP)
  - OpenAI Whisper
  - pyttsx3
  - Groq SDK

Frontend:
  - Node.js 18+
  - React
  - TypeScript
  - Vite
  - Tailwind CSS

Hardware Firmware:
  - Arduino IDE
  - ESP32 libraries
  - Bluetooth libraries
```

### TR-2: Performance Targets

| Metric | Target | Current Status |
|:-------|:-------|:---------------|
| **Guidance Response** | < 2s | ✅ Achieved |
| **Object Detection** | > 85% accuracy | ✅ Achieved |
| **Scene Description** | < 5s | 🔄 Testing |
| **Voice Recognition** | > 90% accuracy | ✅ Achieved |

---

## User Experience Requirements

### UX-1: Accessibility First
- No screen interaction required for core functions
- Voice commands via Handsfree Mode for all controls
- Clear, concise audio feedback
- Consistent audio cues for system states

### UX-2: Hands-Free Design
- Custom ESP32-CAM with casing (recommended) or built-in webcam (default)
- Wireless audio accessories (optional) or built-in speakers (default)
- Voice-only operation — no physical buttons needed

### UX-3: Safety Prioritization
- Hazard detection in Scene Description mode
- Guardian notification system for emergencies
- Clear "obstacle ahead" type warnings

---

## Development Status

### Completed ✅
- Core software architecture
- Active Guidance mode implementation
- Backend API and services
- Frontend development interface
- YOLO object detection integration
- MediaPipe hand tracking
- Groq LLM integration
- Whisper speech-to-text
- pyttsx3 text-to-speech

### In Progress 🔄
- Scene Description mode refinement
- Custom ESP32-CAM WiFi integration (optional)
- Bluetooth mic/headphone integration (optional)
- ✅ Guardian alert system (complete)

### Pending ⏳
- ✅ Voice control complete (no physical buttons needed)
- ✅ Custom camera casing designed (3D printable)
- User field testing
- Final documentation

---

## Success Criteria

### MVP Requirements
1. **Active Guidance**: User can find objects using voice commands
2. **Scene Description**: Continuous environment awareness
3. **Wireless Operation**: Custom ESP32-CAM (recommended) or built-in webcam (default) — both work perfectly
4. **Standalone Use**: No screen required for blind users

### Quality Metrics
- Guidance accuracy: >85% success rate
- Response latency: <2 seconds
- User satisfaction: Positive feedback from testing

---

## Future Considerations

### Potential Enhancements
- Facial recognition for people identification
- OCR for text reading
- Multi-language support
- Mobile companion app

### Scalability
- Cloud backup for complex scenes
- Remote guardian dashboard
- Community-shared location descriptions

---

*This PRD serves as the guide for AIris development. Implementation details are in the codebase at `/AIris-System/`.*
