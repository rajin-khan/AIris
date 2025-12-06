<div align="center">

# 📦 Archive

![Status](https://img.shields.io/badge/Status-Archived-lightgrey?style=for-the-badge)
![History](https://img.shields.io/badge/Development-History-blue?style=for-the-badge)

**Experiments, prototypes, and iterations from our development journey**

---

</div>

> [!NOTE]
> This folder contains **archived development history**. The current working application is in [`/AIris-System/`](../AIris-System/).

---

## What's Here?

These folders document our journey from early experiments to the current system. They're preserved for reference, academic documentation, and to show the evolution of our approach.

---

## Folder Guide

### 🧪 Early Experiments

| Folder | Date | Description |
|:-------|:-----|:------------|
| **`0-Inference-Experimental/`** | Jul 2025 | First BLIP vision model experiments. Local video-to-description pipeline with Gradio UI. |
| **`1-Inference-LLM/`** | Jul 2025 | Added LLM integration. Groq API for narrative synthesis. Prompt engineering experiments. |

### 📊 Benchmarking & Comparison

| Folder | Date | Description |
|:-------|:-----|:------------|
| **`2-Benchmarking/`** | Jul 2025 | Ollama performance tests on Raspberry Pi 5. Token generation benchmarks. |
| **`3-Performance-Comparison/`** | Jul-Aug 2025 | Systematic model comparison. Semantic similarity scoring. Multiple LLM evaluation. |

### 🔧 System Prototypes

| Folder | Date | Description |
|:-------|:-----|:------------|
| **`AIris-Core-System/`** | Aug 2025 | Consolidated core system. Prompt templates and evaluation dataset. |
| **`Activity_Execution/`** | Oct 2025 | Early activity guide experiments. Object guidance base model. |
| **`RSPB/`** | Oct 2025 | Real-time System Prototype Base. Live camera processing with BLIP. |
| **`RSPB-2/`** | Oct 2025 | Improved RSPB with STT/TTS integration. Voice interaction testing. |
| **`Merged_System/`** | Oct 2025 | Engine merge experiments. Combined scene description + activity guide. |

### 🌐 UI & Presentation

| Folder | Date | Description |
|:-------|:-----|:------------|
| **`AIris-Prototype/`** | Sep 2025 | Early React + Vite frontend prototype. UI exploration. |
| **`AIris-Final-App-Old/`** | Nov 2025 | Previous version of the full-stack app. Superseded by AIris-System. |
| **`Mockup/`** | Jun 2025 | Initial UI mockups in React/JSX. |
| **`Website/`** | Jun 2025 | Project presentation website. |
| **`Website-Old/`** | Jun 2025 | Earlier website version. |

---

## Evolution Timeline

```
May 2025    Project Genesis
    │
Jun 2025    Mockups & Website
    │
Jul 2025    BLIP Experiments → LLM Integration → Benchmarking
    │
Aug 2025    Performance Comparison → Core System
    │
Sep 2025    React Prototype → FastAPI Architecture
    │
Oct 2025    Activity Execution → RSPB → Merged System
    │
Nov 2025    Final App → AIris-System (Current)
    │
Dec 2025    Hardware Integration (ESP32 + Arduino)
```

---

## Key Learnings from Each Phase

| Phase | What We Learned |
|:------|:----------------|
| **BLIP Experiments** | Local vision models work but need LLM for coherent narratives |
| **LLM Integration** | Groq API provides ultra-fast inference; prompt engineering is critical |
| **Benchmarking** | Raspberry Pi too slow for real-time; moved to server architecture |
| **Performance Comparison** | Task-specific prompts outperform generic descriptions |
| **RSPB** | Real-time processing requires efficient frame handling |
| **Merged System** | Modular services enable clean integration of multiple features |
| **Final App** | FastAPI + React provides the right separation of concerns |

---

## Should I Use This Code?

**Probably not.** These are historical artifacts. For the current implementation:

👉 **Go to [`/AIris-System/`](../AIris-System/)** — The current, working application

---

## Why Keep This?

1. **Academic Documentation** — Shows our development process for CSE 499A/B
2. **Reference** — Useful for understanding why certain decisions were made
3. **Fallback** — Contains working code if we need to reference old approaches
4. **Learning** — Documents what worked, what didn't, and why

---

<div align="center">

*"The journey is as important as the destination"*

**Development History: May 2025 → November 2025**

</div>

