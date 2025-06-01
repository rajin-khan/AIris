# AIris Product Requirements Document (PRD)

## Document Information
- **Product Name**: AIris - Real-Time Scene Description System
- **Version**: 1.0
- **Date**: June 2025
- **Project Phase**: CSE 499A/B Academic Project

---

## Product Overview

### Vision Statement
AIris is a wearable, AI-powered visual assistance system that provides instant, contextual scene descriptions for visually impaired users through real-time computer vision and natural language processing.

### Problem Statement
Current visual assistance solutions suffer from:
- High latency (>5 seconds response time)
- Cloud dependency and cost barriers
- Poor accessibility (smartphone-dependent)
- Lack of contextual understanding
- Limited real-time capabilities

### Solution
A purpose-built, wearable device combining:
- **Edge AI processing** on Raspberry Pi 5
- **Sub-2-second response time**
- **Single-button operation**
- **Local-first processing** with cloud fallback
- **Contextual scene understanding**

---

## System Architecture

### Hardware Components
| Component | Specification | Purpose | Constraints |
|-----------|---------------|---------|-------------|
| **Main Computer** | Raspberry Pi 5 (8GB RAM) | AI processing, system control | 8GB RAM limit, ARM architecture |
| **Camera** | USB/CSI camera module | Image capture | Must support 1080p, low-light capable |
| **Input Button** | Tactile switch with long wire | User trigger | Debounced, ergonomic placement |
| **Audio Output** | Mini speaker integrated into spectacle frame | Private audio delivery | Clear speech quality, directional audio |
| **Power Supply** | 10,000mAh+ battery pack | Portable power | 8+ hour runtime |
| **Housing** | Custom 3D-printed case | Protection, portability | Weather-resistant, lightweight |

### Software Architecture
```
┌─────────────────────────────────────────┐
│             AIris Core System           │
├─────────────────────────────────────────┤
│  AI Engine                              │
│  ├── Model Manager (local/cloud)        │
│  ├── Scene Analyzer                     │
│  ├── Groq API Client (fallback)        │
│  └── Ollama Integration                 │
├─────────────────────────────────────────┤
│  Camera Interface                       │
│  ├── Camera Manager                     │
│  ├── Image Processor                    │
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
- **Description**: System must capture high-quality images on button press
- **Requirements**:
  - Image capture within 100ms of button press
  - Support 1080p resolution minimum
  - Automatic exposure adjustment
  - Handle various lighting conditions
- **Acceptance Criteria**:
  - ✅ Button press triggers immediate image capture
  - ✅ Images are sharp and properly exposed in 90% of conditions
  - ✅ No visible delay between press and capture

#### FR-2: AI-Powered Scene Analysis
- **Description**: Generate intelligent, contextual descriptions of captured scenes
- **Requirements**:
  - Identify objects, people, activities, and spatial relationships
  - Provide confidence levels for identifications
  - Generate natural language descriptions
  - Prioritize safety-relevant information
- **Acceptance Criteria**:
  - ✅ Achieve >85% accuracy in object identification
  - ✅ Descriptions are contextually relevant and helpful
  - ✅ Safety hazards are prioritized in descriptions

#### FR-3: Sub-2-Second Response Time
- **Description**: Total time from button press to audio output start
- **Requirements**:
  - Local processing preferred (<1.5s typical)
  - Cloud fallback acceptable (<2s maximum)
  - Graceful degradation under load
- **Acceptance Criteria**:
  - ✅ 90% of requests complete within 1.5 seconds locally
  - ✅ 99% of requests complete within 2 seconds total
  - ✅ System provides feedback during processing

#### FR-4: Audio Description Output
- **Description**: Convert scene analysis to clear, spoken descriptions through integrated mini speaker
- **Requirements**:
  - Natural-sounding text-to-speech
  - Adjustable speech rate and volume
  - Directional audio focused toward user's ear
  - Private listening (minimal sound leakage)
  - Queue management for multiple requests
- **Acceptance Criteria**:
  - ✅ Speech is clear and understandable at close range
  - ✅ Audio is directional and private to the user
  - ✅ Multiple descriptions queue properly without overlap
  - ✅ Volume adjustable for different environments

#### FR-5: Offline-First Operation
- **Description**: System functions primarily without internet connectivity
- **Requirements**:
  - Local AI models for scene analysis
  - Local TTS engine
  - All core functions available offline
  - Cloud enhancement when available
- **Acceptance Criteria**:
  - ✅ All basic functions work without internet
  - ✅ Performance degradation is minimal offline
  - ✅ Cloud features enhance but don't replace local capability

### Advanced Features

#### FR-6: Contextual Intelligence
- **Description**: Provide context-aware descriptions based on environment
- **Requirements**:
  - Spatial relationship understanding (left/right, near/far)
  - Activity recognition (walking, driving, cooking)
  - Environment classification (indoor/outdoor, room type)
  - Temporal awareness (changes from previous descriptions)

#### FR-7: Safety Prioritization
- **Description**: Highlight potential hazards and navigation obstacles
- **Requirements**:
  - Obstacle detection and alerting
  - Traffic and vehicle awareness
  - Step, curb, and elevation changes
  - Moving object tracking

#### FR-8: Adaptive Processing
- **Description**: Optimize performance based on system load and context
- **Requirements**:
  - Dynamic model selection (local vs. cloud)
  - Quality vs. speed trade-offs
  - Battery life optimization
  - Temperature-based throttling

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
  - OpenCV 4.8+
  - Transformers 4.30+
  - RPi.GPIO
  - picamera2
  - pyttsx3
  - pygame

AI Models:
  - LLaVA-v1.5 (primary vision-language model)
  - BLIP-2 (fallback model)
  - Quantized variants for performance

System Services:
  - systemd service for auto-start
  - Bluetooth service management
  - Audio service configuration
```

