# Image Generation Prompts for AIris Poster

<div align="center">

**Detailed prompts for generating high-quality, scientific poster visualizations**

*For A0 Landscape (1189mm × 841mm) on white background*

</div>

---

## 🎨 Color Palette Reference

**AIris Brand Colors (Use these exact colors):**
- **Gold (Primary):** #C9AC78
- **Gold Light:** #D4BC8E
- **Gold Dark:** #A89058
- **Charcoal (Text):** #1D1D1D
- **Success Green:** #5A9E6F
- **Success Light:** #6FB583
- **Danger Red:** #C75050
- **Danger Light:** #D46A6A
- **Deep Blue (AI Models):** #4B4E9E
- **Teal (Cloud):** #009688
- **Background:** White (#FFFFFF)

---

## 1. Main System Architecture Diagram

### Prompt:

> Create a professional, scientific system architecture diagram for an AI-powered vision assistant called "AIris". The diagram should be flat vector style, suitable for an academic poster on white background. Show the complete system with clear visual separation between Activity Guide and Scene Description modes.

**Layout Structure:**

**Top Layer - User Interface:**
- **Frontend** box (Gold #C9AC78, charcoal text):
  - **Web Speech API** with STT/TTS icons
  - Label: "Voice I/O" (Georgia font)

**Middle Layer - Backend Processing:**
- **FastAPI Backend** (Gold #C9AC78, border: Charcoal #1D1D1D, 3px, large box) containing:

  **Vision Models (Deep Blue #4B4E9E, white text):**
  - **YOLO26s**: "Object Detection"
  - **MediaPipe**: "Hand Tracking"
  - **BLIP**: "Scene Captioning"

  **Activity Guide Pipeline (Success Green #5A9E6F, charcoal text):**
  - **Object Extraction** → **Vector Calc** → **Depth Est.** → **Rule-Based Guidance** → **Distance Check**

  **Scene Description Pipeline (Danger Red #C75050, white text):**
  - **Frame Buffer** → **Risk Assessment** → **Fall Detection** → **Summarization** → **Risk Scoring**

  **Output Services (Gold #C9AC78, charcoal text):**
  - **Email Service**: "Guardian Alerts"
  - **Audio Service**: "TTS Queue"

**Bottom Layer - Cloud Services:**
- **Groq API** (Teal #009688, white text, dashed border):
  - **GPT OSS120B**: "Object Extraction | Summarization"
  - Label: "Cloud Inference" (Georgia font)

**Key Flow Indicators:**
- Activity Guide: Voice → Extract → Detect → Track → Guide → Audio
- Scene Description: Frames → Caption → Analyze → Summarize → Alert → Audio

**Connections:**
- Solid arrows (charcoal #1D1D1D, 2px) for local flows
- Dashed arrows (charcoal #1D1D1D, 1px) for cloud
- Color-coded: Green (Activity Guide), Red (Scene Description)
- All labels in Georgia font (serif)

**Style:**
- Flat vector design, no 3D effects
- Clean lines, professional appearance
- Clear labels in Georgia font (serif)
- Scientific poster aesthetic
- White background
- All boxes with rounded corners (4-6px radius)
- Grouped by function with clear visual hierarchy

---

## 2. Active Guidance Flowchart

### Prompt:

> Create a clean, horizontal flowchart diagram showing the Active Guidance mode decision loop. Flat vector style on white background, suitable for academic poster.

**Flow Steps (Left to Right):**
1. **Start Node** (Gold #C9AC78, rounded rectangle):
   - Microphone icon
   - Text: "Voice: 'Find Object'" (Georgia font)
   - Border: Charcoal #1D1D1D, 2px

2. **Object Extraction** (Teal #009688, rounded rectangle, dashed border):
   - Brain/AI icon
   - Text: "GPT OSS120B: Extract Target" (Georgia font)
   - White text
   - Note: "Cloud inference"

3. **Object Detection** (Deep Blue #4B4E9E, rounded rectangle):
   - Target/bounding box icon
   - Text: "YOLO26s Detection" (Georgia font)
   - White text

4. **Decision Diamond** (Charcoal outline):
   - Text: "Object Found?" (Georgia font)
   - Two paths: "No" (red arrow back) and "Yes" (green arrow forward) - labels in Georgia font

5. **Hand Tracking** (Deep Blue #4B4E9E, rounded rectangle):
   - Hand skeletal icon
   - Text: "MediaPipe (21 landmarks)" (Georgia font)
   - White text

6. **Decision Diamond** (Charcoal outline):
   - Text: "Hand Visible?" (Georgia font)
   - Two paths: "No" (red arrow back) and "Yes" (green arrow forward) - labels in Georgia font

7. **Spatial Analysis** (Success Green #5A9E6F, rounded rectangle):
   - Vector + depth icon
   - Text: "Vector Calc + Depth Est." (Georgia font)
   - Sub-text: "V = P_obj - P_hand | BBox ratio"
   - Charcoal text

8. **Rule-Based Guidance** (Success Green #5A9E6F, rounded rectangle, bold border):
   - Algorithm icon
   - Text: "Generate Directions (No LLM)" (Georgia font)
   - Charcoal text
   - Note: "Novel algorithm"

9. **Audio Output** (Gold #C9AC78, rounded rectangle):
   - Speaker icon
   - Text: "TTS: 'Move left & forward'" (Georgia font)
   - Charcoal text

10. **Contact Check** (Charcoal, rounded rectangle):
    - Ruler/check icon
    - Text: "Distance & Depth Check" (Georgia font)

11. **Decision Diamond** (Charcoal outline):
    - Text: "Contact?" (Georgia font)
    - Two paths: "No" (loop back to step 7) and "Yes" (forward) - labels in Georgia font

12. **Success Node** (Success Green #5A9E6F, rounded rectangle, bold border 3px):
    - Checkmark icon
    - Text: "Object Found!" (Georgia font)
    - Charcoal text

**Connections:**
- Forward arrows: Success Green #5A9E6F, 2px
- Loop-back arrows: Danger Red #C75050, 2px
- Cloud connection (dashed): Teal #009688, 1px
- All labels in Georgia font

**Style:**
- Flat design, no shadows or gradients
- Consistent spacing between nodes
- Professional, scientific appearance
- White background
- Clear typography in Georgia font (serif)

---

## 3. Scene Description Flowchart

### Prompt:

> Create a clean, horizontal flowchart diagram showing the Scene Description mode continuous monitoring loop. Flat vector style on white background, suitable for academic poster.

**Flow Steps (Left to Right):**
1. **Start Node** (Gold #C9AC78, rounded rectangle):
   - Camera icon
   - Text: "Scene Description Active" (Georgia font)
   - Border: Charcoal #1D1D1D, 2px

2. **Frame Processing** (Deep Blue #4B4E9E, rounded rectangle):
   - Video frame + caption icon
   - Text: "Capture & Caption (BLIP, 2 FPS)" (Georgia font)
   - White text

3. **Multi-Method Analysis** (Charcoal, rounded rectangle):
   - Analysis icon
   - Text: "Risk Assessment: Keywords | Static | Transitions" (Georgia font)
   - Sub-text: "Parallel detection methods"

4. **Frame Buffer** (Charcoal, rounded rectangle):
   - Buffer/stack icon
   - Text: "Buffer (5-10 frames)" (Georgia font)

5. **Decision Diamond** (Charcoal outline):
   - Text: "Buffer Full?" (Georgia font)
   - Two paths: "No" (loop back to step 2) and "Yes" (forward) - labels in Georgia font

6. **LLM Processing** (Teal #009688, rounded rectangle, dashed border):
   - Brain/AI icon
   - Text: "GPT OSS120B: Summarize & Risk Score" (Georgia font)
   - White text
   - Note: "Cloud inference"

7. **Decision Diamond** (Charcoal outline):
   - Text: "Risk > Threshold?" (Georgia font)
   - Two paths: "No" (normal path) and "Yes" (alert path) - labels in Georgia font

8. **Normal Path - Audio Output** (Gold #C9AC78, rounded rectangle):
   - Speaker icon
   - Text: "TTS: Scene Description" (Georgia font)
   - Charcoal text

9. **Alert Path - Fall Alert** (Danger Red #C75050, rounded rectangle, bold border 3px):
   - Warning icon
   - Text: "Fall Alert" (Georgia font)
   - White text

10. **Email Notification** (Gold #C9AC78, rounded rectangle):
    - Email icon
    - Text: "Guardian Email + Cooldown" (Georgia font)
    - Charcoal text

11. **Loop Back** (Success Green #5A9E6F, rounded rectangle):
    - Loop/refresh icon
    - Text: "Continue Monitoring" (Georgia font)
    - Charcoal text
    - Arrow loops back to step 2

**Connections:**
- Main flow arrows: Charcoal #1D1D1D, 2px
- Loop-back arrow: Success Green #5A9E6F, 2px
- Alert path arrow: Danger Red #C75050, 2px
- Cloud connection (dashed): Teal #009688, 1px
- All labels in Georgia font

**Style:**
- Flat design, no shadows or gradients
- Consistent spacing between nodes
- Professional, scientific appearance
- White background
- Clear typography in Georgia font (serif)
- Visual distinction: normal flow (charcoal), alert (red), loop (green)

---

## 4. Latency Comparison Bar Chart

### Prompt:

> Create a flat, scientific bar chart comparing system performance. White background, academic poster style.

**Chart Specifications:**
- **Type:** Horizontal or vertical bar chart (vertical recommended)
- **X-Axis:** "Pipeline Version" with two labels: "Prototype (BLIP+GPT)" and "Final (YOLO26s+GPT OSS120B)" (Georgia font)
- **Y-Axis:** "Response Time (seconds)" from 0 to 16 seconds, with clear tick marks (Georgia font)

**Bars:**
- **Bar 1 - Prototype:**
  - Height: 14.1 seconds
  - Color: Danger Red #C75050
  - Label: "14.1s (BLIP+GPT)" (Georgia font)
  - Border: Charcoal #1D1D1D, 1px

- **Bar 2 - Final System:**
  - Height: 1.8 seconds
  - Color: Success Green #5A9E6F
  - Label: "1.8s (YOLO26s+Groq)" (Georgia font)
  - Border: Charcoal #1D1D1D, 1px

**Annotations:**
- Dashed horizontal line at 2 seconds in Gold #C9AC78
- Label: "Real-time Threshold (2s)" (Georgia font)
- Text annotation: "~7x Faster" in Charcoal #1D1D1D (Georgia font)

**Style:**
- Flat bars, no 3D effects
- Clean grid lines (light gray)
- Professional typography in Georgia font (serif)
- White background
- Scientific data visualization aesthetic

---

## 5. Fall Detection Algorithm Flow

### Prompt:

> Create a vertical flowchart diagram showing the multi-method fall detection system. Flat vector style, scientific poster aesthetic.

**Layout (Top to Bottom):**
1. **Input Node** (Deep Blue #4B4E9E):
   - Video camera icon
   - Text: "Video Frame Input" (Georgia font)
   - White text

2. **BLIP Processing** (Deep Blue #4B4E9E):
   - Image caption icon
   - Text: "BLIP Scene Captioning" (Georgia font)
   - White text

3. **Three Parallel Analysis Paths:**
   - **Path A - Static Frame Analysis** (Charcoal box):
     - Icon: Static image
     - Text: "Static Frame Detection" (Georgia font)
     - Decision: "Static Surface Detected?" (Georgia font)
   
   - **Path B - Transition Detection** (Charcoal box):
     - Icon: Transition arrow
     - Text: "Transition Pattern Analysis" (Georgia font)
     - Decision: "Abrupt Transition?" (Georgia font)
   
   - **Path C - Risk Scoring** (Charcoal box):
     - Icon: Risk meter
     - Text: "Risk Score Calculation" (Georgia font)
     - Decision: "Risk Score > Threshold?" (Georgia font)

4. **Alert Node** (Danger Red #C75050, bold border 3px):
   - Warning icon
   - Text: "Fall Alert Triggered" (Georgia font)
   - White text

5. **LLM Summarization** (Teal #009688):
   - Brain/AI icon
   - Text: "GPT OSS120B: Generate Summary & Risk Score" (Georgia font)
   - White text

6. **Email Service** (Gold #C9AC78):
   - Email icon
   - Text: "Guardian Email Alert (Automated)" (Georgia font)
   - Charcoal text

7. **Cooldown Timer** (Charcoal):
   - Clock icon
   - Text: "Cooldown Timer (Prevent Spam)" (Georgia font)

**Connections:**
- All three paths converge to LLM Summarization
- LLM Summarization connects to Alert Node
- Alert Node connects to Email Service
- Solid arrows in Charcoal #1D1D1D
- Decision diamonds with Yes/No paths
- Cloud connection (dashed) for LLM Summarization

**Style:**
- Flat design
- Clear hierarchy
- Professional appearance
- White background
- Typography in Georgia font (serif)

---

## 6. System Modes Comparison Diagram

### Prompt:

> Create a side-by-side comparison diagram showing the two operational modes. Flat, scientific style on white background.

**Layout:**
Two vertical columns, side by side:

**Left Column - Active Guidance Mode:**
1. **YOLO26s** (Deep Blue #4B4E9E): "Object Detection" (Georgia font)
2. **MediaPipe** (Deep Blue #4B4E9E): "Hand Tracking" (Georgia font)
3. **Vector Calculation** (Success Green #5A9E6F): "Geometric Vector: V = P_obj - P_hand" (Georgia font)
4. **Depth Estimation** (Success Green #5A9E6F): "Bounding Box Size Ratio" (Georgia font)
5. **Rule-Based Algorithm** (Success Green #5A9E6F): "Novel Guidance Generation (No LLM)" (Georgia font)
6. **Audio Guidance** (Gold #C9AC78): "Directional Instructions" (Georgia font)

**Right Column - Scene Description Mode:**
1. **BLIP** (Deep Blue #4B4E9E): "Scene Captioning (2 FPS)" (Georgia font)
2. **Quick Risk Assessment** (Charcoal): "Keyword-based Analysis" (Georgia font)
3. **Static Frame Detection** (Charcoal): "Fall Indicator Detection" (Georgia font)
4. **Transition Detection** (Charcoal): "Abrupt Change Analysis" (Georgia font)
5. **Buffer Accumulation** (Charcoal): "Frame Buffer (5-10 frames)" (Georgia font)
6. **GPT OSS120B** (Teal #009688): "Summarization & Risk Scoring" (Georgia font)
7. **Fall Detection** (Danger Red #C75050): "Multi-method Safety Analysis" (Georgia font)
8. **Guardian Alerts** (Gold #C9AC78): "Email Notifications" (Georgia font)

**Connections:**
- Vertical flow within each column
- Downward arrows between steps
- Clear separation between columns

**Style:**
- Flat boxes with rounded corners
- Consistent spacing
- Professional typography in Georgia font (serif)
- White background

---

## 7. Technology Stack Visualization

### Prompt:

> Create a layered technology stack diagram showing the complete software architecture. Flat, scientific style.

**Layers (Bottom to Top):**
1. **Hardware Layer** (Charcoal):
   - Icons: Camera, Microphone, Computer
   - Text: "User Device (Computer/Phone) + Optional ESP32-CAM + Bluetooth Headset" (Georgia font)

2. **Backend Layer** (Gold #C9AC78):
   - FastAPI logo/icon
   - Text: "FastAPI Backend (Python 3.10+)" (Georgia font)

3. **AI Models Layer** (Deep Blue #4B4E9E):
   - Multiple boxes:
     - "YOLO26s (Object Detection)" (Georgia font)
     - "MediaPipe (Hand Tracking - 21 landmarks)" (Georgia font)
     - "BLIP (Scene Captioning)" (Georgia font)

4. **Activity Guide Logic Layer** (Success Green #5A9E6F):
   - "Object Extraction (GPT OSS120B)" (Georgia font)
   - "Vector Calculation Algorithm" (Georgia font)
   - "Depth Estimation Algorithm" (Georgia font)
   - "Rule-Based Guidance Algorithm (Novel, No LLM)" (Georgia font)
   - "Distance Check Logic" (Georgia font)

5. **Scene Description Logic Layer** (Danger Red #C75050):
   - "Quick Risk Assessment (Keyword-based)" (Georgia font)
   - "Static Frame Detection" (Georgia font)
   - "Transition Detection" (Georgia font)
   - "Buffer Management" (Georgia font)
   - "Fall Detection Algorithm" (Georgia font)
   - "Risk Scoring System" (Georgia font)

6. **Cloud Layer** (Teal #009688):
   - "Groq API" (Georgia font)
   - "GPT OSS120B (Object Extraction - Activity Guide)" (Georgia font)
   - "GPT OSS120B (Summarization - Scene Description)" (Georgia font)

7. **Output Layer** (Gold #C9AC78):
   - "Web Speech API (TTS)" (Georgia font)
   - "Email Service (Guardian Alerts)" (Georgia font)
   - "Audio Output" (Georgia font)

**Style:**
- Stacked layers with clear separation
- Flat design
- Color-coded by function
- White background
- Typography in Georgia font (serif)

---

## 8. Performance Metrics Visualization

### Prompt:

> Create a clean metrics dashboard showing key performance indicators. Flat, scientific style.

**Metrics Display:**
- **Latency:** "1.8s" (Success Green #5A9E6F, large number, Georgia font)
- **Object Detection Accuracy:** ">85%" (Success Green #5A9E6F, Georgia font)
- **Success Rate:** ">85%" (Success Green #5A9E6F, Georgia font)
- **Fall Detection:** "High Accuracy" (Danger Red #C75050, Georgia font)
- **Response Time:** "<2s" (Success Green #5A9E6F, Georgia font)

**Layout:**
- Grid of metric cards
- Each card: Icon + Large number + Label
- Consistent spacing
- Flat design
- All text in Georgia font (serif)

**Style:**
- Clean, minimal
- Professional typography in Georgia font (serif)
- White background
- Color-coded by metric type

---

## 9. AIris Strengths Octagonal Radar Chart

### Prompt:

> Create a professional octagonal radar/spider chart showing AIris system strengths and capabilities. Flat vector style, scientific poster aesthetic on white background.

**Chart Specifications:**
- **Type:** Octagonal radar chart (8 axes)
- **Shape:** Regular octagon with 8 axes extending from center
- **Center Point:** System name "AIris" in Gold #C9AC78 (Georgia font, bold)
- **Axes:** 8 evenly spaced axes (45° apart) labeled with strength categories

**Eight Strength Axes (Clockwise from top):**
1. **Real-Time Performance** (Top axis):
   - Label: "Real-Time" (Georgia font)
   - Value: 95% (near maximum)
   - Sub-text: "<2s latency"
   - Color: Success Green #5A9E6F

2. **Accuracy** (Top-right axis):
   - Label: "Accuracy" (Georgia font)
   - Value: 90% (high)
   - Sub-text: ">85% success"
   - Color: Success Green #5A9E6F

3. **Privacy** (Right axis):
   - Label: "Privacy" (Georgia font)
   - Value: 100% (maximum)
   - Sub-text: "Local-first"
   - Color: Deep Blue #4B4E9E

4. **Accessibility** (Bottom-right axis):
   - Label: "Accessibility" (Georgia font)
   - Value: 100% (maximum)
   - Sub-text: "Handsfree"
   - Color: Gold #C9AC78

5. **Safety Features** (Bottom axis):
   - Label: "Safety" (Georgia font)
   - Value: 95% (near maximum)
   - Sub-text: "Fall detection"
   - Color: Danger Red #C75050

6. **Innovation** (Bottom-left axis):
   - Label: "Innovation" (Georgia font)
   - Value: 100% (maximum)
   - Sub-text: "Novel algorithm"
   - Color: Teal #009688

7. **Cost-Effectiveness** (Left axis):
   - Label: "Cost-Effective" (Georgia font)
   - Value: 90% (high)
   - Sub-text: "Web Speech API"
   - Color: Success Green #5A9E6F

8. **Reliability** (Top-left axis):
   - Label: "Reliability" (Georgia font)
   - Value: 95% (near maximum)
   - Sub-text: "7x faster"
   - Color: Success Green #5A9E6F

**Visual Elements:**
- **Octagonal Grid:** Light gray concentric octagons (5 levels: 0%, 25%, 50%, 75%, 100%)
- **Data Polygon:** Filled area connecting all 8 data points
  - Fill color: Gold #C9AC78 with 30% opacity
  - Border: Gold #C9AC78, 2px solid
- **Data Points:** Small circles at each axis endpoint
  - Color: Gold #C9AC78
  - Size: 6px diameter
- **Axis Lines:** Charcoal #1D1D1D, 1px solid
- **Labels:** Each axis labeled at outer edge (Georgia font, 12-14pt)
- **Value Indicators:** Small text near each point showing percentage (Georgia font, 10pt)

**Center Design:**
- **Central Circle:** Gold #C9AC78 background, Charcoal #1D1D1D border (2px)
- **Text:** "AIris" in Charcoal #1D1D1D (Georgia font, 18pt, bold)
- **Subtitle:** "System Strengths" in Charcoal #1D1D1D (Georgia font, 10pt)

**Style:**
- Flat design, no 3D effects
- Clean, scientific appearance
- Professional typography in Georgia font (serif)
- White background
- Color-coded axes by category type
- Clear visual hierarchy

**Layout:**
- Octagon centered on canvas
- Sufficient margin space for labels
- Grid lines subtle but visible
- Data polygon clearly visible with transparency

---

## 10. Data Flow Diagram

### Prompt:

> Create a comprehensive data flow diagram showing how information moves through the system. Flat vector style.

**Flow:**
1. **Input:** Video frames + Voice input (Web Speech API STT)
2. **Vision Processing:** Parallel inference (YOLO26s, MediaPipe, BLIP)
3. **Activity Guide Path:** Object extraction (GPT OSS120B) → Vector calculation → Depth estimation → Rule-based guidance (novel algorithm, no LLM) → Audio output
4. **Scene Description Path:** Frame captioning → Risk assessment → Buffer accumulation → Summarization (GPT OSS120B) → Fall detection
5. **Cloud Processing:** LLM via Groq API (GPT OSS120B) for object extraction and summarization only
6. **Output:** Audio feedback (Web Speech API TTS) + Email alerts (Guardian system)

**Visual Elements:**
- Data packets/icons flowing through system
- Clear labels for each stage (Georgia font)
- Color-coded by function
- Arrows showing direction

**Style:**
- Flat design
- Scientific appearance
- White background
- Clear typography in Georgia font (serif)

---

## 🎨 General Style Guidelines for All Visualizations

### Design Principles:
1. **Flat Design:** No shadows, gradients, or 3D effects
2. **Scientific Aesthetic:** Professional, academic poster style
3. **Color Consistency:** Use exact AIris brand colors
4. **Typography:** Georgia font (serif), clear, readable (24-32pt for text, 48-60pt for headings)
5. **White Background:** All visuals on white (#FFFFFF)
6. **Clean Lines:** Sharp, precise edges
7. **Consistent Spacing:** Professional layout with proper margins

### Color Usage:
- **Gold (#C9AC78):** Primary features, main components
- **Deep Blue (#4B4E9E):** AI models and vision processing
- **Success Green (#5A9E6F):** Positive metrics, guidance logic
- **Danger Red (#C75050):** Safety features, alerts
- **Teal (#009688):** Cloud services, LLM
- **Charcoal (#1D1D1D):** Text, borders, structure

### Technical Specifications:
- **Format:** Vector (SVG preferred) or high-resolution raster (300 DPI minimum)
- **Dimensions:** Scalable to A0 size (1189mm × 841mm landscape)
- **Text:** Must be readable at poster size (minimum 24pt equivalent)
- **Icons:** Flat, minimal, professional style

---

## 📝 Notes for Image Generation

1. **Text Overlay:** If generated text is unclear, use the image as base and overlay real text in design software (Figma, Canva, PowerPoint)

2. **Flat Vector Style:** Request "flat vector style" or "infographic style" to avoid photorealistic rendering

3. **Scientific Poster:** Emphasize "academic poster style" or "scientific visualization" for appropriate aesthetic

4. **Color Accuracy:** Specify exact hex codes to ensure brand color consistency

5. **White Background:** Always specify white background (#FFFFFF) for A0 poster printing

6. **Resolution:** Request high resolution (300 DPI minimum) for A0 printing quality

---

<div align="center">

**Detailed prompts for creating professional, scientific poster visualizations**

*All visuals optimized for A0 landscape white background*

</div>
