# 🌟 AIris: Real-Time Scene Description System

<div align="center">

![Status](https://img.shields.io/badge/Status-Planning%20Phase-blue?style=for-the-badge&logo=target)
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

- **Latency Issues**: Existing apps require multiple steps (open app → navigate → capture → process)
- **Cost Barriers**: Many solutions rely on expensive cloud APIs or proprietary hardware
- **Limited Accessibility**: Smartphone-dependent solutions aren't always practical or accessible
- **Context Gap**: Static image analysis without understanding of user intent or environment

**AIris addresses these challenges with a purpose-built, wearable solution that prioritizes speed, accessibility, and independence.**

---

## **System Architecture Overview**

## Hardware Components

<table>
<tr>
<td width="33%" align="center">

### **Spectacle Camera**
Smart capture system  
Integrated button control  
Optimized for mobility  

</td>
<td width="33%" align="center">

### **Raspberry Pi 5**
8GB RAM powerhouse  
Local AI processing  
Edge computing core  

</td>
<td width="33%" align="center">

### **Power & Housing**
Custom pocket case  
Portable power supply  
All-day battery life  

</td>
</tr>
</table>

## Software Architecture

<table>
<tr>
<td width="50%" align="center">

### **🎯 Scene Description Engine**
Local AI models (primary)  
Groq API fallback system  
Ollama LLM integration  

</td>
<td width="50%" align="center">

### **📷 Camera Interface**
Low-latency image capture  
Automatic lighting adjustment  
Button trigger management  

</td>
</tr>
<tr>
<td width="50%" align="center">

### **🔊 Audio Output System**
Text-to-speech engine  
Bluetooth audio support  
Priority audio management  

</td>
<td width="50%" align="center">

### **⚡ Performance Optimization**
Model caching & preloading  
Background processing  
Intelligent power management  

</td>
</tr>
</table>

---

## **Core Features & Capabilities**

### **Instant Scene Analysis**
- **Sub-2-second** response time from button press to audio description
- **Contextual understanding** of spatial relationships and important objects
- **Dynamic detail levels** based on scene complexity

### **Intelligent Description Engine**
- **Object identification** with confidence levels
- **Spatial awareness** (left/right, near/far relationships)
- **Activity recognition** (people walking, cars moving, etc.)
- **Safety alerts** (obstacles, hazards, traffic conditions)

### **Adaptive AI Processing**
- **Local-first approach** using optimized models on Raspberry Pi
- **Smart fallback** to Groq API for complex scenes requiring more processing power
- **Learning capabilities** to improve descriptions based on user preferences

### **Seamless User Experience**
- **Single-button operation** - press and receive description
- **Hands-free design** - fully wearable and wireless
- **Long battery life** - optimized for all-day use
- **Weather-resistant** construction for outdoor use

---

## **Technical Implementation Strategy**

### **Phase 1: CSE 499A - Software Foundation**

#### **Core Development Goals:**
1. **AI Model Research & Selection**
   - Evaluate lightweight vision-language models (LLaVA, MiniGPT-4, BLIP-2)
   - Benchmark performance on Raspberry Pi 5
   - Implement Groq API integration as backup
   - Set up Ollama for local LLM processing

2. **Scene Description Engine**
   - Develop intelligent prompting strategies for optimal descriptions
   - Create context-aware description templates
   - Implement confidence-based description filtering
   - Build audio output optimization

3. **Camera Integration & Testing**
   - USB/CSI camera module integration
   - Real-time image capture optimization
   - Lighting condition handling
   - Button trigger implementation

4. **Performance Optimization**
   - Model quantization for faster inference
   - Memory management for 8GB RAM constraint
   - Background processing architecture
   - Latency measurement and optimization

#### **Deliverables:**
- Fully functional prototype running on Raspberry Pi 5
- Comprehensive performance benchmarks
- Working camera integration with button trigger
- Audio description system with TTS
- Documentation of AI model comparison and selection

### **Phase 2: CSE 499B - Hardware Integration & Refinement**

#### **Hardware Development Goals:**
1. **Custom Hardware Design**
   - 3D-printed spectacle mount for camera
   - Ergonomic button placement and wiring
   - Compact Raspberry Pi case design
   - Portable power supply solution

2. **Wiring & Electronics**
   - Long-wire camera connection design
   - Button integration with proper debouncing
   - Power management system
   - Bluetooth audio integration

3. **User Experience Optimization**
   - Field testing with actual users
   - Ergonomic refinements
   - Battery life optimization
   - Durability and weather-proofing

4. **Final System Integration**
   - Complete hardware-software integration
   - Production-ready prototype
   - User manual and setup documentation
   - Performance validation in real-world scenarios

---

## **Technology Stack**

### **Software Technologies**
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Core Language** | Python 3.11+ | Main development language |
| **Computer Vision** | OpenCV, PIL | Image processing and optimization |
| **AI/ML Framework** | PyTorch, Transformers | Local model inference |
| **API Integration** | Groq SDK, Ollama API | Cloud/local LLM integration |
| **Audio Processing** | pyttsx3, pygame | Text-to-speech and audio management |
| **Hardware Interface** | RPi.GPIO, picamera2 | Raspberry Pi hardware control |
| **Optimization** | ONNX Runtime, TensorRT | Model acceleration |

### **Hardware Components**
| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Processing Unit** | Raspberry Pi 5 (8GB RAM) | Main computing platform |
| **Camera** | High-res USB/CSI module | Image capture |
| **Button** | Tactile switch with long wire | User input trigger |
| **Audio Output** | Bluetooth/3.5mm jack | Description delivery |
| **Power Supply** | Portable battery pack (10,000mAh+) | Portable power |
| **Enclosure** | Custom 3D-printed case | Protection and portability |

---

## **Success Metrics & Goals**

### **Performance Targets**
- **Latency**: < 2 seconds from button press to audio start
- **Accuracy**: > 85% object identification accuracy
- **Battery Life**: > 8 hours continuous use
- **Description Quality**: Natural, helpful, contextually relevant

### **User Experience Goals**
- **Ease of Use**: Single-button operation
- **Reliability**: 99%+ uptime during testing
- **Portability**: Comfortable for extended wear
- **Independence**: Fully offline capable (with online enhancement)

### **Technical Achievements**
- **Cost-Effective**: Total hardware cost < $200
- **Open Source**: All software freely available
- **Extensible**: Plugin architecture for additional features
- **Cross-Platform**: Adaptable to other hardware platforms

---

## **Impact & Future Vision**

### **Immediate Impact**
AIris will provide visually impaired individuals with unprecedented real-time awareness of their environment, enhancing safety, independence, and confidence in navigation and daily activities.

### **Long-term Vision**
- **Community Platform**: Open-source ecosystem for accessibility technology
- **AI Enhancement**: Continuous learning from anonymized usage data
- **Feature Expansion**: Navigation assistance, facial recognition, document reading
- **Hardware Evolution**: Integration with AR glasses, smaller form factors

### **Research Contributions**
- **Edge AI Optimization**: Techniques for running vision-language models on constrained hardware
- **Accessibility Interface Design**: Best practices for wearable assistive technology
- **Real-time Scene Understanding**: Novel approaches to contextual visual description

---

## **Getting Started**

### **Development Environment Setup**
```bash
# Raspberry Pi 5 Setup
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git

# Project Dependencies
pip install torch torchvision transformers
pip install opencv-python pillow groq ollama
pip install pyttsx3 pygame RPi.GPIO picamera2
```

### **Repository Structure**
```
AIris/
├── src/
│   ├── ai_engine/          # AI model handling
│   ├── camera_interface/   # Camera and hardware control
│   ├── audio_system/       # TTS and audio management
│   └── core/              # Main application logic
├── models/                # Local AI models
├── hardware/              # 3D models and wiring diagrams
├── docs/                  # Documentation and research
└── tests/                 # Testing and benchmarks
```

---

## **Academic Integration**

This project directly builds upon the **TapSense** foundation from CSE 299, extending its accessibility mission into real-time environmental awareness. The technical challenges span multiple computer science disciplines:

- **Computer Vision & AI**: Scene understanding and model optimization
- **Systems Programming**: Real-time processing and hardware integration
- **Human-Computer Interaction**: Accessibility-focused interface design
- **Embedded Systems**: Resource-constrained computing optimization

**AIris** represents a practical application of cutting-edge AI technology to solve real-world accessibility challenges, with the potential for significant social impact and technical innovation.

---

<div align="center">

**Empowering Vision Through Innovation**

*Where TapSense gave tools, AIris gives sight.*

</div>