### TR-3: Performance Benchmarks
| Metric | Target | Minimum Acceptable |
|--------|--------|--------------------|
| **Response Latency** | <1.5s | <2.0s |
| **Object Recognition Accuracy** | >90% | >85% |
| **Battery Life** | >10 hours | >8 hours |
| **Memory Usage** | <6GB | <7GB |
| **CPU Usage** | <80% sustained | <95% peak |
| **Storage Requirements** | <32GB | <64GB |

**Integration Requirements**:
- **Groq API Integration**: Fallback for complex scenes
- **Ollama Integration**: Local LLM hosting capability
- **Mini Speaker Audio**: Direct audio output via GPIO/I2S
- **File System**: Organized structure matching documentation
- **Logging**: Comprehensive system and performance logging

---

## User Experience Requirements

### UX-1: Single-Button Interaction
- **Primary Interaction**: Single tactile button
- **Feedback**: Immediate tactile/audio confirmation
- **Error Handling**: Clear audio error messages
- **Recovery**: Simple reset procedures

### UX-2: Audio Interface Design
- **Speech Quality**: Natural, clear pronunciation through integrated speaker
- **Information Hierarchy**: Critical information first
- **Brevity**: Concise but complete descriptions
- **Privacy**: Directional audio to prevent eavesdropping
- **Volume Control**: Adjustable for different environments
- **Personalization**: Adjustable detail levels

### UX-3: Wearability Requirements
- **Weight**: <500g total system weight
- **Form Factor**: Spectacle-mounted camera + pocket device
- **Durability**: Withstand daily wear and weather
- **Comfort**: Extended wear without discomfort

### UX-4: Setup and Maintenance
- **Initial Setup**: <30 minutes for technical users
- **Daily Use**: No setup required after initial configuration
- **Maintenance**: Weekly charging, monthly updates
- **Troubleshooting**: Audio-guided diagnostic procedures

---

## Non-Functional Requirements

### Performance Requirements
- **Reliability**: 99.5% uptime during normal operation
- **Scalability**: Support for future feature additions
- **Maintainability**: Modular architecture for easy updates
- **Testability**: Comprehensive unit and integration tests

### Security Requirements
- **Data Privacy**: All processing local by default
- **Image Storage**: Temporary storage only, automatic deletion
- **API Security**: Encrypted cloud communications when used
- **Access Control**: No unauthorized system access

### Compatibility Requirements
- **Operating System**: Raspberry Pi OS (Debian-based)
- **Audio Devices**: Integrated mini speaker via I2S/GPIO
- **Power Sources**: USB-C PD, standard power banks
- **Mounting**: Universal spectacle frame compatibility with speaker integration

---

## Success Metrics

### Primary KPIs
1. **Response Time**: 95% of requests <2 seconds
2. **Accuracy**: >85% object identification accuracy
3. **Battery Life**: >8 hours continuous use
4. **User Satisfaction**: Based on usability testing feedback

### Secondary Metrics
1. **System Reliability**: <0.1% crash rate
2. **Feature Adoption**: Usage patterns of different capabilities
3. **Performance Optimization**: Memory and CPU utilization trends
4. **Audio Quality**: Speech clarity and comprehension rates

