<div align="center">

# AIris: Real-Time Scene Description System

![Status](https://img.shields.io/badge/Status-Prototyping%20%26%20Development-blue?style=for-the-badge&logo=target)
![Course](https://img.shields.io/badge/Course-CSE%20499A/B-orange?style=for-the-badge&logo=graduation-cap)
![Focus](https://img.shields.io/badge/Focus-Accessibility%20Technology-green?style=for-the-badge&logo=eye)

**AI-powered instant vision for the visually impaired**

*Building upon the foundation of TapSense to create instant, intelligent visual assistance*

</div>

---

## **Project Vision**

**AIris** represents the next evolutionary step in accessibility technology for the visually impaired. Where TapSense provided powerful tools for structured tasks, AIris delivers **instant, contextual awareness** of the visual world through real-time scene description.

Imagine walking down a street, entering a new room, or navigating an unfamiliar environment, and with the simple press of a button, receiving an immediate, intelligent description of your surroundings. This is the core promise of AIris.

---

## **The Problem We're Solving**

Current visual assistance solutions fall short in several key areas:

- **Latency Issues**: Existing apps require multiple steps (open app → navigate → capture → process).
- **Cost Barriers**: Many solutions rely on expensive cloud APIs or proprietary hardware.
- **Limited Accessibility**: Smartphone-dependent solutions aren't always practical or accessible.
- **Context Gap**: Static image analysis without understanding of user intent or environment over time.

**AIris addresses these challenges with a purpose-built, wearable solution that prioritizes speed, privacy, accessibility, and independence.**

---

## **System Architecture Overview**

### Hardware Components

<table>
<tr>
<td width="33%" align="center">

### **Spectacle Camera**
Smart capture system<br/>
Integrated button control<br/>
Optimized for mobility

</td>
<td width="33%" align="center">

### **Raspberry Pi 5**
16GB RAM powerhouse<br/>
Local AI processing<br/>
Edge computing core

</td>
<td width="33%" align="center">

### **Power & Housing**
Custom pocket case<br/>
Portable power supply<br/>
All-day battery life

</td>
</tr>
</table>

### Software Architecture

<table>
<tr>
<td width="50%" align="center">

### **🎯 Context-Aware Scene Engine**
- **Position-Aware Encoder (ViT + 3D data)**
- **Memory Consolidation Agent (k-means)**
- **LLM Decoder with Cross-Attention**
- Groq/Ollama Fallback System

</td>
<td width="50%" align="center">

### **📷 Camera Interface**
Low-latency image capture<br/>
Automatic lighting adjustment<br/>
Button trigger management

</td>
</tr>
<tr>
<td width="50%" align="center">

### **🔊 Audio Output System**
Text-to-speech engine<br/>
Bluetooth audio support<br/>
Priority audio management

</td>
<td width="50%" align="center">

### **⚡ Performance Optimization**
Model quantization & caching<br/>
Background processing<br/>
Intelligent power management

</td>
</tr>
</table>

---

## **Core Features & Capabilities**

### **Instant Scene Analysis**
- **Sub-2-second** response time from button press to audio description.
- **Contextual understanding** of spatial relationships and important objects.
- **Dynamic detail levels** based on scene complexity.

### **Intelligent Description Engine**
- **Spatio-Temporal Memory:** Remembers objects and context from previous moments to inform current descriptions.
- **Object identification** with confidence levels.
- **Spatial awareness** (left/right, near/far relationships).
- **Activity recognition** (people walking, cars moving, etc.).
- **Safety alerts** (obstacles, hazards, traffic conditions).

### **Adaptive AI Processing**
- **Local-first approach** using optimized models on Raspberry Pi.
- **Smart fallback** to Groq API for complex narrative synthesis.
- **Learning capabilities** to improve descriptions based on user preferences.

### **Seamless User Experience**
- **Single-button operation** - press and receive description.
- **Hands-free design** - fully wearable and wireless.
- **Long battery life** - optimized for all-day use.
- **Weather-resistant** construction for outdoor use.

---

## **Technical Implementation Strategy**

Our development is structured into a focused 4-week sprint to build the advanced Context-Aware Spatial Description (CAS-D) system.

*   **Week 1: Formalize Prototype & Foundations**
    *   **Goal:** Refactor our current `app.py` prototype into a professional project structure and establish the theoretical groundwork for the advanced system by analyzing key research papers (MC-ViT, Video-3D LLM).
    *   **Deliverable:** A polished, runnable v1 prototype and a research summary document.

*   **Week 2: Build the Core AIris Engine**
    *   **Goal:** Implement the main `AIrisModel` class, including the `PositionAwareEncoder`, the k-means-based `MemoryAgent`, and the LLM decoder wired for cross-attention.
    *   **Deliverable:** A functional `AIrisModel` that can be tested with dummy data, proving the internal mechanics work.

*   **Week 3: Integrate the 3D Data Pipeline**
    *   **Goal:** Implement a PyTorch `Dataset` and `DataLoader` for the ScanNet dataset, capable of feeding real-world RGB, depth, and camera pose data into our model.
    *   **Deliverable:** A successful integration test showing that real data can flow through the `AIrisModel` without errors.

*   **Week 4: End-to-End Proof-of-Concept**
    *   **Goal:** Implement a full training loop, run it on a small subset of the data, and demonstrate that the training loss decreases. This proves the entire architecture is viable and can learn.
    *   **Deliverable:** A functional, end-to-end MVP codebase with a `README.md`, and a near-complete research proposal draft.

---

## **Technology Stack**

### **Software Technologies**
| Component | Technology | Purpose |
|:---|:---|:---|
| **Core Language** | Python 3.11+ | Main development language |
| **Computer Vision** | OpenCV, PIL, Open3D | Image, video, and 3D data processing |
| **AI/ML Framework** | PyTorch, Transformers, `timm` | Local model inference and architecture |
| **API Integration** | Groq SDK, Ollama API | Cloud/local LLM for narrative synthesis |
| **Audio Processing** | pyttsx3, pygame | Text-to-speech and audio management |
| **Hardware Interface** | RPi.GPIO, picamera2 | Raspberry Pi hardware control |
| **Optimization** | ONNX Runtime, TensorRT | Model acceleration (Future Goal) |

### **Hardware Components**
| Component | Specification | Purpose |
|:---|:---|:---|
| **Processing Unit** | Raspberry Pi 5 (8GB RAM) | Main computing platform |
| **Camera** | High-res USB/CSI module | Image capture |
| **Button** | Tactile switch with long wire | User input trigger |
| **Audio Output** | Bluetooth/3.5mm jack | Description delivery |
| **Power Supply** | Portable battery pack (10,000mAh+) | Portable power |
| **Enclosure** | Custom 3D-printed case | Protection and portability |

---

## **Success Metrics & Goals**

### **Performance Targets**
- **Latency**: < 2 seconds from button press to audio start.
- **Accuracy**: > 85% object identification accuracy.
- **Contextual Accuracy:** High score on our novel, context-dependent Q&A evaluation.
- **Battery Life**: > 8 hours continuous use.
- **Description Quality**: Natural, helpful, and contextually relevant.

### **User Experience Goals**
- **Ease of Use**: Single-button operation.
- **Reliability**: 99%+ uptime during testing.
- **Portability**: Comfortable for extended wear.
- **Independence**: Fully offline capable (with online enhancement).

### **Technical Achievements**
- **Cost-Effective**: Total hardware cost < $200.
- **Open Source**: All software freely available.
- **Extensible**: Modular architecture for additional features.
- **Cross-Platform**: Adaptable to other hardware platforms.

---

## **Impact & Future Vision**

### **Immediate Impact**
AIris will provide visually impaired individuals with unprecedented real-time awareness of their environment, enhancing safety, independence, and confidence in navigation and daily activities.

### **Long-term Vision**
- **Community Platform**: Open-source ecosystem for accessibility technology.
- **AI Enhancement**: Continuous learning from anonymized usage data.
- **Feature Expansion**: Navigation assistance, facial recognition, document reading.
- **Hardware Evolution**: Integration with AR glasses, smaller form factors.

### **Research Contributions**
- **Novel Framework:** A new architecture for spatio-temporal context in assistive tech.
- **Edge AI Optimization**: Techniques for running complex vision-language models on constrained hardware.
- **Accessibility Interface Design**: Best practices for wearable assistive technology.

---

## **Getting Started**

### **Development Environment Setup**
```bash
# Set up a Conda environment
conda create -n airis_casd python=3.10 -y
conda activate airis_casd

# Project Dependencies
pip install torch torchvision transformers opencv-python-headless
pip install timm numpy open3d # For advanced model
pip install groq ollama # For LLM integration
pip install pyttsx3 pygame RPi.GPIO picamera2 # For hardware
```

### **Repository Structure**
```
airis_project/
├── data/                  # For dataset files (e.g., ScanNet)
├── notebooks/             # For exploration and visualization
├── src/
│   ├── dataset.py         # Data loading and preprocessing
│   ├── model.py           # The main AIris model architecture
│   ├── agent.py           # The memory consolidation agent
│   ├── train.py           # Training and evaluation loop
│   └── config.py          # Hyperparameters and settings
├── README.md
└── requirements.txt
```

---

## **Academic Integration**

This project directly builds upon the **TapSense** foundation from CSE 299, extending its accessibility mission into real-time environmental awareness. The technical challenges span multiple computer science disciplines:

- **Computer Vision & AI**: Scene understanding and model optimization.
- **Systems Programming**: Real-time processing and hardware integration.
- **Human-Computer Interaction**: Accessibility-focused interface design.
- **Embedded Systems**: Resource-constrained computing optimization.

**AIris** represents a practical application of cutting-edge AI research to solve real-world accessibility challenges, with the potential for significant social impact and technical innovation.

---

<div align="center">

**Empowering Vision Through Innovation**

*Where TapSense gave tools, AIris gives sight.*

</div>