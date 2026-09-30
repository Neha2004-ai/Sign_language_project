# Deployment Guide

## 1. Local Development (Windows / Linux / macOS)

### Prerequisites
- Python 3.10+
- Node.js 18+

### Step-by-Step
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

---

## 2. Docker Deployment

```bash
docker-compose up --build -d
```
- Frontend UI: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`
