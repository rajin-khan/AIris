# Quick Start Guide

Get AIris running in 5 minutes.

---

## Step 1: Backend Setup

### 1.1 Navigate to backend
```bash
cd AIris-System/backend
```

### 1.2 Create Python environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 1.3 Install dependencies
```bash
pip install -r requirements.txt
```

### 1.4 Create .env file
```bash
# Create the file with your Groq API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Optional: Add email configuration for guardian alerts
# echo "EMAIL_SENDER=your_email@gmail.com" >> .env
# echo "EMAIL_PASSWORD=your_app_password" >> .env
# echo "EMAIL_RECIPIENT=guardian@example.com" >> .env
```

> Get a free API key at [console.groq.com](https://console.groq.com/keys)

### 1.5 Start the backend
```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

---

## Step 2: Frontend Setup

Open a **new terminal** (keep backend running).

### 2.1 Navigate to frontend
```bash
cd AIris-System/frontend
```

### 2.2 Install dependencies
```bash
npm install
```

### 2.3 Start dev server
```bash
npm run dev
```

You should see:
```
VITE ready in xxx ms
➜  Local:   http://localhost:5173/
```

---

## Step 3: Use the App

1. Open `http://localhost:5173` in your browser
2. Click **"Start Camera"** (camera icon in header)
3. Grant camera permissions when prompted
4. Choose a mode:

### Activity Guide Mode
- Enter an object to find (e.g., "water bottle", "my phone")
- Follow the audio instructions to locate and reach the object
- The system tracks your hand and guides you to the target
- **Handsfree**: Enable Voice-Only Mode and say "input task" to enter via voice

### Scene Description Mode  
- Click **"Start Recording"**
- The system continuously analyzes and describes your environment
- Safety alerts are prioritized
- **Fall Detection**: Automatically detects falls and sends guardian alerts
- **Handsfree**: Enable Voice-Only Mode and say "start recording" to begin

### Handsfree Mode (Voice-Only)
- Click the **microphone icon** in the header to enable
- All instructions are automatically spoken
- Use voice commands:
  - "Switch to activity guide" / "Switch to scene description"
  - "Turn on camera" / "Turn off camera"
  - "Input task" (dictate task name)
  - "Start task" (begin the task)
  - "Yes" / "No" (for feedback)
- Perfect for blind users — no screen needed!

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Make sure `.env` file exists with `GROQ_API_KEY`
- Activate virtual environment: `source venv/bin/activate`

### Frontend can't connect
- Verify backend is running on port 8000
- Check browser console for errors
- Try refreshing the page

### Camera not working
- Grant camera permissions in browser settings
- Close other apps using the camera
- Try a different browser (Chrome recommended)

### Models loading slowly
- First run downloads YOLO model (~25MB) — be patient
- Subsequent runs use cached models

---

## What's Running

| Service | URL | Purpose |
|:--------|:----|:--------|
| Backend | `http://localhost:8000` | FastAPI server |
| API Docs | `http://localhost:8000/docs` | Interactive API documentation |
| Frontend | `http://localhost:5173` | React development interface |

---

## Next Steps

- Test both modes with your laptop camera
- Check the API docs at `/docs` to understand available endpoints
- See the main [README.md](./README.md) for architecture details

---

## Hardware Note

**Recommended Setup:** We've designed a **custom ESP32-CAM with protective casing** (see `Hardware/cam-casing/airis-case.stl`) for the best handsfree experience. This provides wireless camera positioning and professional appearance.

**Default Setup:** The system works perfectly with your computer's built-in webcam and speakers/microphone. No external hardware is required — we've made this the default option for maximum accessibility and ease of use.

**Optional Accessories:**
- **Custom ESP32-CAM with casing** ⭐ — Recommended for handsfree camera positioning
- **Bluetooth Microphone** — Optional for wireless voice input
- **Bluetooth Headphone** — Optional for wireless audio output

Enable **Voice-Only Mode** for full handsfree operation using voice commands — works with any camera setup!
