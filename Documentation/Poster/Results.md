# Results & Evaluation

The system was evaluated against a custom dataset of video scenarios representing common daily tasks for the visually impaired. We benchmarked the final system against our initial prototype to quantify improvements.

### Performance Metrics

| Metric | Early Prototype (Aug '25) | **Final System (Current)** | Improvement |
| :--- | :---: | :---: | :---: |
| **Average Latency** | 14.09s | **< 2.0s** | **~7x Faster** |
| **Object Detection** | BLIP (Caption-based) | **YOLO26s (Real-time)** | High Precision |
| **Hand Tracking** | None | **MediaPipe (21 landmarks)** | Spatial Awareness |
| **Guidance Type** | Passive Description | **Active Vector Guidance** | Actionable |
| **Success Rate** | ~40% (Object Finding) | **>85% (Object Finding)** | **Major Gain** |
| **Fall Detection** | None | **Multi-method Algorithm** | Safety Innovation |
| **Guardian Alerts** | None | **Automated Email System** | Complete Solution |
| **Voice Control** | Limited | **Full Handsfree Mode** | Complete Accessibility |

### Key Findings
1.  **Latency is Critical:** The reduction of latency from ~14s to under 2s transformed the system from a "novelty" to a functional "tool." Users can act on the advice immediately, making real-time guidance practical.
2.  **Spatial Awareness:** The addition of hand tracking (MediaPipe with 21 landmark points) was the deciding factor in task success. Knowing *where* the object is relative to the *hand* proved infinitely more valuable than knowing where it is relative to the *frame*. The geometric vector calculation enables precise directional guidance.
3.  **Safety Innovation:** The proprietary fall detection module employs multiple detection methods (static frame analysis, transition pattern detection, risk scoring) and achieved high accuracy in simulated tests, successfully dispatching automated email alerts via the Guardian system within 3 seconds of a detected event. The system includes configurable risk thresholds and cooldown protection.
4.  **Handsfree Operation:** Complete voice control eliminates the need for screen interaction, making the system fully accessible to blind users. The handsfree mode enables mode switching, task input, and all interactions through voice commands.
5.  **Model Upgrade Impact:** Upgrading from YOLOv8s to YOLO26s improved small object detection accuracy and inference speed, critical for finding everyday items like keys, phones, and watches.
