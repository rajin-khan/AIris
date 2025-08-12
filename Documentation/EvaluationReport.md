# AIris Performance Evaluation Report

This report documents the performance of the AIris Core System against our custom evaluation dataset. The goal is to benchmark the system's effectiveness in addressing its primary assistive use cases for visually impaired users.

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

The evaluation reveals that the core pipeline is functional but highlights several critical areas for improvement before it can be considered a reliable assistive tool.

### Key Successes:
*   **Contextual Understanding:** The system successfully identified the general context of the environment in the navigation and object-finding scenarios (correctly identifying a "bedroom" and a "laptop on a table").
*   **Prompt Adherence (Brevity):** The refined prompts were successful in forcing the LLM to produce a concise, 1-2 sentence summary, eliminating the previous issues with conversational fluff.

### Critical Challenges:

1.  **High Latency:** The system's latency (5.6s to 16.8s) is significantly higher than the sub-2-second target required for real-time assistance. This is the most pressing technical hurdle to overcome. The high number of frames analyzed is likely the primary cause.

2.  **Lack of Assistive Specificity (Object Finder):** In the object-finding test, the AI identified the correct objects but failed to provide their *relative positions* ("on your right," "next to"). This makes the description unhelpful for the core task of localization by touch. The task success was marked as **"No"** for this reason.

3.  **Critical Safety Failure (Hazard Detection):** The system made a dangerous and unacceptable error in the hazard detection test. It incorrectly identified a person "walking away" as "walking towards you." This misinformation is more dangerous than no information at all. The Semantic Score is critically low, and the Safety Score is **0 (Missed/Misinformed Hazard)**.

---

## III. Conclusion & Next Steps for 499B

This evaluation validates that our two-stage architecture (Vision -> Reasoning) is a viable approach for generating descriptive summaries from video. However, it also proves that both performance and reasoning accuracy must be drastically improved.

Our next steps for the project will be:

*   **Latency Optimization:** Prioritize reducing the pipeline's latency. This will involve experimenting with fewer frames, exploring more efficient vision models (like MobileNet), and optimizing data transfer between processes.
*   **Advanced Prompt Engineering:** Further refine the prompts to explicitly demand critical assistive details, such as relative directions ("to your left/right") and actionable safety information ("the path is clear").
*   **Re-evaluate Hazard Detection:** The safety failure in the hazard test indicates either the raw observations from BLIP were insufficient or the LLM's reasoning was flawed. This specific use case requires a more robust and reliable implementation, potentially with a model fine-tuned for motion detection.