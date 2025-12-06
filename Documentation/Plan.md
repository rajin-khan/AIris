# AIris Development Plan

## Project Timeline

**Course**: CSE 499A/B  
**Duration**: Two semesters  
**Expected Completion**: December 2025

---

## Current Status

| Component | Status | Progress |
|:----------|:------:|:--------:|
| Core Software | ✅ Complete | 100% |
| Active Guidance Mode | ✅ Complete | 100% |
| Scene Description Mode | 🔄 Testing | 90% |
| Hardware Integration | 🔄 In Progress | 40% |
| Final Assembly | ⏳ Pending | 0% |

**Overall Progress: ~70%**

---

## Phase 1: Software Development *(Completed)*

### Objectives
Build and validate the core AI pipeline using laptop camera for testing.

### Deliverables ✅
- FastAPI backend with all services
- React frontend for development/testing
- Active Guidance mode (YOLO + MediaPipe + LLM)
- Scene Description mode (BLIP + LLM)
- Voice I/O (Whisper + pyttsx3)
- API documentation

### Key Achievements
- Object detection working with >85% accuracy
- Hand tracking successfully guides users to objects
- LLM generates clear, actionable audio instructions
- Response latency <2 seconds

---

## Phase 2: Hardware Integration *(Current)*

### Objectives
Replace laptop camera/audio with wireless hardware components.

### Tasks

#### ESP32-CAM Integration
- [x] Acquire ESP32-CAM module
- [x] Basic camera test firmware
- [ ] WiFi streaming to server
- [ ] Video feed integration with backend
- [ ] Latency optimization

#### Arduino Audio
- [x] Acquire Arduino + Bluetooth module
- [ ] Bluetooth communication setup
- [ ] Microphone input handling
- [ ] Speaker output handling
- [ ] Integration with backend STT/TTS

#### Physical Controls
- [ ] Button wiring and debouncing
- [ ] Mode selection implementation
- [ ] Activation/deactivation controls

### Timeline
**Target**: End of current semester

---

## Phase 3: Assembly & Testing *(Upcoming)*

### Objectives
Build the physical wearable device and conduct user testing.

### Tasks

#### Enclosure Design
- [ ] Design wearable camera mount
- [ ] Design audio unit housing
- [ ] 3D print prototypes
- [ ] Iterate based on comfort testing

#### System Integration
- [ ] Connect all hardware components
- [ ] End-to-end wireless testing
- [ ] Battery life testing
- [ ] Reliability testing

#### User Testing
- [ ] Recruit test participants
- [ ] Conduct guided testing sessions
- [ ] Collect feedback
- [ ] Iterate on UX issues

### Timeline
**Target**: Final weeks before submission

---

## Phase 4: Documentation & Submission

### Deliverables
- [ ] Final project report
- [ ] Demo video
- [ ] User manual
- [ ] Source code documentation
- [ ] Presentation slides

---

## Risk Management

| Risk | Mitigation |
|:-----|:-----------|
| ESP32 latency issues | Pre-buffer frames, optimize compression |
| Bluetooth audio delays | Use low-latency codec, buffer management |
| Battery life concerns | Power management, efficient streaming |
| User comfort | Multiple enclosure iterations |

---

## Resource Allocation

### Hardware Budget
See [Budget.md](./Info/Budget.md) for detailed costs.

### Time Allocation
- Software refinement: 20%
- Hardware integration: 40%
- Testing & iteration: 30%
- Documentation: 10%

---

## Success Criteria

### Must Have
- [ ] Active Guidance works end-to-end
- [ ] Scene Description functional
- [ ] Wireless camera streaming
- [ ] Wireless audio I/O
- [ ] Physical button controls

### Nice to Have
- [ ] Guardian alert notifications
- [ ] Extended battery life (>4 hours)
- [ ] Compact wearable form factor

---

## Weekly Checkpoints

| Week | Focus | Deliverable |
|:-----|:------|:------------|
| Current | ESP32 WiFi streaming | Video feed in backend |
| +1 | Arduino Bluetooth | Audio communication |
| +2 | Integration testing | Full wireless demo |
| +3 | Enclosure design | 3D printed prototype |
| +4 | User testing | Feedback report |
| +5 | Final polish | Submission ready |

---

*This plan is updated as development progresses. See [Log.md](../Log.md) for detailed progress updates.*
