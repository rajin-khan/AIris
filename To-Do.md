# AIris To-Do List

## Current Focus: Hardware Integration

---

## Software ✅ (Complete)

- [x] FastAPI backend architecture
- [x] React frontend (development GUI)
- [x] Active Guidance mode (YOLO26s + MediaPipe + LLM)
- [x] Scene Description mode (BLIP + LLM) with fall detection
- [x] Speech-to-text (Whisper - offline)
- [x] Text-to-speech (pyttsx3 - native)
- [x] Handsfree/Voice-Only mode (full voice control)
- [x] Guardian email alerts (safety notifications)
- [x] Daily/weekly summary emails
- [x] Risk threshold configuration
- [x] API documentation
- [x] WebSocket video streaming

---

## Hardware Accessories 🔄 (Optional - In Progress)

**Note:** The system runs entirely on your computer. These are optional accessories for enhanced handsfree operation.

### ESP32-CAM (Optional)
- [x] Acquire ESP32-CAM module
- [x] Basic camera test
- [ ] WiFi streaming firmware
- [ ] Connect to FastAPI backend
- [ ] Optimize for latency

### Bluetooth Audio (Optional)
- [x] Architecture shift to separate Bluetooth mic/headphone
- [ ] Bluetooth microphone pairing and setup
- [ ] Bluetooth headphone pairing and setup
- [ ] Audio input handling (mic → computer)
- [ ] Audio output handling (computer → headphone)
- [ ] Integrate with backend

**Controls:** Voice commands via Handsfree Mode handle all control — no physical buttons needed.

---

## Integration ⏳ (Pending)

- [ ] End-to-end wireless testing
- [ ] Full system demo
- [ ] Battery life testing
- [ ] Reliability testing

---

## Refinement ⏳ (Pending)

- [x] Scene Description prompt optimization
- [x] Guardian alert system
- [x] Safety hazard prioritization (fall detection implemented)
- [x] Risk threshold configuration
- [ ] Response latency optimization
- [ ] Voice command recognition improvements

---

## Documentation ⏳ (Pending)

- [ ] User manual
- [ ] Demo video
- [ ] Final project report
- [ ] Presentation slides

---

## Testing ⏳ (Pending)

- [ ] Wearable enclosure design
- [ ] 3D print prototype
- [ ] User field testing
- [ ] Iterate on feedback

---

## Priority Order

1. ✅ **Core Software** — Complete (runs on computer)
2. ✅ **Handsfree Voice Control** — Complete (voice commands work)
3. **ESP32 WiFi streaming** (optional) — Get video feed working wirelessly
4. **Bluetooth mic/headphone** (optional) — Get voice I/O working wirelessly
5. **End-to-end testing** — Validate system with optional accessories
6. **User testing** — Get feedback from blind users

## Recent Completions (December 2025)

- ✅ **Handsfree Mode**: Full voice control implementation
- ✅ **YOLO26s Upgrade**: Updated from YOLOv8s to YOLO26s
- ✅ **Guardian Email System**: Complete with alerts, daily/weekly summaries
- ✅ **Fall Detection**: Advanced algorithm with email notifications
- ✅ **Risk Threshold**: Configurable sensitivity (0.1 - 0.5)
- ✅ **Architecture Shift**: Moved to ESP32-CAM + Bluetooth mic/headphone (separate components)

---

*Last updated: December 2025*
