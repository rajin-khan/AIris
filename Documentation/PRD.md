# AIris Product Requirements Document (PRD)

## Document Information
- **Product Name**: AIris - Real-Time Scene Description System
- **Version**: 1.2
- **Date**: July 2024
- **Project Phase**: CSE 499A/B Academic Project (Development Phase)

---

## Product Overview

### Vision Statement
AIris is a wearable, AI-powered visual assistance system that provides instant, contextual scene descriptions for visually impaired users through real-time computer vision and natural language processing.

### Problem Statement
Current visual assistance solutions suffer from:
- High latency (>5 seconds response time)
- Cloud dependency and cost barriers
- Poor accessibility (smartphone-dependent)
- Lack of contextual understanding and memory
- Limited real-time capabilities

### Solution
A purpose-built, wearable device combining:
- **Edge AI processing** on Raspberry Pi 5
- **Sub-2-second response time**
- **Single-button operation**
- **Local-first processing** with cloud fallback
- **Contextual scene understanding** with a novel memory-augmented architecture.

---

## System Architecture

### Hardware Components
| Component | Specification | Purpose | Constraints |
|:---|:---|:---|:---|
| **Main Computer** | Raspberry Pi 5 (8GB RAM) | AI processing, system control | 8GB RAM limit, ARM architecture |
| **Camera** | USB/CSI camera module | Image capture | Must support 1080p, low-light capable |
| **Input Button** | Tactile switch with long wire | User trigger | Debounced, ergonomic placement |
| **Audio Output** | Mini speaker integrated into spectacle frame | Private audio delivery | Clear speech quality, directional audio |
| **Power Supply** | 10,000mAh+ battery pack | Portable power | 8+ hour runtime |
| **Housing** | Custom 3D-printed case | Protection, portability | Weather-resistant, lightweight |

### Software Architecture
*This diagram represents the full software vision, incorporating the advanced CAS-D components into the modular system.*
```
┌─────────────────────────────────────────┐
│             AIris Core System           │
├─────────────────────────────────────────┤
│  AI Engine (AIrisModel)                 │
│  ├── Model Manager (local/cloud)        │
│  ├── Scene Analyzer (CAS-D Core)        │
│  │   ├── Position-Aware Encoder        │
│  │   ├── Memory Agent & Bank           │
│  │   └── LLM Decoder (Cross-Attention) │
│  ├── Groq API Client (fallback)         │
│  └── Ollama Integration (local LLM)     │
├─────────────────────────────────────────┤
│  Camera Interface                       │
│  ├── Camera Manager                     │
│  ├── Image Processor (RGB, Depth)       │
│  └── Button Handler                     │
├─────────────────────────────────────────┤
│  Audio System                           │
│  ├── TTS Engine                         │
│  ├── Audio Manager                      │
│  └── Mini Speaker Controller            │
├─────────────────────────────────────────┤
│  Core Services                          │
│  ├── Application Controller             │
│  ├── State Manager                      │
│  ├── Event Handler                      │
│  └── Logger                             │
└─────────────────────────────────────────┘
```

---

## Functional Requirements

### Core Features

#### FR-1: Real-Time Scene Capture
- **Description**: System must capture high-quality images on button press.
- **Requirements**:
  - Image capture within 100ms of button press.
  - Support 1080p resolution minimum.
  - Automatic exposure adjustment.
  - Handle various lighting conditions.
- **Acceptance Criteria**:
  - ✅ Button press triggers immediate image capture.
  - ✅ Images are sharp and properly exposed in 90% of conditions.
  - ✅ No visible delay between press and capture.

#### FR-2: AI-Powered Scene Analysis
- **Description**: Generate intelligent, contextual descriptions of captured scenes.
- **Requirements**:
  - Identify objects, people, activities, and spatial relationships.
  - Provide confidence levels for identifications.
  - Generate natural language descriptions.
  - Prioritize safety-relevant information.
- **Acceptance Criteria**:
  - ✅ Achieve >85% accuracy in object identification.
  - ✅ Descriptions are contextually relevant and helpful.
  - ✅ Safety hazards are prioritized in descriptions.

