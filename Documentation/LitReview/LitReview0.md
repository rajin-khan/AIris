# Literature Review Outline for AIris Thesis Project

## Introduction
The AIris project, a wearable AI system designed to provide real-time scene descriptions for visually impaired users, builds upon advancements in assistive technologies, computer vision, and natural language processing (NLP). This literature review synthesizes key research to contextualize AIris within the field, identify gaps, and highlight its contributions. The review draws on papers from reputable sources, including arXiv, PMC, and journals like Sensors and Journal on Multimodal User Interfaces, focusing on wearable devices, AI applications, and user-centric design.

## 1. Existing Wearable Assistive Technologies
Wearable assistive technologies for visually impaired individuals have evolved significantly, offering solutions for navigation, object recognition, and scene description. Key papers provide insights into current systems:

- **AI-Powered Assistive Technologies for Visual Impairment** ([AI-Powered Assistive Technologies](https://arxiv.org/pdf/2503.15494.pdf)) reviews wearable devices like smart glasses and smartphone applications that use AI to enhance independence. These devices often integrate cameras and audio output, similar to AIris’s spectacle camera and directional speakers.
- **Deep Learning based Wearable Assistive System for Visually Impaired People** ([Deep Learning Wearable System](https://arxiv.org/pdf/1908.03364.pdf)) proposes a system with an RGBD camera and earphone, achieving high accuracy in obstacle avoidance. This aligns with AIris’s goal of sub-2-second response times and offline-first design.
- **Sensor-Based Assistive Devices for Visually-Impaired People: Current Status, Challenges, and Future Directions** ([Sensor-Based Devices](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5375851/pdf/sensors-17-00565.pdf)) surveys portable devices, noting challenges like usability and battery life, which AIris addresses through its portable battery and optimized hardware.

### Table 1: Comparison of Wearable Assistive Devices
| Paper Title | Device Type | Key Features | Challenges |
|-------------|-------------|--------------|------------|
| AI-Powered Assistive Technologies | Smart Glasses, Smartphone Apps | Object recognition, scene description | Cost, accessibility |
| Deep Learning Wearable System | Wearable Terminal with RGBD Camera | Obstacle avoidance, semantic mapping | Computational complexity |
| Sensor-Based Devices | Various Wearables | Navigation, object detection | Usability, battery life |

## 2. Computer Vision and AI in Assistive Technology
Computer vision is central to assistive devices, enabling object recognition, scene analysis, and navigation. Relevant research includes:

- **Enabling Computer Vision Driven Assistive Devices for the Visually Impaired via Micro-architecture Design Exploration** ([Computer Vision Optimization](https://arxiv.org/pdf/1905.07836.pdf)) optimizes object detection networks for on-device operation, critical for AIris’s Raspberry Pi 5 implementation. The paper emphasizes reducing computational and memory requirements, aligning with AIris’s target of <7GB memory usage.
- **Deep Learning based Wearable Assistive System** highlights the use of deep learning models for real-time environment perception, achieving excellent results in indoor and outdoor settings. AIris’s evaluation of models like LLaVA-v1.5 and BLIP-2 draws on similar methodologies.
- **Review of substitutive assistive tools and technologies for people with visual impairments: recent advancements and prospects** ([Journal on Multimodal User Interfaces](https://link.springer.com/article/10.1007/s12193-023-00427-4)) discusses computer vision limitations, such as distinguishing between partial and total blindness, which AIris aims to address through contextual intelligence.

## 3. Natural Language Processing for Scene Description
NLP converts visual data into accessible audio descriptions, a core component of AIris. Key findings include:

- **AI-Powered Assistive Technologies** details NLP-driven text-to-speech systems, like NaturalReader, which provide natural voice synthesis. AIris’s TTS engine aims for similar user-friendly audio delivery.
- **Towards assisting visually impaired individuals: A review on current status and future prospects** ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2590137022001583)) examines algorithms for text-to-speech synthesis, noting the importance of real-time processing, which AIris targets with its <2-second latency goal.
- **Sensor-Based Assistive Devices** highlights user hesitancy due to poor learnability of audio interfaces, suggesting AIris’s focus on private audio delivery via directional speakers could improve adoption.

## 4. Performance and Usability
Performance metrics like response time, accuracy, and user satisfaction are critical for assistive devices. The AIris project sets ambitious targets, informed by existing research:

- **AI-Powered Assistive Technologies** reports high user satisfaction with AI-enabled navigation aids but notes affordability issues. AIris’s offline-first design may reduce costs by minimizing cloud dependency.
- **Deep Learning Wearable System** achieves high accuracy (91.70% with YOLOV8 in similar systems), providing a benchmark for AIris’s >85% object recognition target.
- **Sensor-Based Assistive Devices** identifies battery life (>8 hours) and memory usage as key challenges, which AIris addresses through its portable battery and optimization efforts.

### Table 2: Performance Metrics of Assistive Systems
| Paper Title | Response Time | Accuracy | Battery Life | Memory Usage |
|-------------|---------------|----------|--------------|--------------|
| AI-Powered Assistive Technologies | Not specified | High | Varies | Not specified |
| Deep Learning Wearable System | Real-time | 91.70% | Not specified | High |
| Sensor-Based Devices | Varies | Varies | <8 hours | High |

## 5. Research Gaps and AIris’s Contributions
The reviewed papers identify several gaps that AIris aims to address:

- **Usability and Learnability**: **Review of substitutive assistive tools** notes that many devices lack user-friendly interfaces, particularly for children and those with total blindness. AIris’s simple button-press activation and wearable form factor enhance accessibility.
- **Offline Processing**: **Sensor-Based Assistive Devices** highlights the need for offline capabilities to ensure reliability in varied environments. AIris’s offline-first design with cloud enhancement addresses this.
- **Contextual Intelligence**: **AI-Powered Assistive Technologies** suggests that current systems lack spatial awareness and safety prioritization, which AIris incorporates through its scene analyzer and safety-focused descriptions.
- **Hardware Integration**: **Deep Learning Wearable System** and **Enabling Computer Vision** emphasize the challenge of integrating AI models into compact hardware. AIris’s use of Raspberry Pi 5 and custom hardware design tackles this issue.

## 6. Exploration of Specific Journals
The user requested papers from specific journals, including the “Journal of ECE” (likely Journal of Electrical and Computer Engineering) and the International Journal of Computer Aided Engineering and Technology (IJCAET):

- **Journal of Electrical and Computer Engineering**: The paper **An insight into assistive technology for the visually impaired and blind people: state-of-the-art and future trends** ([ResearchGate](https://www.researchgate.net/publication/312158644_An_insight_into_assistive_technology_for_the_visually_impaired_and_blind_people_state-of-the-art_and_future_trends)) provides a statistical survey of assistive technologies, relevant to AIris’s interdisciplinary approach. However, no PDF was accessible.
- **International Journal of Computer Aided Engineering and Technology**: A search on the journal’s website ([Inderscience](https://www.inderscience.com/jhome.php?jcode=ijcaet)) yielded no directly relevant papers on assistive technology for visually impaired users. The journal focuses on broader computer-aided engineering, suggesting limited overlap with AIris’s scope.
- **Other Reputable Journals**: Papers from Sensors ([Sensor-Based Devices](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5375851/pdf/sensors-17-00565.pdf)) and Journal on Multimodal User Interfaces ([Review of substitutive assistive tools](https://link.springer.com/article/10.1007/s12193-023-00427-4)) were included, as they are highly relevant and from reputable sources.

## Conclusion
The literature review establishes AIris as a promising advancement in assistive technology, building on existing wearable devices, computer vision, and NLP while addressing key gaps in usability, offline processing, and contextual intelligence. The identified papers provide a robust foundation for your thesis, with open-access PDFs available for immediate reference. Future research should focus on user testing and hardware optimization, as AIris moves toward its December 2025 completion goal.
