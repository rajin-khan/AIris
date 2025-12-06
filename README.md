<div align="center">

![AIris Banner](./Documentation/Images/AIrisBantiny.png)

---

**(pronounced: ai·ris | aɪ.rɪs)**

![Status](https://img.shields.io/badge/Status-Active%20Development-blue?style=for-the-badge&logo=target) ![Course](https://img.shields.io/badge/Course-CSE%20499A/B-orange?style=for-the-badge&logo=graduation-cap) ![Focus](https://img.shields.io/badge/Focus-Accessibility%20Technology-green?style=for-the-badge&logo=eye) ![AI](https://img.shields.io/badge/AI-Multimodal%20Vision-purple?style=for-the-badge&logo=brain)

### AI-Powered Vision Assistant for the Visually Impaired
*"AI That Opens Eyes"*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com) [![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev) [![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=flat&logo=espressif&logoColor=white)](https://espressif.com) [![License](https://img.shields.io/badge/License-MIT-brightgreen?style=flat)](LICENSE)

---

</div>

> [!NOTE]
> This project is under active development. The **core software is complete and tested**.
> Hardware integration (ESP32 + Arduino) is currently in progress.
>
> **Expected Completion: December 2025**

---

<div align="center">

## ✨ What is AIris?

</div>

**AIris** is a wearable AI assistant that helps visually impaired users **find objects** and **understand their surroundings** through real-time audio feedback. Unlike passive description tools, AIris provides **active guidance** — it doesn't just tell you what's there, it helps you reach it.

<div align="center">

### 🎯 Two Powerful Modes

</div>

<table>
<tr>
<td width="50%" align="center">

### **Active Guidance** ✅
*"Find my water bottle"*

Detects the object, tracks your hand, and guides you with audio until you touch it.

**Status: Working**

</td>
<td width="50%" align="center">

### **Scene Description** 🔄
*Continuous awareness*

Analyzes your environment and describes what's around you with safety alerts.

**Status: Testing**

</td>
</tr>
</table>

---

<div align="center">

## 🏗️ System Architecture

### Hardware Design

```mermaid
graph TB
    subgraph "👓 Wearable Unit"
        A[📷 ESP32-CAM<br/>Camera Module]
        B[🎤 Microphone]
        C[🔊 Speaker]
        D[🎛️ Arduino<br/>Audio Controller]
    end
    
    subgraph "🖥️ Server"
        E[⚡ FastAPI<br/>Backend]
        F[🧠 AI Models<br/>YOLO • MediaPipe • BLIP]
        G[💬 Groq LLM<br/>Llama 3]
        H[🌐 React<br/>Dev GUI]
    end
    
    A -->|WiFi Stream| E
    D -->|Bluetooth| E
    B --> D
    D --> C
    E --> F
    F --> G
    E --> H
    
    style A fill:#E7352C,color:#fff
    style D fill:#00979D,color:#fff
    style E fill:#009688,color:#fff
    style F fill:#4B4E9E,color:#fff
    style G fill:#C9AC78,color:#000
    style H fill:#61DAFB,color:#000
```

### Data Flow

```mermaid
graph LR
    A[📷 Camera] -->|Video| B[🎯 YOLO<br/>Detection]
    B -->|Objects| C[✋ MediaPipe<br/>Hand Track]
    C -->|Position| D[🧠 LLM<br/>Reasoning]
    D -->|Instructions| E[🔊 TTS<br/>Audio]
    E -->|Voice| F[👤 User]
    F -->|Speech| G[🎤 STT<br/>Whisper]
    G -->|Command| D
    
    style B fill:#4B4E9E,color:#fff
    style C fill:#4B4E9E,color:#fff
    style D fill:#C9AC78,color:#000
    style E fill:#009688,color:#fff
    style G fill:#009688,color:#fff
```

</div>

---

<div align="center">

## 📊 Current Progress

</div>

| Component | Status | Progress |
|:----------|:------:|:--------:|
| 🎯 **Active Guidance Mode** | ✅ Complete | ![100%](https://img.shields.io/badge/100%25-success?style=flat-square) |
| 🔍 **Scene Description Mode** | 🔄 Testing | ![90%](https://img.shields.io/badge/90%25-yellow?style=flat-square) |
| ⚡ **Backend API** | ✅ Complete | ![100%](https://img.shields.io/badge/100%25-success?style=flat-square) |
| 🌐 **Frontend GUI** | ✅ Complete | ![100%](https://img.shields.io/badge/100%25-success?style=flat-square) |
| 📷 **ESP32-CAM Integration** | 🔄 In Progress | ![40%](https://img.shields.io/badge/40%25-orange?style=flat-square) |
| 🔊 **Arduino Audio** | 🔄 In Progress | ![30%](https://img.shields.io/badge/30%25-orange?style=flat-square) |
| 📦 **Physical Device** | ⏳ Pending | ![0%](https://img.shields.io/badge/0%25-lightgrey?style=flat-square) |

<div align="center">

**Overall: ~70% Complete**

</div>

---

<div align="center">

## 🛠️ Technology Stack

</div>

<table>
<tr>
<td width="50%">

### 💻 Software

| Layer | Technology |
|:------|:-----------|
| **Backend** | FastAPI, Python 3.10+ |
| **Object Detection** | YOLOv8 (Ultralytics) |
| **Hand Tracking** | MediaPipe |
| **Scene Analysis** | BLIP |
| **LLM Reasoning** | Groq API (Llama 3) |
| **Speech-to-Text** | OpenAI Whisper |
| **Text-to-Speech** | pyttsx3 |
| **Frontend** | React, TypeScript, Vite |

</td>
<td width="50%">

### 🔌 Hardware

| Component | Technology |
|:----------|:-----------|
| **Camera** | ESP32-CAM (WiFi) |
| **Audio I/O** | Arduino + Bluetooth |
| **Microphone** | Electret/MEMS |
| **Speaker** | Mini 2W Speaker |
| **Controls** | Physical Buttons |
| **Processing** | Server/Computer |

</td>
</tr>
</table>

> **Note:** The React frontend is a development interface. The final device will be fully usable by blind users through **physical buttons and audio** alone — no screen required.

---

<div align="center">

## 📁 Repository Structure

</div>

```mermaid
graph TD
    ROOT[📂 AIRIS] --> MAIN[⭐ AIris-System<br/>Main Application]
    ROOT --> HW[🔌 Hardware<br/>ESP32 & Arduino]
    ROOT --> DOCS[📚 Documentation<br/>Project Docs]
    ROOT --> SW[📦 Archive<br/>Archived Experiments]
    
    MAIN --> BE[backend/<br/>FastAPI Server]
    MAIN --> FE[frontend/<br/>React GUI]
    
    SW --> EXP1[0-Inference-Experimental]
    SW --> EXP2[1-Inference-LLM]
    SW --> EXP3[2-Benchmarking]
    SW --> OLD[AIris-Final-App-Old]
    SW --> MORE[... more archives]
    
    style ROOT fill:#1a1a2e,color:#fff
    style MAIN fill:#C9AC78,color:#000
    style HW fill:#00979D,color:#fff
    style DOCS fill:#4B4E9E,color:#fff
    style SW fill:#333,color:#fff
```

<div align="center">

### 📂 Folder Guide

</div>

| Folder | Purpose | Status |
|:-------|:--------|:------:|
| **`AIris-System/`** | ⭐ **Main application** — Start here! Contains the working FastAPI backend and React frontend | Active |
| **`Hardware/`** | ESP32-CAM and Arduino firmware code | In Progress |
| **`Documentation/`** | PRD, plans, technical docs, images | Reference |
| **`Archive/`** | Archived experiments and prototypes from our development journey | Archive |

<details>
<summary><strong>📦 What's in Archive/?</strong></summary>

These folders document our development journey — experiments, prototypes, and iterations that led to the current implementation:

| Folder | What It Was |
|:-------|:------------|
| `0-Inference-Experimental` | Early BLIP experiments |
| `1-Inference-LLM` | First LLM integration tests |
| `2-Benchmarking` | Ollama/Raspberry Pi benchmarks |
| `3-Performance-Comparision` | Model comparison tests |
| `AIris-Core-System` | Previous core implementation |
| `AIris-Final-App-Old` | Previous app version |
| `Merged_System` | Integration experiments |
| `RSPB`, `RSPB-2` | Real-time system prototypes |

*Preserved for reference and academic documentation.*

</details>

---

<div align="center">

## 🚀 Quick Start

</div>

```bash
# Clone the repository
git clone https://github.com/rajin-khan/AIRIS.git
cd AIRIS/AIris-System

# Follow the setup guide
cat QUICKSTART.md
```

### Requirements
- Python 3.10+ and Node.js 18+
- Groq API Key (free at [console.groq.com](https://console.groq.com))
- Camera access (laptop webcam for testing)

📖 **Full setup:** [`AIris-System/README.md`](./AIris-System/README.md)

---

<div align="center">

## 📋 What's Left To Do

</div>

### 🔌 Hardware Integration *(Current Focus)*
- [ ] Complete ESP32-CAM WiFi streaming
- [ ] Finalize Arduino Bluetooth audio
- [ ] Wire physical button controls
- [ ] Design wearable enclosure (3D print)

### 🔧 Software Refinement
- [ ] Optimize Scene Description prompts
- [ ] Add guardian alert notifications
- [ ] Performance tuning for real-time streaming

### ✅ Testing & Validation
- [ ] End-to-end wireless testing
- [ ] Field testing with visually impaired users
- [ ] Battery life and reliability testing

---

<div align="center">

## 🌟 Key Features

| Feature | Description |
|:--------|:------------|
| 🎯 **Object Guidance** | Speak an object name → Get audio directions until you touch it |
| 🔍 **Scene Understanding** | Continuous environment awareness and description |
| ⚠️ **Safety Alerts** | Hazard detection with optional guardian notifications |
| 🎤 **Voice Control** | Speak commands, receive audio responses |
| 📡 **Wireless Design** | ESP32 WiFi camera + Bluetooth audio — no cables |
| 🔒 **Privacy First** | All AI processing happens on your local server |

---

## 📚 Documentation

| Document | Description |
|:---------|:------------|
| [**PRD.md**](./Documentation/PRD.md) | Product Requirements Document |
| [**Idea.md**](./Documentation/Idea.md) | Project vision and concept |
| [**Plan.md**](./Documentation/Plan.md) | Development roadmap |
| [**Structure.md**](./Documentation/Structure.md) | Detailed project structure |
| [**UseCases.md**](./Documentation/UseCases.md) | Core assistive scenarios |
| [**TechKnowledge.md**](./Documentation/Info/TechKnowledge.md) | Technology stack details |

---

## 👥 Development Team

This project is developed by:

| Name                      | Institution             | ID | GitHub | Followers |
|---------------------------|-------------------------|--  |--------|------|
| **Rajin Khan**            | North South University | 2212708042 | [![Rajin's GitHub](https://img.shields.io/badge/-rajin--khan-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/rajin-khan) | ![Followers](https://img.shields.io/github/followers/rajin-khan?label=Follow&style=social) |
| **Saumik Saha Kabbya**    | North South University | 2211204042 | [![Saumik's GitHub](https://img.shields.io/badge/-Kabbya04-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Kabbya04) | ![Followers](https://img.shields.io/github/followers/Kabbya04?label=Follow&style=social) |

---

~ as part of CSE 499A/B at North South University, building upon the foundation of [TapSense](https://github.com/rajin-khan/TapSense) to advance accessibility technology.

---

</div>
