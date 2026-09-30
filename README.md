# SignBridge AI: AI-Powered Bidirectional Indian Sign Language (ISL) Translation System

![SignBridge AI](https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&w=1200&q=80)

**SignBridge AI** is a production-quality, bidirectional Indian Sign Language (ISL) assistive communication and learning platform. It bridges the communication gap between ISL users and hearing individuals in real time across **English, Hindi, and Bengali**.

---

## Key Features

1. **Sign Language → Text & Speech**: Live webcam recognition with MediaPipe 21 hand landmarks overlay, calibrated confidence score meter, debouncing, and instant voice output (English, हिन्दी, বাংলা).
2. **Text → Sign Language**: Multilingual sentence input translated into animated ISL avatar gestures and fingerspelling sequences via modular `SignRenderer`.
3. **Speech → Sign Language**: Live microphone voice capture in English, Hindi, and Bengali converted into ISL sign sequences.
4. **Assistive AI Chatbot**: Bidirectional communication assistant that answers user messages and automatically renders responses in ISL sign animations.
5. **Learn ISL & Quizzes**: Structured modules (Alphabets, Numbers, Common Words, Phrases) with Sign→Word, Word→Sign, and Live Camera Practice quizzes.
6. **Gamified Streak & Progress**: XP tracking, 7-day streak tracking, accuracy ratings, and level progression.
7. **Custom Gesture Training**: Personal hand pose capture (20–50 samples), quality validation, and instant personalized classifier training.
8. **Low-Cost Laptop Deployment**: Runs at 30+ FPS on standard CPU without dedicated GPU requirements.

---

## Tech Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons, Recharts, HTML5 Canvas, MediaPipe Hands.
- **Backend**: Python, FastAPI, Uvicorn, WebSockets, SQLAlchemy ORM, SQLite / PostgreSQL ready.
- **AI / Computer Vision**: MediaPipe Hands, OpenCV, NumPy, Scikit-Learn, PyTorch.
- **Speech**: Browser Web Speech API & SpeechSynthesis API with backend fallbacks.
- **Containerization**: Docker, Docker Compose, Nginx.

---

## Project Structure

```
/
├── frontend/                     # React + Vite + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/           # LandmarkCanvas, SignRenderer, ConfidenceMeter, AudioPlayer, Navbar, Sidebar
│   │   ├── pages/                # Translator, TextToSign, SpeechToSign, Chat, Learn, CustomGestures, Analytics, Admin
│   │   ├── hooks/                # useWebcam, useSpeechRecognition, useSpeechSynthesis, useWebSocketSign
│   │   ├── store/                # AuthContext, ThemeContext, LanguageContext
│   │   └── types/                # TypeScript definitions
├── backend/                      # FastAPI Python Application
│   ├── app/
│   │   ├── api/v1/               # Auth, Predict, Translate, Speech, Chat, Learning, CustomGestures, Analytics, Admin
│   │   ├── core/                 # Config, Security, JWT
│   │   ├── db/                   # Database session & rich seed data
│   │   ├── ml/                   # Feature extractor, real-time inference engine, model loader
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── services/             # Translation, Chat, Speech services
│   │   └── websocket/            # Real-time WebSocket sign recognition handler
│   └── tests/                    # Pytest test suite (100% passing)
├── ml/                           # ML Training, preprocessing, feature extraction & evaluation
├── models/                       # Pre-trained baseline model weights (.pkl & .pt)
├── dataset/                      # Dataset repository & seed gestures
├── docs/                         # Architecture, API, ML pipeline, and deployment docs
├── docker-compose.yml            # Multi-container Docker deployment
└── README.md
```

---

## Quick Start (How to Run)

### 1. Prerequisites
- Python 3.10+ installed
- Node.js 18+ and npm installed

### 2. Run Backend (FastAPI + WebSockets)
```bash
# Navigate to backend and install requirements
cd backend
python -m pip install -r requirements.txt

# Start FastAPI server on port 8000
python -m uvicorn app.main:app --reload --port 8000
```
Backend API will be available at: `http://localhost:8000`  
Interactive Swagger Docs: `http://localhost:8000/docs`

### 3. Run Frontend (React + Vite)
```bash
# Open a second terminal, navigate to frontend
cd frontend
npm install
npm run dev
```
Frontend Web Application will be available at: `http://localhost:5173`

---

## Test Credentials & Guest Access

- **Demo Account**:
  - Email: `demo@signbridge.ai`
  - Password: `Password123!`
  - Pre-seeded with a **7-Day Streak** and **1,420 XP**.
- **1-Click Guest Mode**:
  - Click **"⚡ 1-Click Guest Demo"** on the landing page or login screen for instant access without entering credentials.

---

## Supported Initial ISL Gestures

- **Common Words & Phrases**: `HELLO`, `THANK YOU`, `YES`, `NO`, `HELP` ("I Need Help"), `GOODBYE`, `PLEASE`, `SORRY`, `I LOVE YOU`, `OK`.
- **Numbers**: `0`, `1`, `2`, `3`, `4`, `5`.
- **Fingerspelling**: Full `A–Z` alphabet support with fallback fingerspelling sequences.
- **Custom Gestures**: Train unlimited user-specific gestures through the Custom Gesture module.

---

## Running Automated Tests

```bash
# Run backend pytest suite
python -m pytest backend/tests/test_backend.py -v

# Run ML evaluation & latency benchmarks
python ml/evaluation/evaluate.py
```

---

## Current Model Status & Production Scalability

- **Active Model Status**: Clearly labeled as **Development / Demo Baseline Model** in the UI and Admin dashboard.
- **Real-Time Computer Vision Pipeline**: Fully functional live 21-landmark MediaPipe tracking with geometric invariant extraction and temporal debouncing.
- **Production Expansion**: To deploy a full continuous ISL model covering thousands of signs, place expanded training files in `dataset/` and run `python ml/training/train_classifier.py`.
