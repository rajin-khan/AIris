# AIris Final App

A modern full-stack application for AIris Unified Assistance Platform, featuring a FastAPI backend and React frontend with Tailwind CSS v4.

## Project Structure

```
AIris-Final-App/
├── backend/          # FastAPI backend
│   ├── api/          # API routes
│   ├── services/     # Business logic services
│   ├── models/       # Pydantic schemas
│   └── main.py       # FastAPI application entry point
└── frontend/         # React + Vite frontend
    ├── src/
    │   ├── components/   # React components
    │   └── services/     # API client
    └── vite.config.ts
```

## Features

### Activity Guide Mode
- Real-time object detection using YOLO
- Hand tracking using MediaPipe
- LLM-powered guidance instructions
- Text-to-speech audio feedback
- Interactive feedback system

### Scene Description Mode
- Continuous scene analysis using BLIP vision model
- Automatic summarization of observations
- Safety alert detection
- Recording and logging system

## Prerequisites

- Python 3.9+
- Node.js 18+
- Camera access
- GROQ_API_KEY environment variable

## Backend Setup

### Using Conda (Recommended)

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a conda environment from the environment file:
```bash
conda env create -f environment.yml
```

3. Activate the conda environment:
```bash
conda activate airis-backend
```

4. Create a `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key_here
YOLO_MODEL_PATH=yolov8s.pt
CONFIG_PATH=config.yaml
```

5. Download YOLO model (if not present):
The model will be downloaded automatically on first run, or you can download it manually.

6. Run the backend:
```bash
# Make sure your conda environment is activated
conda activate airis-backend
python main.py
```

The backend will be available at `http://localhost:8000`

**Note**: Always activate your conda environment before running the backend:
```bash
conda activate airis-backend
```

### Alternative: Using Python venv

If you prefer not to use conda:

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Follow steps 4-6 from the conda setup above.

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. Start the backend server
2. Start the frontend development server
3. Open your browser to `http://localhost:5173`
4. Click "Start Camera" to begin
5. Select a mode (Activity Guide or Scene Description)
6. For Activity Guide: Enter a task and follow the instructions
7. For Scene Description: Click "Start Recording" to begin analysis

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Environment Variables

### Backend
- `GROQ_API_KEY`: Your Groq API key (required)
- `YOLO_MODEL_PATH`: Path to YOLO model file (default: yolov8s.pt)
- `CONFIG_PATH`: Path to config.yaml (default: config.yaml)

### Frontend
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Development

### Backend
- Uses FastAPI with async/await
- Services are modular and testable
- WebSocket support for real-time camera streaming

### Frontend
- React with TypeScript
- Tailwind CSS v4 for styling
- Axios for API calls
- Lucide React for icons

## License

MIT

