# AIris Project Development Plan (1-Month Sprint) - Revised

## Overall Goal for the Month:

To evolve the AIris prototype from a simple frame-by-frame descriptor into a **Context-Aware Spatial Description (CAS-D)** system. This involves formalizing our current MVP, then iteratively implementing a novel framework inspired by cutting-edge research (MC-ViT, Video-3D LLM) to manage contextual memory and generate coherent, narrative descriptions.

---

### **Week 1: Formalize the Current Prototype & Project Structure**

**Objective:** To take our existing `app.py` prototype, formalize it into a professional project structure, and establish the theoretical groundwork for the advanced features to come. This week is about solidifying our starting point.

*   **Showcasing Existing Work:**
    *   **a. Refactor the Prototype:** Move the logic from the single `app.py` file into a clean, new project structure. This demonstrates an understanding of software engineering best practices.
        ```
        airis_prototype_v1/
        ├── app.py                 # The Gradio UI and endpoint
        ├── pipeline.py            # Core logic for video processing & BLIP model inference
        ├── requirements.txt
        └── sample_videos/
        ```
    *   **b. Create a Polished README.md:** Write a comprehensive README for the *current* prototype, detailing its features, how to set it up (environment setup), and how to run it with sample videos. This is our "Week 1 deliverable" to showcase.

*   **Theoretical Work (Laying the Groundwork for Future Weeks):**
    *   **a. In-depth Paper Analysis:** Deconstruct the core mechanisms of **MC-ViT** (non-parametric memory) and **Video-3D LLM** (position-aware representations). Diagram their data flows.
    *   **b. Problem Formalization:** Write a clear problem statement that explains the limitations of our current prototype (e.g., "it lacks memory and 3D context") and justifies why the more advanced CAS-D system is necessary for a truly helpful assistive device.
    *   **c. Initial Architecture Sketch:** Draw a rough, first-pass diagram of the *final* CAS-D framework we aim to build in the coming weeks.

*   **Deliverable for Week 1:**
    *   **Code:** A clean, professional repository containing the current, functional prototype, complete with a `README.md` that allows anyone to run it.
    *   **Theory:** A document with diagrams and the finalized problem statement, setting the stage for the work ahead.

---

### **Week 2: The Core AIris Engine: Position-Aware Encoder, Memory, and LLM**

**Objective:** To implement the core intelligence of the new system in a single, self-contained module. This is an intensive week focused on building the most complex part of the MVP.

*   **Theoretical Work:**
    1.  **Formal Architecture Design:** Turn the Week 1 sketch into a formal architectural diagram of the `AIrisModel`, detailing all its internal components, inputs, outputs, and tensor shapes.
    2.  **Agent Strategy Justification:** Write a paragraph justifying why k-means is a good starting point for the memory agent, explaining how centroids of position-aware tokens can represent persistent objects.

*   **Coding Work (MVP Focus: The All-in-One Model):**
    1.  **Create the Core Model File:** In a new `airis_casd/` project folder, create `src/model.py`.
    2.  **Implement the `PositionAwareEncoder`:**
        *   Instantiate a pre-trained Vision Transformer (e.g., ViT-Base from `timm`).
        *   Write the helper functions for 3D back-projection (using dummy camera data for now) and sinusoidal position encoding.
    3.  **Implement the `MemoryAgent`:**
        *   In `src/agent.py`, create the `MemoryAgent` class with a `consolidate` method that uses a k-means algorithm to find centroids from input embeddings.
    4.  **Build the `AIrisModel` Class in `src/model.py`:** This class will contain everything.
        *   In its `__init__`, instantiate your `PositionAwareEncoder` and `MemoryAgent`.
        *   Add a persistent buffer for the `memory_bank`.
        *   Choose a decoder-only LLM (e.g., GPT-2 for local testing, or wire up an API call to **Groq** or a local **Ollama** model).
        *   Implement the main `forward` pass that takes a batch of `e_vis` embeddings, uses the agent to update memory, and then feeds both the current embeddings and the memory bank to the LLM decoder using cross-attention.

*   **Deliverable for Week 2:**
    *   **Code:** A functional `AIrisModel` class. You should be able to instantiate this class, pass it a *dummy tensor* of the correct shape, and get back language logits from the decoder without errors. This proves the entire internal mechanism works.

---

### **Week 3: Advanced Data Pipeline & Integration Testing**

**Objective:** To build the data pipeline capable of feeding real-world 3D data into the advanced model created in Week 2, and test the two components together.

*   **Theoretical Work:**
    1.  **Refine Mathematical Formalism:** Write down the exact, final equations for the 3D back-projection and position encoding, as implemented in code.
    2.  **Evaluation Design:** Design a specific, novel evaluation task for the framework. Create 5-10 example Question/Answer pairs that are impossible to answer without the long-term context that the memory agent provides.

*   **Coding Work (MVP Focus: Data Input):**
    1.  **Download and Prepare Dataset:** Download a suitable subset of the **ScanNet** dataset.
    2.  **Implement the `ScanNetDataset` Class:** In `src/dataset.py`, create a PyTorch `Dataset` that:
        *   Loads a video sequence from ScanNet.
        *   Retrieves the RGB image, depth map, and camera parameters for each frame.
        *   Uses the "Maximum Coverage Sampling" technique to select a fixed number of frames.
    3.  **Create a `DataLoader`:** Wrap your `ScanNetDataset` in a PyTorch `DataLoader`.
    4.  **Integration Test:** Write a simple script that:
        *   Initializes your `AIrisModel` from Week 2.
        *   Initializes your `DataLoader` from this week.
        *   Runs a single batch of real data from the `DataLoader` through the `AIrisModel` to ensure there are no shape mismatches or errors.

*   **Deliverable for Week 3:**
    *   **Code:** A functional data pipeline that successfully loads real 3D data and feeds it into your advanced model without crashing. This is the final integration step before training.
    *   **Theory:** A document detailing the novel, context-dependent evaluation protocol.

---

### **Week 4: End-to-End Training & Final Proposal**

**Objective:** To connect all components, run a proof-of-concept training loop to prove the entire architecture is viable and can learn, and synthesize all work into a final project proposal or paper draft.

*   **Theoretical Work:**
    1.  **Write the Full Proposal/Paper Draft:**
        *   Write the **Introduction**, **Related Work**, and **Methodology** sections using the materials from previous weeks.
        *   Write the **Experiments** section, detailing the ScanNet dataset, the MVP implementation, and the evaluation strategy.

*   **Coding Work (MVP Focus: End-to-End Run):**
    1.  **Implement the Training Loop:** In `src/train.py`:
        *   Write a full training loop that iterates through your `DataLoader`.
        *   In the loop, pass the data through your `AIrisModel`.
        *   Compute the standard cross-entropy loss between the model's predictions and ground-truth text descriptions (from the dataset).
        *   Implement `loss.backward()` and `optimizer.step()`.
    2.  **Proof-of-Concept Run:**
        *   Run your `train.py` script on a very small subset of the data (e.g., 1-2 videos, batch size of 1) for a few dozen steps.
        *   **Goal:** Verify that the code runs end-to-end and that the **training loss decreases**. This is the ultimate proof that the entire architecture is viable and capable of learning.
    3.  **Code Finalization:** Clean up the code, add comments, docstrings, and update the `README.md` to explain how to set up the full environment and run the proof-of-concept.

*   **Deliverable for Week 4:**
    *   **Theory:** A polished, near-complete research proposal or paper draft.
    *   **Code:** A functional, end-to-end MVP codebase. A successful demonstration showing the training loss going down on a toy example.