#### FR-3: Sub-2-Second Response Time
- **Description**: Total time from button press to audio output start.
- **Requirements**:
  - Local processing preferred (<1.5s typical).
  - Cloud fallback acceptable (<2s maximum).
  - Graceful degradation under load.
- **Acceptance Criteria**:
  - ✅ 90% of requests complete within 2 seconds total.
  - ✅ System provides feedback during processing if needed.

#### FR-4: Audio Description Output
- **Description**: Convert scene analysis to clear, spoken descriptions through integrated mini speaker.
- **Requirements**:
  - Natural-sounding text-to-speech.
  - Adjustable speech rate and volume.
  - Directional audio focused toward user's ear.
  - Private listening (minimal sound leakage).
  - Queue management for multiple requests.
- **Acceptance Criteria**:
  - ✅ Speech is clear and understandable at close range.
  - ✅ Audio is directional and private to the user.
  - ✅ Multiple descriptions queue properly without overlap.
  - ✅ Volume adjustable for different environments.

#### FR-5: Offline-First Operation
- **Description**: System functions primarily without internet connectivity.
- **Requirements**:
  - Local AI models for scene analysis.
  - Local TTS engine.
  - All core functions available offline.
  - Cloud enhancement when available.
- **Acceptance Criteria**:
  - ✅ All basic functions work without internet.
  - ✅ Performance degradation is minimal offline.
  - ✅ Cloud features enhance but don't replace local capability.

### Advanced Features

#### FR-6: Contextual Intelligence
- **Description**: Provide context-aware descriptions based on environment and memory over time.
- **Requirements**:
  - Spatial relationship understanding (left/right, near/far) **achieved via Position-Aware Encoding**.
  - Activity recognition (walking, driving, cooking).
  - Environment classification (indoor/outdoor, room type).
  - Temporal awareness (changes from previous descriptions) **achieved via the Memory Agent and cross-attention**.

#### FR-7: Safety Prioritization
- **Description**: Highlight potential hazards and navigation obstacles.
- **Requirements**:
  - Obstacle detection and alerting.
  - Traffic and vehicle awareness.
  - Step, curb, and elevation changes.
  - Moving object tracking.

#### FR-8: Adaptive Processing
- **Description**: Optimize performance based on system load and context.
- **Requirements**:
  - Dynamic model selection (local vs. cloud).
  - Quality vs. speed trade-offs.
  - Battery life optimization.
  - Temperature-based throttling.

---

## Technical Requirements

### TR-1: Hardware Specifications
```yaml
Minimum System Requirements:
  - Raspberry Pi 5 with 8GB RAM
  - 64GB microSD card (Class 10+)
  - USB 3.0 camera or CSI camera module
  - Mini speaker (3W-5W, 8Ω impedance)
  - Audio amplifier (PAM8403 or similar)
  - GPIO access for button input
  - 5V/3A power supply capability

Recommended Specifications:
  - High-quality USB camera with autofocus
  - External SSD for faster model loading
  - Heat sink and fan for thermal management
  - Directional mini speaker with good frequency response
  - Digital audio amplifier with volume control
```

### TR-2: Software Dependencies
```yaml
Core Dependencies:
  - Python 3.11+
  - PyTorch 2.0+
  - OpenCV 4.8+, Open3D
  - Transformers 4.30+, timm
  - RPi.GPIO, picamera2
  - pyttsx3, pygame
  - scikit-learn

AI Models (Initial Prototype):
  - Salesforce/blip-image-captioning-large

AI Models (Advanced CAS-D):
  - ViT-Base (from timm)
  - GPT-2 or Llama 3 (via Ollama/Groq)
  - Quantized variants for performance

System Services:
  - systemd service for auto-start
  - Bluetooth service management
  - Audio service configuration
```

### TR-3: Performance Benchmarks
| Metric | Target | Minimum Acceptable |
|:---|:---|:---|
| **Response Latency** | <1.5s | <2.0s |
| **Object Recognition Accuracy** | >90% | >85% |
| **Battery Life** | >10 hours | >8 hours |
| **Memory Usage** | <6GB | <7GB |
| **CPU Usage** | <80% sustained | <95% peak |
| **Storage Requirements** | <32GB | <64GB |

