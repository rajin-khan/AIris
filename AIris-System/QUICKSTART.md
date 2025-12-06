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

### Scene Description Mode  
- Click **"Start Recording"**
- The system continuously analyzes and describes your environment
- Safety alerts are prioritized

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

This setup uses your laptop's camera and speakers for testing. The production device will use:
- **ESP32-CAM** for wireless video (WiFi)
- **Arduino** for wireless audio (Bluetooth)

Hardware integration is currently in progress.
