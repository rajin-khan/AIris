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
A purpose-built wearable device providing:
- **Active Guidance** — Audio instructions to find and reach specific objects
- **Scene Description** — Continuous environment awareness with safety alerts
- **Wireless Design** — ESP32 camera (WiFi) + Arduino audio (Bluetooth)
- **Privacy-First** — All AI processing on user's local server
- **Hands-Free** — Physical buttons, no screen interaction required

---

## System Architecture

### Hardware Components

| Component | Specification | Purpose |
|:----------|:--------------|:--------|
| **Camera** | ESP32-CAM | Video capture, WiFi streaming to server |
| **Audio Input** | Microphone via Arduino | Voice commands from user |
| **Audio Output** | Speaker via Arduino | Audio feedback delivery |
| **Wireless** | WiFi (camera), Bluetooth (audio) | Cable-free operation |
| **Processing** | Server/Computer | AI inference, backend services |
| **Controls** | Physical buttons | Mode selection, activation |

### Software Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AIris Software Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Backend Services (FastAPI)                            │ │
│  │  ├── Camera Service      — Video feed handling         │ │
│  │  ├── Model Service       — YOLO, MediaPipe, BLIP       │ │
│  │  ├── Activity Guide      — Object localization logic   │ │
│  │  ├── Scene Description   — Environment analysis        │ │
│  │  ├── STT Service         — Whisper speech recognition  │ │
│  │  └── TTS Service         — Audio response generation   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  AI Models                                              │ │
│  │  ├── YOLOv8              — Real-time object detection  │ │
│  │  ├── MediaPipe           — Hand tracking               │ │
│  │  ├── BLIP                — Image captioning            │ │
│  │  ├── Groq API            — LLM reasoning (Llama 3)     │ │
│  │  └── Whisper             — Speech-to-text              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Frontend (React) — Development GUI                    │ │
│  │  Note: Proof of concept only. Final device uses        │ │
│  │  physical buttons + audio, no screen required.         │ │
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
- Support guardian alert notifications

**Acceptance Criteria**:
- ✅ Descriptions are contextually relevant
- ✅ Safety hazards are identified and prioritized
- 🔄 Guardian alerts functional (in testing)

### FR-3: Voice Interaction

**Description**: Hands-free voice command and response.

**Requirements**:
- Speech-to-text using Whisper
- Text-to-speech for audio responses
- Support via Arduino Bluetooth audio

**Acceptance Criteria**:
- ✅ Voice commands recognized accurately
- ✅ Audio responses are clear
- 🔄 Bluetooth audio integration (in progress)

### FR-4: Wireless Operation

**Description**: Cable-free wearable design.

**Requirements**:
- ESP32-CAM streams video over WiFi
- Arduino handles audio over Bluetooth
- Physical buttons for basic controls

**Acceptance Criteria**:
- 🔄 WiFi streaming functional (in progress)
- 🔄 Bluetooth audio functional (in progress)
- ⏳ Button controls (pending)

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
- Physical buttons for mode selection
- Clear, concise audio feedback
- Consistent audio cues for system states

### UX-2: Hands-Free Design
- Wearable camera (spectacle-mounted or clip-on)
- Wireless audio (earpiece or speaker)
- No cables during operation

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
- ESP32-CAM WiFi integration
- Arduino Bluetooth audio
- Guardian alert system

### Pending ⏳
- Physical button controls
- Wearable enclosure design
- User field testing
- Final documentation

---

## Success Criteria

### MVP Requirements
1. **Active Guidance**: User can find objects using voice commands
2. **Scene Description**: Continuous environment awareness
3. **Wireless Operation**: ESP32 camera + Arduino audio working
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