**Integration Requirements**:
- **Groq API Integration**: Fallback for complex scenes.
- **Ollama Integration**: Local LLM hosting capability.
- **Mini Speaker Audio**: Direct audio output via GPIO/I2S.
- **File System**: Organized structure matching documentation.
- **Logging**: Comprehensive system and performance logging.

---

## User Experience Requirements

### UX-1: Single-Button Interaction
- **Primary Interaction**: Single tactile button.
- **Feedback**: Immediate tactile/audio confirmation.
- **Error Handling**: Clear audio error messages.
- **Recovery**: Simple reset procedures.

### UX-2: Audio Interface Design
- **Speech Quality**: Natural, clear pronunciation through integrated speaker.
- **Information Hierarchy**: Critical information first.
- **Brevity**: Concise but complete descriptions.
- **Privacy**: Directional audio to prevent eavesdropping.
- **Volume Control**: Adjustable for different environments.
- **Personalization**: Adjustable detail levels.

### UX-3: Wearability Requirements
- **Weight**: <500g total system weight.
- **Form Factor**: Spectacle-mounted camera + pocket device.
- **Durability**: Withstand daily wear and weather.
- **Comfort**: Extended wear without discomfort.

### UX-4: Setup and Maintenance
- **Initial Setup**: <30 minutes for technical users.
- **Daily Use**: No setup required after initial configuration.
- **Maintenance**: Weekly charging, monthly updates.
- **Troubleshooting**: Audio-guided diagnostic procedures.

---

## Non-Functional Requirements

### Performance Requirements
- **Reliability**: 99.5% uptime during normal operation.
- **Scalability**: Support for future feature additions.
- **Maintainability**: Modular architecture for easy updates.
- **Testability**: Comprehensive unit and integration tests.

### Security Requirements
- **Data Privacy**: All processing local by default.
- **Image Storage**: Temporary storage only, automatic deletion.
- **API Security**: Encrypted cloud communications when used.
- **Access Control**: No unauthorized system access.

### Compatibility Requirements
- **Operating System**: Raspberry Pi OS (Debian-based).
- **Audio Devices**: Integrated mini speaker via I2S/GPIO.
- **Power Sources**: USB-C PD, standard power banks.
- **Mounting**: Universal spectacle frame compatibility with speaker integration.

---

## Success Metrics

### Primary KPIs
1. **Response Time**: 95% of requests <2 seconds.
2. **Accuracy**: >85% object identification accuracy (for v1 prototype); High score on contextual Q&A for CAS-D.
3. **Battery Life**: >8 hours continuous use.
4. **User Satisfaction**: Based on usability testing feedback.

### Secondary Metrics
1. **System Reliability**: <0.1% crash rate.
2. **Feature Adoption**: Usage patterns of different capabilities.
3. **Performance Optimization**: Memory and CPU utilization trends.
4. **Audio Quality**: Speech clarity and comprehension rates.

---

## Development Phases

*This section is updated to reflect the new, detailed 4-week development plan for building the advanced system.*

### Phase 1: CSE 499A (Software Foundation)
**Duration**: 4 Weeks (Sprint)  
**Focus**: Evolve the prototype into a functional Context-Aware Spatial Description (CAS-D) system.

*   **Week 1: Formalize Prototype & Foundations**
    *   **Goal:** Refactor the current `app.py` prototype into a professional project structure and establish the theoretical groundwork by analyzing key research papers (MC-ViT, Video-3D LLM).
    *   **Deliverable:** A polished, runnable v1 prototype and a research summary document.

*   **Week 2: Build the Core AIris Engine**
    *   **Goal:** Implement the main `AIrisModel` class, including the `PositionAwareEncoder`, the k-means-based `MemoryAgent`, and the LLM decoder wired for cross-attention.
    *   **Deliverable:** A functional `AIrisModel` that can be tested with dummy data.

*   **Week 3: Integrate the 3D Data Pipeline**
    *   **Goal:** Implement a PyTorch `Dataset` and `DataLoader` for the ScanNet dataset, capable of feeding real-world RGB, depth, and camera pose data into our model.
    *   **Deliverable:** A successful integration test showing that real data can flow through the `AIrisModel`.