---

## Development Phases

### Phase 1: CSE 499A (Software Foundation)
**Duration**: 16 weeks  
**Focus**: Core software development and AI integration

#### Milestones:
1. **Week 1-4**: Environment setup and basic camera integration
2. **Week 5-8**: AI model research, selection, and integration
3. **Week 9-12**: Scene description engine development
4. **Week 13-16**: Audio system and performance optimization

#### Deliverables:
- ✅ Functional prototype running on Raspberry Pi 5
- ✅ Working camera integration with button trigger
- ✅ AI model comparison and selection documentation
- ✅ Audio description system with TTS
- ✅ Performance benchmarks and optimization results

### Phase 2: CSE 499B (Hardware Integration)
**Duration**: 16 weeks  
**Focus**: Hardware design, integration, and user experience

#### Milestones:
1. **Week 1-4**: Hardware design and 3D modeling
2. **Week 5-8**: Hardware assembly and testing
3. **Week 9-12**: System integration and field testing
4. **Week 13-16**: Final optimization and documentation

#### Deliverables:
- ✅ Complete wearable hardware system
- ✅ 3D-printed components and assembly instructions
- ✅ User manual and setup documentation
- ✅ Field testing results and user feedback
- ✅ Production-ready prototype

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
Software/airis-core/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── requirements.txt       # Dependencies
└── src/
    ├── ai_engine/         # AI and ML components
    ├── camera/           # Camera and hardware interface
    ├── audio/            # Audio processing, TTS, and speaker control
    ├── core/             # Application logic
    └── utils/            # Utilities and helpers
```

### Quality Standards
- **Code Coverage**: >80% test coverage
- **Documentation**: Comprehensive docstrings and README files
- **Code Style**: PEP 8 compliance with Black formatting
- **Version Control**: Git with semantic versioning
- **Error Handling**: Graceful failure and recovery mechanisms

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: System-wide functionality testing
- **Performance Tests**: Latency and resource usage benchmarks
- **User Acceptance Tests**: Real-world usage scenarios
- **Hardware Tests**: Physical device stress testing

---

## 📋 Acceptance Criteria

### Minimum Viable Product (MVP)
For successful project completion, AIris must demonstrate:

1. **Hardware Integration**
   - Camera captures images on button press
   - Audio output functions correctly
   - System runs on portable power for 8+ hours

2. **Software Functionality**
   - AI models process images and generate descriptions
   - Response time consistently under 2 seconds
   - Text-to-speech provides clear audio output through integrated speaker

3. **User Experience**
   - Single-button operation works reliably
   - Descriptions are accurate and helpful
   - System is comfortable to wear and use

4. **Technical Performance**
   - Meets all performance benchmarks
   - Demonstrates offline-first capability
   - Shows graceful cloud fallback functionality

### Success Criteria
- **Functionality**: All core features working as specified
- **Performance**: Meets or exceeds all benchmark targets
- **Usability**: Positive feedback from user testing
- **Documentation**: Complete technical and user documentation
- **Reproducibility**: Other developers can build and deploy the system

---

## Future Considerations

### Potential Enhancements
- **Facial Recognition**: Identify known individuals
- **Document Reading**: OCR for text recognition
- **Multi-language Support**: International accessibility
- **Voice Commands**: Hands-free operation modes

### Scalability Considerations
- **Cloud Integration**: Enhanced processing capabilities
- **Mobile App**: Companion smartphone application
- **Community Features**: Shared location descriptions
- **Hardware Evolution**: Integration with AR glasses

### Research Opportunities
- **Edge AI Optimization**: Novel compression techniques
- **Contextual Learning**: Personalized description preferences
- **Multi-modal Integration**: Sound and vibration feedback
- **Accessibility Standards**: Contributing to accessibility research

---

## Support and Maintenance

### Development Support
- **Repository**: AIris GitHub repository with issue tracking
- **Documentation**: Comprehensive setup and troubleshooting guides
- **Community**: Open-source community for contributions and support

### Maintenance Plan
- **Regular Updates**: Monthly software updates
- **Model Updates**: Quarterly AI model improvements
- **Hardware Revisions**: Annual hardware design improvements
- **Security Updates**: Immediate security patch deployment

---

*This PRD serves as the definitive guide for AIris development. All implementation decisions should align with these requirements while maintaining flexibility for innovation and improvement.*