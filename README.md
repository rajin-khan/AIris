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
> Core software complete. Custom ESP32-CAM with casing designed. Optional hardware accessories in progress.
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

### System Architecture

```mermaid
graph TB
    subgraph "💻 Computer/Server"
        E[⚡ FastAPI<br/>Backend]
        F[🧠 AI Models<br/>YOLO26 • MediaPipe • BLIP]
        G[💬 Groq LLM<br/>Llama 3]
        H[🌐 React<br/>Frontend]
        I[📧 Email Service<br/>Guardian Alerts]
        J[📷 Built-in<br/>Webcam/Mic]
    end
    
    subgraph "🔌 Optional Accessories"
        A[📷 ESP32-CAM<br/>WiFi Camera]
        B[🎤 Bluetooth<br/>Microphone]
        C[🎧 Bluetooth<br/>Headphone]
    end
    
    A -.->|WiFi Optional| E
    B -.->|Bluetooth Optional| E
    E -.->|Bluetooth Optional| C
    J -->|Default| E
    E --> F
    F --> G
    E --> H
    E --> I
    
    style E fill:#009688,color:#fff
    style F fill:#4B4E9E,color:#fff
    style G fill:#C9AC78,color:#000
    style H fill:#61DAFB,color:#000
    style I fill:#C75050,color:#fff
    style J fill:#666,color:#fff
    style A fill:#E7352C,color:#fff,stroke-dasharray: 5 5
    style B fill:#00979D,color:#fff,stroke-dasharray: 5 5
    style C fill:#00979D,color:#fff,stroke-dasharray: 5 5
```

**Note:** Dashed lines indicate optional accessories. The system runs entirely on your computer with built-in webcam/mic by default.

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
| 🔍 **Scene Description Mode** | ✅ Complete | ![100%](https://img.shields.io/badge/100%25-success?style=flat-square) |
| 🎤 **Handsfree Voice Mode** | ✅ Complete | ![100%](https://img.shields.io/badge/100%25-success?style=flat-square) |
| 📧 **Guardian Email Alerts** | ✅ Complete | ![100%](https://img.shields.io/badge/100%25-success?style=flat-square) |
| ⚡ **Backend API** | ✅ Complete | ![100%](https://img.shields.io/badge/100%25-success?style=flat-square) |
| 🌐 **Frontend GUI** | ✅ Complete | ![100%](https://img.shields.io/badge/100%25-success?style=flat-square) |
| 📷 **ESP32-CAM (Optional)** | 🔄 Optional | ![40%](https://img.shields.io/badge/40%25-orange?style=flat-square) |
| 🎧 **Bluetooth Audio (Optional)** | 🔄 Optional | ![30%](https://img.shields.io/badge/30%25-orange?style=flat-square) |

<div align="center">

**Core Software: 100% Complete**  
**Optional Hardware Accessories: In Progress**

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
| **Object Detection** | YOLO26s (Ultralytics) |
| **Hand Tracking** | MediaPipe |
| **Scene Analysis** | BLIP |
| **LLM Reasoning** | Groq API (Llama 3) |
| **Speech-to-Text** | Whisper (offline) |
| **Text-to-Speech** | pyttsx3 (native) |
| **Email Notifications** | aiosmtplib (Gmail SMTP) |
| **Frontend** | React, TypeScript, Vite |

</td>
<td width="50%">

### 🔌 Hardware

| Component | Technology | Required? |
|:----------|:-----------|:---------:|
| **Camera** | Built-in webcam (default) or **Custom ESP32-CAM with casing** ⭐ (recommended) | No |
| **Audio Input** | Built-in mic (default) or Bluetooth Microphone (optional) | No |
| **Audio Output** | Built-in speakers (default) or Bluetooth Headphone (optional) | No |
| **Controls** | Voice Commands (handsfree mode) | Yes |
| **Processing** | Computer/Server | Yes |

**Note:** We've designed a custom ESP32-CAM with protective casing (see `Hardware/cam-casing/`) — recommended for best handsfree experience. However, the system works perfectly with built-in hardware by default for maximum accessibility.

</td>
</tr>
</table>

> **Note:** The React frontend is a development interface. The system is fully usable by blind users through **handsfree voice commands** — no screen or physical buttons required.

---

<div align="center">

## 📁 Repository Structure

</div>

```mermaid
graph TD
    ROOT[📂 AIRIS] --> MAIN[⭐ AIris-System<br/>Main Application]
    ROOT --> HW[🔌 Hardware<br/>Custom ESP32-CAM]
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
| **`Hardware/`** | Custom ESP32-CAM casing design & firmware | Optional |
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
- [ ] Finalize Bluetooth mic/headphone integration (optional)
- ✅ Voice control complete (no physical buttons needed)
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
| 🔍 **Scene Understanding** | Continuous environment awareness with fall detection |
| ⚠️ **Safety Alerts** | Automatic fall detection with guardian email notifications |
| 🎤 **Handsfree Mode** | Full voice control — no screen interaction required |
| 📧 **Guardian Features** | Daily/weekly summaries and configurable risk thresholds |
| 📡 **Custom Hardware** | Custom ESP32-CAM with casing (recommended) + Bluetooth mic/headphone (optional) |
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
