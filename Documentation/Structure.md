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
├── 📁 Documentation/                  # Project docs, research, and planning
├── 📁 Hardware/                       # Hardware designs & specs
├── 📁 Software/                       # All software development
├── 📄 README.md                      # ✅ Main project overview
└── 📄 .gitignore
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
├── 📄 Idea.md                        # ✅ High-level project vision
├── 📄 Vision.md                      # ✅ Visual identity and brand guide
├── 📄 PLAN.md                        # ✅ Detailed 4-week development plan
├── 📄 Structure.md                   # This file: Main project structure
├── 📄 research-summary.md            # Analysis of MC-ViT, Video-3D LLM, etc.
├── 📄 system-architecture.md         # Technical architecture diagrams
├── 📄 user-manual.md                 # How to use the final AIris device
└── 📁 media/                         # Images, videos, logos, and demos
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
│   │   └── 📄 pi-case.stl
│   └── 📁 Schematics/
│       ├── 📄 wiring-diagram.pdf
│       └── 📄 pin-configuration.pdf
├── 📁 Components/
│   ├── 📄 bill-of-materials.xlsx
│   └── 📄 component-specifications.md
└── 📁 Assembly/
    └── 📄 assembly-instructions.md
```

---

## **Software/**
*Core application development and AI models. This is split into two key phases.*

```
Software/
├── 📁 prototype_v1/                   # Week 1: Formalized initial prototype
│   ├── 📄 app.py                     # Gradio UI and main endpoint
│   ├── 📄 pipeline.py                # Core logic for BLIP model inference
│   ├── 📄 requirements.txt           # Dependencies for the simple prototype
│   └── 📁 sample_videos/             # Directory for test videos
│
├── 📁 airis_casd_mvp/                 # Weeks 2-4: The advanced CAS-D system
│   ├── 📄 train.py                    # Main script to run training loop
│   ├── 📄 requirements.txt           # Dependencies for the advanced model
│   ├── 📁 data/                     # For storing/caching datasets like ScanNet
│   ├── 📁 notebooks/                # Jupyter notebooks for exploration
│   └── 📁 src/
│       ├── 📄 __init__.py
│       ├── 📄 dataset.py              # PyTorch Dataset for ScanNet
│       ├── 📄 model.py                # The main AIrisModel (Encoder + Decoder)
│       ├── 📄 agent.py                # The MemoryAgent (k-means consolidation)
│       └── 📄 config.py               # Hyperparameters and settings
│
└── 📁 tools/                          # Helper scripts for data management
    └── 📄 setup_kinetics_samples.py   # Script to download sample videos
```

---

## **Development Phases**

### **Phase 1: CSE 499A (Software Foundation)**
*Focus on formalizing the initial prototype and building the advanced CAS-D engine.*

```
✅ Software/prototype_v1/                  # Week 1 Deliverable
⬜ Documentation/research-summary.md       # Week 1 Deliverable
⬜ Software/airis_casd_mvp/src/model.py    # Week 2 Deliverable
⬜ Software/airis_casd_mvp/src/dataset.py  # Week 3 Deliverable
⬜ Software/airis_casd_mvp/train.py        # Week 4 Deliverable
⬜ Class/project-proposal.pdf
```

### **Phase 2: CSE 499B (Hardware Integration & Refinement)**
*Focus on building the physical device and conducting user testing.*
```
⬜ Hardware/Designs/
⬜ Hardware/Assembly/
⬜ Documentation/user-manual.md
⬜ Class/final-report.pdf
```

---

<div align="center">

*This structure will evolve as AIris grows*

</div>