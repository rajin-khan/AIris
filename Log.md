<div align="center">

# AIris Development Log

![Phase](https://img.shields.io/badge/Phase-Software%20Complete-success?style=for-the-badge)
![Progress](https://img.shields.io/badge/Progress-100%25%20Core-success?style=for-the-badge)

---

## Current Sprint: Software Complete, Hardware Optional

**Goal:** Core software system complete with handsfree mode. Custom ESP32-CAM with casing designed.  
**Timeline:** December 2025  
**Status:** ✅ Core software 100% complete | 🔄 Optional hardware accessories in progress

---

## Development Timeline

<table>
  <tr>
    <td width="15%" align="center"><strong>Date</strong></td>
    <td width="75%"><strong>Entry</strong></td>
  </tr>
  <tr>
    <td align="center">
      <strong>Dec 9</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Handsfree Mode Polished</strong><br/>
      Finalized handsfree/voice-only mode implementation. Made STT robust, implemented native TTS for narration. Fixed voice control service bugs. System now fully functional with voice commands — no screen interaction needed.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Dec 9</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Handsfree Mode Initial Implementation</strong><br/>
      Initial working implementation of handsfree mode. Voice commands now control entire system. Users can switch modes, control camera, input tasks, and interact fully via voice.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Dec 8</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>YOLO Model Upgrade</strong><br/>
      Upgraded from YOLOv8s to YOLO26s for improved object detection accuracy and performance. Updated model service and documentation.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Dec 7</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Guardian Email System Complete</strong><br/>
      Implemented complete guardian email notification system. Added fall detection algorithm with email alerts. Created daily/weekly summary emails. Added risk threshold configuration. System now sends automatic safety alerts to guardians.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Dec 7</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Scene Description Upgrade</strong><br/>
      Major upgrade to Scene Description mode with improved fall detection, depth tracking, and UI overhaul. Enhanced safety alert prioritization and risk scoring.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Dec 6</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Repository Reorganization & Custom Camera Design</strong><br/>
      Complete restructure of project folders. Renamed AIris-Final-App-2 to AIris-System as main application. Moved Hardware and Documentation into organized structure. Designed custom ESP32-CAM casing (3D printable STL). Updated architecture to computer-based system with optional accessories.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Dec 5</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>ESP32-CAM Connection Flow</strong><br/>
      Implemented ESP32-CAM WiFi streaming integration with FastAPI backend. Added camera service modifications to accept ESP32 video feed.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Dec 1</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>ESP32 Firmware Development</strong><br/>
      Created esp32-cam-test folder with Arduino sketch for camera streaming. Developed Python test client for WiFi communication validation.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Nov 26</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Hardware Architecture Planning</strong><br/>
      Finalized decision to use ESP32-CAM (WiFi) + Arduino (Bluetooth) instead of Raspberry Pi. Documented new architecture and updated budget estimates.<br/>
      <em>- Rajin/Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Nov 20</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>System Testing & Refinement</strong><br/>
      Extensive testing of both Activity Guide and Scene Description modes. Fixed edge cases in hand tracking. Improved LLM prompt reliability.<br/>
      <em>- Rajin/Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Nov 16</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Final Demo System Complete</strong><br/>
      Merged all components into AIris-Final-App-2. Complete working demo with Activity Guide and Scene Description. Added evaluation dataset and ground truth files.<br/>
      <em>- Rajin/Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Nov 12</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Frontend Polish</strong><br/>
      Updated React frontend with improved UI components. Added CameraSettings panel. Enhanced visual feedback during guidance mode.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Nov 8</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Scene Description Integration</strong><br/>
      Integrated scene_description_service with frontend. Added recording functionality and observation logging. Implemented safety alert detection.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Nov 4</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Activity Guide Testing</strong><br/>
      Comprehensive testing of object guidance with various objects. Tuned distance thresholds and directional prompts. Verified hand-to-object detection accuracy.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Nov 1</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Activity Guide v1 Complete</strong><br/>
      First complete version of Activity Guide mode. YOLO detects target object, MediaPipe tracks hand, LLM generates directional guidance until hand reaches object.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Oct 27</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Hand Tracking Integration</strong><br/>
      Integrated MediaPipe hand tracking with activity guide service. Implemented distance calculation between hand and detected objects.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Oct 22</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>YOLO Object Detection</strong><br/>
      Added YOLOv8 integration to model_service. Implemented real-time object detection with bounding box extraction. Created object filtering for guidance targets.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Oct 19</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Speech I/O Implementation</strong><br/>
      Implemented STT service using Whisper for voice command recognition. Added TTS service using pyttsx3 for audio responses. RSPB-2 script with voice interaction.<br/>
      <em>- Rajin/Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Oct 14</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Real-Time System Prototype</strong><br/>
      Created RSPB folder with real-time system prototype. Implemented live camera feed processing with BLIP analysis. Added recording functionality.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Oct 8</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Engine Merge</strong><br/>
      Merged scene description and activity execution engines into unified Merged_System. Created app-v2 and app-v3 with combined functionality.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Oct 5</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Activity Execution Base</strong><br/>
      Created Activity_Execution folder with base model for object guidance. Implemented core logic for guiding user to touch objects. Added font resources for UI.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Sep 28</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>FastAPI Backend Architecture</strong><br/>
      Designed new FastAPI-based backend architecture. Created service layer pattern with modular services. Planned API routes for both operational modes.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Sep 20</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>React Frontend Setup</strong><br/>
      Set up new React + TypeScript + Vite frontend. Created AIris-Prototype with component structure. Added Tailwind CSS for styling.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Sep 12</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Architecture Decision</strong><br/>
      Decided to move from Gradio prototype to full-stack FastAPI + React application. Planned separation of backend services and frontend components.<br/>
      <em>- Rajin/Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Sep 2</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Code Cleanup</strong><br/>
      Added comprehensive .gitignore. Cleaned up repository structure. Prepared for new development phase in 499B.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Aug 12</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>499A Final Presentation</strong><br/>
      Added final presentation documentation. Updated website title. Completed CSE 499A phase with working prototype demonstration.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Aug 11</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Performance Comparison Complete</strong><br/>
      Completed comprehensive model performance comparison. Documented results for multiple LLMs. Identified best performing configurations.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Aug 5</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Evaluation Framework</strong><br/>
      Created ground truth descriptions for test videos. Developed semantic helpfulness scoring. Added task success rate metrics.<br/>
      <em>- Rajin/Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jul 29</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Performance Comparison Framework</strong><br/>
      Added 3-Performance-Comparision module. Created system prompts for different assistive scenarios. Implemented semantic similarity scoring.<br/>
      <em>- Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jul 25</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Edge Computing Benchmarks</strong><br/>
      Created Ollama benchmarking framework. Tested local LLM inference on Raspberry Pi 5 (16GB). Generated detailed performance reports with token/second metrics.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jul 24</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Folder Reorganization</strong><br/>
      Restructured Software folder with numbered prefixes. Moved test videos to custom_test folder. Organized experimental code.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jul 22</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>LLM Integration Complete</strong><br/>
      Added Groq API integration for ultra-fast LLM inference. Developed "motion analysis expert" prompt through iterative engineering. Solved LLM descriptive bias issues.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jul 18</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Prompt Engineering</strong><br/>
      Iterative refinement of system prompts. Tested multiple prompt versions for action derivation. Identified key improvements for assistive descriptions.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jul 15</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Experimental Inference Pipeline</strong><br/>
      Added BLIP vision model integration with Gradio UI. Created video-to-description pipeline. Added workplan and literature review papers. Major documentation update.<br/>
      <em>- Rajin/Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jul 8</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>BLIP Model Research</strong><br/>
      Researched vision-language models for scene understanding. Selected BLIP-image-captioning-large as initial model. Set up PyTorch environment with MPS support.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jul 1</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Development Planning</strong><br/>
      Created detailed 4-week sprint plan. Defined milestones for prototype development. Outlined evaluation strategy.<br/>
      <em>- Rajin/Kabbya</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jun 24</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Literature Review & Website</strong><br/>
      Added comprehensive literature review with research papers. Created presentation website for project showcase. Documented related work in assistive technology.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jun 19</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Visual Identity Polish</strong><br/>
      Updated banner images. Finalized AIrisBan.png and AIrisBantiny.png graphics. Established consistent visual branding.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jun 17</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Concept Visualization</strong><br/>
      Added concept images (concept a.png, concept b.png). Created visual representations of system architecture. Added multiple design iterations.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jun 12</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>README Enhancement</strong><br/>
      Updated main README with badges and mermaid diagrams. Added project vision and roadmap sections. Improved documentation formatting.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jun 11</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Vision & Mockups</strong><br/>
      Defined project vision document. Created React-based UI mockup. Established typography and color palette. Added Vision.md with brand guidelines.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jun 3</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Idea Refinement</strong><br/>
      Updated Idea.md with technical implementation details. Added architecture diagrams. Defined core features and success metrics.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Jun 1</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Documentation Foundation</strong><br/>
      Finished initial documentation structure. Added resources, budget planning, and technical knowledge base. Created development log template.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>May 27</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>Course Materials</strong><br/>
      Added CSE 499A class notes. Documented course requirements and project scope.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>May 21</strong><br/>
      <em>2025</em>
    </td>
    <td>
      <strong>🎉 Project Genesis</strong><br/>
      Initial commit. Repository created. AIris officially begins.<br/>
      <em>- Rajin</em>
    </td>
  </tr>
</table>

---

## Key Milestones

| Milestone | Date | Status |
|:----------|:-----|:------:|
| Repository created | May 21, 2025 | ✅ |
| Initial documentation | Jun 1, 2025 | ✅ |
| Vision & mockups | Jun 11, 2025 | ✅ |
| Literature review | Jun 24, 2025 | ✅ |
| BLIP inference pipeline | Jul 15, 2025 | ✅ |
| LLM integration (Groq) | Jul 22, 2025 | ✅ |
| Edge benchmarking | Jul 25, 2025 | ✅ |
| Performance comparison | Aug 11, 2025 | ✅ |
| 499A presentation | Aug 12, 2025 | ✅ |
| FastAPI architecture | Sep 20, 2025 | ✅ |
| Activity execution base | Oct 5, 2025 | ✅ |
| Engine merge | Oct 8, 2025 | ✅ |
| Speech I/O complete | Oct 19, 2025 | ✅ |
| Activity Guide v1 | Nov 1, 2025 | ✅ |
| Final demo system | Nov 16, 2025 | ✅ |
| ESP32 integration started | Dec 1, 2025 | 🔄 |
| Custom camera casing designed | Dec 6, 2025 | ✅ |
| Repo reorganization | Dec 6, 2025 | ✅ |
| YOLO26s upgrade | Dec 8, 2025 | ✅ |
| Guardian email system | Dec 7, 2025 | ✅ |
| Handsfree mode complete | Dec 9, 2025 | ✅ |
| Core software complete | Dec 9, 2025 | ✅ |
| Optional hardware accessories | Dec 2025 | 🔄 |
| Final submission | Dec 2025 | ⏳ |

---

## Contributors

| Contributor | Primary Contributions |
|:------------|:----------------------|
| **Rajin Khan** | Project lead, documentation, LLM integration, benchmarking, ESP32, architecture |
| **Saumik Saha Kabbya** | Activity execution, performance comparison, RSPB, hand tracking, YOLO integration |

---

## Development Statistics

| Metric | Value |
|:-------|------:|
| **Total Commits** | 60+ |
| **Development Duration** | 7 months |
| **Contributors** | 2 |
| **Major Features** | 6 |
| **Documentation Files** | 15+ |
| **Lines of Python** | 3000+ |
| **Lines of TypeScript** | 1500+ |

---

## Phase Summary

### Phase 1: Research & Planning *(May-Jun 2025)*
- Project inception and documentation
- Literature review and related work analysis
- Visual identity and branding
- Architecture planning

### Phase 2: Prototype Development *(Jul-Aug 2025)*
- BLIP vision model integration
- LLM integration and prompt engineering
- Performance benchmarking
- 499A presentation and evaluation

### Phase 3: Full System Development *(Sep-Nov 2025)*
- FastAPI + React architecture
- Activity Guide mode implementation
- Scene Description mode implementation
- Speech I/O integration
- System integration and testing

### Phase 4: Software Completion & Hardware Design *(Dec 2025)*
- ✅ Handsfree/voice-only mode implementation
- ✅ Guardian email system with fall detection
- ✅ YOLO26s model upgrade
- ✅ Custom ESP32-CAM casing design (3D printable)
- ✅ Repository reorganization
- ✅ Architecture shift to computer-based system
- 🔄 Optional hardware accessories (ESP32-CAM, Bluetooth audio)
- ✅ Complete documentation update

---

![Commits](https://img.shields.io/badge/Commits-60+-blue?style=flat-square)
![Duration](https://img.shields.io/badge/Duration-7%20Months-green?style=flat-square)
![Coffee](https://img.shields.io/badge/Coffee-☕%20×100-brown?style=flat-square)

</div>
