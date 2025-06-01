# 📁 AIris Project Structure

<div align="center">

![Project](https://img.shields.io/badge/Project-AIris-blue?style=for-the-badge&logo=eye)
![Phase](https://img.shields.io/badge/Phase-CSE%20499A/B-orange?style=for-the-badge&logo=folder)

**Complete file and folder organization for the AIris development lifecycle**

</div>

---

## **Root Directory Structure**

```
AIris/
├── 📁 Class/                          # Course materials & submissions
├── 📁 Documentation/                  # Project docs & research
├── 📁 Hardware/                       # Hardware designs & specs
├── 📁 Software/                       # Core software development
├── 📄 README.md                      # ✅ Main project overview
```

---

## **Class/** 
*Course deliverables and academic materials*

```
Class/
├── 📄 project-proposal.pdf
├── 📄 literature-review.pdf
├── 📄 progress-reports.pdf
├── 📄 final-report.pdf
├── 📄 presentation-slides.pptx
└── 📄 meeting-notes.md
```

---

## **Documentation/**
*Project documentation and research*

```
Documentation/
├── 📄 Idea.md                        # ✅ Main project vision
├── 📄 Structure.md                   # Main Structure File
├── 📄 ai-models-research.md          # AI model comparison
├── 📄 system-architecture.md         # Technical architecture
├── 📄 user-manual.md                 # How to use AIris
├── 📄 installation-guide.md          # Setup instructions
└── 📁 media/                         # Images, videos, demos
    ├── 🖼️ system-diagram.png
    ├── 🎥 demo-video.mp4
    └── 🔊 sample-audio.wav
```

---

## **Hardware/**
*Physical components, designs, and specifications*

```
Hardware/
├── 📁 Designs/
│   ├── 📁 3D-Models/
│   │   ├── 📄 spectacle-mount.stl
│   │   ├── 📄 pi-case.stl
│   │   ├── 📄 button-housing.stl
│   │   └── 📄 cable-management.stl
│   ├── 📁 CAD-Files/
│   │   ├── 📄 spectacle-mount.dwg
│   │   ├── 📄 pi-case.dwg
│   │   └── 📄 assembly-drawing.dwg
│   └── 📁 Schematics/
│       ├── 📄 wiring-diagram.pdf
│       ├── 📄 circuit-schematic.pdf
│       └── 📄 pin-configuration.pdf
├── 📁 Components/
│   ├── 📄 bill-of-materials.xlsx
│   ├── 📄 component-specifications.md
│   ├── 📄 vendor-information.md
│   └── 📄 cost-analysis.xlsx
├── 📁 Assembly/
│   ├── 📄 assembly-instructions.md
│   ├── 📄 wiring-guide.md
│   ├── 📄 testing-procedures.md
│   └── 📁 Photos/
│       ├── 🖼️ assembly-step-01.jpg
│       ├── 🖼️ assembly-step-02.jpg
│       └── 🖼️ final-assembly.jpg
└── 📁 Testing/
    ├── 📄 hardware-test-plan.md
    ├── 📄 stress-test-results.xlsx
    ├── 📄 durability-tests.md
    └── 📄 power-consumption-analysis.xlsx
```

---

## **Software/**
*Core application development and AI models*

```
Software/
├── 📁 airis-core/                     # Main application
│   ├── 📄 main.py                    # Application entry point
│   ├── 📄 config.py                  # Configuration management
│   ├── 📄 requirements.txt           # Python dependencies
│   ├── 📄 setup.py                   # Installation script
│   ├── 📁 src/
│   │   ├── 📄 __init__.py
│   │   ├── 📁 ai_engine/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 model_manager.py   # AI model loading/switching
│   │   │   ├── 📄 scene_analyzer.py  # Core scene description
│   │   │   ├── 📄 groq_client.py     # Groq API integration
│   │   │   ├── 📄 ollama_client.py   # Ollama integration
│   │   │   └── 📄 prompt_templates.py # Description prompts
│   │   ├── 📁 camera/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 camera_manager.py  # Camera control
│   │   │   ├── 📄 image_processor.py # Image preprocessing
│   │   │   └── 📄 button_handler.py  # Hardware button interface
│   │   ├── 📁 audio/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 tts_engine.py      # Text-to-speech
│   │   │   ├── 📄 audio_manager.py   # Audio output control
│   │   │   └── 📄 bluetooth_handler.py # Bluetooth audio
│   │   ├── 📁 core/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 application.py     # Main app logic
│   │   │   ├── 📄 state_manager.py   # Application state
│   │   │   ├── 📄 event_handler.py   # Event processing
│   │   │   └── 📄 logger.py          # Logging system
│   │   └── 📁 utils/
│   │       ├── 📄 __init__.py
│   │       ├── 📄 performance.py     # Performance monitoring
│   │       ├── 📄 power_manager.py   # Power optimization
│   │       └── 📄 helpers.py         # Utility functions
│   ├── 📁 tests/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_ai_engine.py
│   │   ├── 📄 test_camera.py
│   │   ├── 📄 test_audio.py
│   │   ├── 📄 test_integration.py
│   │   └── 📁 fixtures/
│   │       ├── 🖼️ test_image_01.jpg
│   │       ├── 🖼️ test_image_02.jpg
│   │       └── 📄 mock_data.json
│   ├── 📁 scripts/
│   │   ├── 📄 install.sh             # System setup script
│   │   ├── 📄 start_airis.sh         # Startup script
│   │   ├── 📄 benchmark.py           # Performance testing
│   │   └── 📄 model_downloader.py    # Download AI models
│   └── 📁 configs/
│       ├── 📄 default.yaml           # Default configuration
│       ├── 📄 development.yaml       # Dev environment config
│       └── 📄 production.yaml        # Production config
├── 📁 models/                         # AI Models storage
│   ├── 📁 local/
│   │   ├── 📄 model_info.json        # Model metadata
│   │   ├── 📁 llava-v1.5/            # Local vision-language model
│   │   ├── 📁 blip2-opt/             # Alternative model
│   │   └── 📄 model_comparison.md    # Performance comparison
│   └── 📁 optimized/
│       ├── 📄 quantized_llava.onnx   # Optimized models
│       └── 📄 optimization_log.md    # Optimization notes
├── 📁 tools/                         # Development tools
│   ├── 📄 model_optimizer.py         # Model optimization tool
│   ├── 📄 image_tester.py            # Image testing utility
│   ├── 📄 latency_profiler.py        # Performance profiler
│   └── 📄 dataset_generator.py       # Test data generator
├── 📁 experiments/                    # Research and prototypes
│   ├── 📁 model_comparison/
│   │   ├── 📄 llava_test.py
│   │   ├── 📄 blip2_test.py
│   │   └── 📄 results_analysis.ipynb
│   ├── 📁 optimization/
│   │   ├── 📄 quantization_test.py
│   │   └── 📄 pruning_experiment.py
│   └── 📁 prototypes/
│       ├── 📄 basic_camera_test.py
│       └── 📄 tts_prototype.py
└── 📁 deployment/                     # Deployment configurations
    ├── 📄 Dockerfile                 # Container setup
    ├── 📄 docker-compose.yml         # Multi-container setup
    ├── 📁 systemd/
    │   └── 📄 airis.service           # System service config
    └── 📁 scripts/
        ├── 📄 deploy.sh               # Deployment script
        └── 📄 update.sh               # Update script
```

---

## **Development Phases**

### **Phase 1: CSE 499A (Software Focus)**
```
⬜ Software/airis-core/main.py
⬜ Software/models/local/ (AI models)
⬜ Documentation/ai-models-research.md
⬜ Class/project-proposal.pdf
```

### **Phase 2: CSE 499B (Hardware Integration)**
```
⬜ Hardware/designs/spectacle-mount.stl
⬜ Hardware/assembly/instructions.md
⬜ Documentation/user-manual.md
```

---

<div align="center">

*This structure will evolve as AIris grows*

</div>