<div align="center">

# AIris: AI-Powered Vision Assistant

![Status](https://img.shields.io/badge/Status-Active%20Development-blue?style=for-the-badge&logo=target)
![Course](https://img.shields.io/badge/Course-CSE%20499A/B-orange?style=for-the-badge&logo=graduation-cap)
![Focus](https://img.shields.io/badge/Focus-Accessibility%20Technology-green?style=for-the-badge&logo=eye)

**Helping visually impaired users navigate and interact with their environment**

*Building upon the foundation of TapSense to create active, intelligent visual assistance*

</div>

---

## **The Vision**

**AIris** is a wearable AI assistant that gives visually impaired users real-time awareness of their surroundings. Unlike passive description tools, AIris provides **active guidance** — it doesn't just tell you what's there, it helps you find and reach things.

Imagine asking "where are my keys?" and receiving step-by-step audio directions until your hand touches them. That's AIris.

---

## **The Problem**

Current visual assistance solutions fall short:

| Problem | Impact |
|:--------|:-------|
| **Passive descriptions only** | "There's a cup on the table" doesn't help you grab it |
| **Smartphone dependency** | Navigating apps isn't accessible for blind users |
| **High latency** | 5+ second delays break the flow of natural interaction |
| **Cloud dependency** | Privacy concerns, requires internet |
| **No spatial guidance** | Knowing an object exists ≠ knowing how to reach it |

**AIris solves these with active, real-time, hands-free guidance.**

---

## **The Solution**

### Two Complementary Modes

<table>
<tr>
<td width="50%" align="center">

### 🎯 Active Guidance
**"Find my water bottle"**

Detects the object, tracks your hand, and guides you with audio instructions until you can touch it.

*"Move your hand left... forward... almost there... got it!"*

</td>
<td width="50%" align="center">

### 🔍 Scene Description
**Continuous awareness**

Analyzes your environment and describes what's around you, prioritizing safety information.

*"You're in the kitchen. Counter ahead with objects. Clear path to your right."*

</td>
</tr>
</table>

---

## **System Design**

### Hardware Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Wearable Device                    │
│                                                     │
│   ┌─────────────┐           ┌─────────────┐        │
│   │  ESP32-CAM  │           │   Arduino   │        │
│   │  (Camera)   │           │ (Mic/Speaker)│        │
│   └──────┬──────┘           └──────┬──────┘        │
│          │                         │               │
│          │ WiFi                    │ Bluetooth     │
│          │                         │               │
└──────────┼─────────────────────────┼───────────────┘
           │                         │
           └────────────┬────────────┘
                        │
                        ▼
           ┌────────────────────────┐
           │   Server / Computer    │
           │                        │
           │  • FastAPI Backend     │
           │  • YOLO Detection      │
           │  • Hand Tracking       │
           │  • LLM Reasoning       │
           │  • Speech I/O          │
           │                        │
           │  • React Frontend      │
           │    (Dev GUI only)      │
           └────────────────────────┘
```

### Why This Architecture?

| Choice | Reason |
|:-------|:-------|
| **ESP32-CAM over USB camera** | Wireless, wearable-friendly, low cost |
| **Arduino for audio** | Bluetooth support, dedicated audio handling |
| **Server-based processing** | Full AI power, no device size constraints |
| **Physical buttons** | Accessible to blind users, no screen needed |
| **WiFi + Bluetooth** | No cables, freedom of movement |

---

## **Technology Stack**

### Software

| Component | Technology | Purpose |
|:----------|:-----------|:--------|
| **Backend** | FastAPI (Python) | API server, service orchestration |
| **Object Detection** | YOLOv8 | Real-time object recognition |
| **Hand Tracking** | MediaPipe | Track user's hand position |
| **Image Understanding** | BLIP | Scene captioning |
| **Reasoning** | Groq API (Llama 3) | Generate guidance instructions |
| **Speech-to-Text** | Whisper | Voice command recognition |
| **Text-to-Speech** | pyttsx3 | Audio response generation |
| **Frontend** | React + TypeScript | Development/testing interface |

### Hardware

| Component | Technology | Purpose |
|:----------|:-----------|:--------|
| **Camera** | ESP32-CAM | Wireless video capture |
| **Audio** | Arduino + Bluetooth module | Mic input, speaker output |
| **Controls** | Physical buttons | Mode selection, activation |
| **Processing** | Any computer/server | Run AI models |

---

## **Current Status**

### What's Working ✅

- **Active Guidance Mode** — Tested with laptop camera, guides user to objects
- **Scene Description Mode** — Core functionality complete
- **Backend API** — All services operational
- **Frontend GUI** — Development interface ready
- **Voice Commands** — Whisper STT working
- **Audio Responses** — TTS working

### In Progress 🔄

- **ESP32-CAM integration** — WiFi streaming to server
- **Arduino audio** — Bluetooth communication
- **Guardian alerts** — Safety notification system

### Coming Up ⏳

- **Physical buttons** — Hardware controls
- **Wearable enclosure** — 3D printed case
- **User testing** — Field trials with blind users

---

## **Key Differentiators**

| Feature | AIris | Traditional Apps |
|:--------|:------|:-----------------|
| **Active guidance** | ✅ Guides you TO objects | ❌ Only describes |
| **Hands-free** | ✅ Voice + buttons | ❌ Touch screen |
| **Real-time** | ✅ <2 second response | ❌ 5+ seconds |
| **Privacy** | ✅ Local processing | ❌ Cloud upload |
| **Wearable** | ✅ Wireless, portable | ❌ Phone in hand |

---

## **Success Metrics**

| Metric | Target |
|:-------|:-------|
| **Guidance latency** | < 2 seconds |
| **Object detection accuracy** | > 85% |
| **Voice recognition accuracy** | > 90% |
| **User task success rate** | > 80% |

---

## **Impact**

### For Users
- Find objects without sighted assistance
- Navigate unfamiliar spaces with confidence
- Receive safety alerts about hazards
- Maintain independence in daily activities

### For Caregivers
- Peace of mind with guardian alerts
- Reduced need for constant assistance
- Emergency notification system

---

## **Academic Context**

This project is developed as part of **CSE 499A/B** at North South University, building upon the accessibility technology foundation established by [TapSense](https://github.com/rajin-khan/TapSense).

The work spans multiple computer science domains:
- **Computer Vision** — Object detection, scene understanding
- **Natural Language Processing** — LLM reasoning, speech processing
- **Embedded Systems** — ESP32, Arduino integration
- **Human-Computer Interaction** — Accessible interface design

---

<div align="center">

**AIris: AI That Opens Eyes**

*Empowering independence through intelligent vision assistance*

</div>
