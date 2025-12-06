<div align="center">

# AIris Performance Evaluation Report

![Phase](https://img.shields.io/badge/Evaluation-Early%20Prototype-orange?style=flat-square)
![Date](https://img.shields.io/badge/Date-August%202025-blue?style=flat-square)

</div>

> [!NOTE]
> **Historical Document:** This report evaluates an early prototype from August 2025 using the BLIP + LLM pipeline. The current system (November 2025+) uses YOLOv8 + MediaPipe + Groq and achieves significantly better performance with <2 second latency.

---

This report documents the performance of the early AIris prototype against our custom evaluation dataset. The goal was to benchmark the system's effectiveness in addressing its primary assistive use cases for visually impaired users.

---

## I. Quantitative & Qualitative Results

The following table summarizes the performance across three core scenarios: Indoor Navigation, Object Finding, and Dynamic Hazard Detection.

| Video ID                 | Latency (s) | Semantic Helpfulness Score | Task Success Rate | Safety Score | LLM Used             |
| ------------------------ | :---------: | :------------------------: | :---------------: | :----------: | -------------------- |
| `indoor_nav_01.mp4`      |   14.09s    |            0.87            |        Yes        |      1       | openai/gpt-oss-120b |
| `object_find_01.mp4`     |    5.61s    |            0.75            |        No         |     N/A      | openai/gpt-oss-120b |
| `dynamic_hazard_01.mp4`  |   16.86s    |        **0.40** (Critically Low)        |        No         |      0       | openai/gpt-oss-120b |

---

## II. Analysis of Findings

The evaluation revealed that the core pipeline was functional but highlighted several critical areas for improvement.

### Key Successes:
*   **Contextual Understanding:** The system successfully identified the general context of the environment in the navigation and object-finding scenarios (correctly identifying a "bedroom" and a "laptop on a table").
*   **Prompt Adherence (Brevity):** The refined prompts were successful in forcing the LLM to produce a concise, 1-2 sentence summary, eliminating the previous issues with conversational fluff.

### Critical Challenges:

1.  **High Latency:** The system's latency (5.6s to 16.8s) was significantly higher than the sub-2-second target required for real-time assistance. This was the most pressing technical hurdle to overcome.

2.  **Lack of Assistive Specificity (Object Finder):** In the object-finding test, the AI identified the correct objects but failed to provide their *relative positions* ("on your right," "next to"). This made the description unhelpful for localization by touch.

3.  **Critical Safety Failure (Hazard Detection):** The system made a dangerous error in the hazard detection test. It incorrectly identified a person "walking away" as "walking towards you."

---

## III. How These Issues Were Addressed

The challenges identified in this evaluation directly informed the development of the current AIris system:

| Challenge | Solution Implemented |
|:----------|:--------------------|
| **High Latency** | Switched to YOLOv8 for real-time detection + Groq API for ultra-fast LLM inference |
| **No Relative Positions** | Added MediaPipe hand tracking + spatial relationship calculation |
| **Hazard Detection Failures** | Moved from passive description to active guidance with continuous tracking |

---

## IV. Current System Performance

The current AIris system (as of November 2025) achieves:

| Metric | Early Prototype | Current System |
|:-------|:---------------:|:--------------:|
| **Latency** | 5-17 seconds | <2 seconds |
| **Object Detection** | BLIP captioning | YOLOv8 real-time |
| **Guidance** | Passive description | Active directional guidance |
| **Hand Tracking** | None | MediaPipe integration |

---

*This document is preserved for historical reference and to document the project's evolution.*
