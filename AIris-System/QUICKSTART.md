# Quick Start Guide

## Step 1: Backend Setup

### 1.1 Create .env file

Navigate to the backend directory and create a `.env` file:

```bash
cd backend
```

Create the `.env` file with your configuration:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (defaults shown)
YOLO_MODEL_PATH=yolov8s.pt
CONFIG_PATH=config.yaml
```

**Note**: The `config.yaml` file is already in place, so you don't need to create it.

### 1.2 Activate conda environment and start backend

```bash
# Make sure you're in the backend directory
cd backend

# Activate the conda environment
conda activate airis-backend

# Start the backend server
python main.py
```

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
Initializing AIris backend...
Loading models...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

The backend is now running at `http://localhost:8000`

**Keep this terminal window open!**

## Step 2: Frontend Setup

Open a **new terminal window** (keep the backend running):

### 2.1 Navigate to frontend and install dependencies

```bash
cd AIris-Final-App/frontend
npm install
```

### 2.2 Create frontend .env file (optional)

The frontend will default to `http://localhost:8000`, but you can create a `.env` file if needed:

```bash
# Create .env file (optional - defaults shown)
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

### 2.3 Start the frontend development server

```bash
npm run dev
```

You should see output like:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

The frontend is now running at `http://localhost:5173`

## Step 3: Use the Application

1. Open your browser and go to: `http://localhost:5173`
2. Click the **"Start Camera"** button (camera icon in the header)
3. Grant camera permissions when prompted
4. Select a mode:
   - **Activity Guide**: Enter a task like "find my watch" and follow instructions
   - **Scene Description**: Click "Start Recording" to begin scene analysis

## Troubleshooting

### Backend won't start
- Make sure conda environment is activated: `conda activate airis-backend`
- Check that `.env` file exists and has `GROQ_API_KEY` set
- Verify Python version: `python --version` (should be 3.10)

### Frontend can't connect to backend
- Make sure backend is running on port 8000
- Check that `VITE_API_BASE_URL` in frontend `.env` matches backend URL
- Check browser console for errors

### Camera not working
- Grant camera permissions in browser/system settings
- Check that no other app is using the camera
- Try refreshing the page

### Models not loading
- First run will download YOLO model automatically (may take a few minutes)
- Check internet connection
- Models are cached, so subsequent runs will be faster

## What's Running

- **Backend**: FastAPI server on `http://localhost:8000`
- **Frontend**: Vite dev server on `http://localhost:5173`
- **API Docs**: Visit `http://localhost:8000/docs` for interactive API documentation

## Next Steps

- The YOLO model will download automatically on first run
- All ML models (YOLO, MediaPipe, BLIP) will be loaded when needed
- Check the terminal for any error messages
- Use the API docs at `/docs` to test endpoints directly