*   **Week 4: End-to-End Proof-of-Concept**
    *   **Goal:** Implement a full training loop, run it on a small subset of the data, and demonstrate that the training loss decreases, proving the architecture is viable.
    *   **Deliverable:** A functional, end-to-end MVP codebase and a near-complete research proposal draft.

### Phase 2: CSE 499B (Hardware Integration & Refinement)
**Duration**: 16 weeks  
**Focus**: Hardware design, integration, and user experience.
*   **Milestones:** Hardware design and 3D modeling, full system assembly, field testing with users, final optimization and documentation.

---

## Technical Implementation Guidelines

### Development Environment
```bash
# Required System Setup
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git cmake

# Python Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Hardware Setup
sudo apt install python3-rpi.gpio python3-picamera2
sudo raspi-config  # Enable camera and GPIO
```

### Code Organization
```
Software/
├── prototype_v1/          # Formalized initial prototype
└── airis_casd_mvp/        # Advanced CAS-D system
    ├── data/
    ├── src/
    │   ├── dataset.py
    │   ├── model.py
    │   ├── agent.py
    │   └── train.py
    └── ...
```

### Quality Standards
- **Code Coverage**: >80% test coverage.
- **Documentation**: Comprehensive docstrings and README files.
- **Code Style**: PEP 8 compliance with Black formatting.
- **Version Control**: Git with semantic versioning.
- **Error Handling**: Graceful failure and recovery mechanisms.

### Testing Strategy
- **Unit Tests**: Individual component testing.
- **Integration Tests**: System-wide functionality testing.
- **Performance Tests**: Latency and resource usage benchmarks.
- **User Acceptance Tests**: Real-world usage scenarios.
- **Hardware Tests**: Physical device stress testing.

---

## 📋 Acceptance Criteria

### MVP for this Sprint (End of Week 4)
For successful project progress, the CAS-D MVP must demonstrate:

1.  **Hardware Integration**
    - Camera captures images on button press.
    - Audio output functions correctly.
    - System runs on portable power for 8+ hours.

2.  **Software Functionality**
    - AI models process images and generate descriptions.
    - Response time consistently under 2 seconds.
    - Text-to-speech provides clear audio output through integrated speaker.

3.  **User Experience**
    - Single-button operation works reliably.
    - Descriptions are accurate and helpful.
    - System is comfortable to wear and use.

4.  **Technical Performance**
    - Meets all performance benchmarks.
    - Demonstrates offline-first capability.
    - Shows graceful cloud fallback functionality.

### Success Criteria
- **Functionality**: All core features working as specified.
- **Performance**: Meets or exceeds all benchmark targets.
- **Usability**: Positive feedback from user testing.
- **Documentation**: Complete technical and user documentation.
- **Reproducibility**: Other developers can build and deploy the system.

---

## Future Considerations

### Potential Enhancements
- **Facial Recognition**: Identify known individuals.
- **Document Reading**: OCR for text recognition.
- **Multi-language Support**: International accessibility.
- **Voice Commands**: Hands-free operation modes.

### Scalability Considerations
- **Cloud Integration**: Enhanced processing capabilities.
- **Mobile App**: Companion smartphone application.
- **Community Features**: Shared location descriptions.
- **Hardware Evolution**: Integration with AR glasses.

### Research Opportunities
- **Edge AI Optimization**: Novel compression techniques.
- **Contextual Learning**: Personalized description preferences.
- **Multi-modal Integration**: Sound and vibration feedback.
- **Accessibility Standards**: Contributing to accessibility research.

---

## Support and Maintenance

### Development Support
- **Repository**: AIris GitHub repository with issue tracking.
- **Documentation**: Comprehensive setup and troubleshooting guides.
- **Community**: Open-source community for contributions and support.

### Maintenance Plan
- **Regular Updates**: Monthly software updates.
- **Model Updates**: Quarterly AI model improvements.
- **Hardware Revisions**: Annual hardware design improvements.
- **Security Updates**: Immediate security patch deployment.

---

*This PRD serves as the definitive guide for AIris development. All implementation decisions should align with these requirements while maintaining flexibility for innovation and improvement.*