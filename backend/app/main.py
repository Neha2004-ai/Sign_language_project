import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.db.seed_data import seed_database

# Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.gestures import router as gestures_router
from app.api.v1.predict import router as predict_router
from app.api.v1.translate import router as translate_router
from app.api.v1.speech import router as speech_router
from app.api.v1.chat import router as chat_router
from app.api.v1.learning import router as learning_router
from app.api.v1.custom_gestures import router as custom_gestures_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.admin import router as admin_router
from app.websocket.ws_sign_recognition import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables & seed initial data
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Bidirectional Indian Sign Language (ISL) Translation System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(gestures_router, prefix=f"{settings.API_V1_STR}/gestures", tags=["Gestures"])
app.include_router(predict_router, prefix=f"{settings.API_V1_STR}/predict", tags=["Prediction & Inference"])
app.include_router(translate_router, prefix=f"{settings.API_V1_STR}/translate", tags=["Translation"])
app.include_router(speech_router, prefix=f"{settings.API_V1_STR}/speech", tags=["Speech Processing"])
app.include_router(chat_router, prefix=f"{settings.API_V1_STR}/chat", tags=["Assistive Chatbot"])
app.include_router(learning_router, prefix=f"{settings.API_V1_STR}/learning", tags=["Learning & Quizzes"])
app.include_router(custom_gestures_router, prefix=f"{settings.API_V1_STR}/custom-gestures", tags=["Custom Gestures"])
app.include_router(analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics & History"])
app.include_router(admin_router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin & Model Management"])

# WebSocket router
app.include_router(ws_router, tags=["WebSocket Real-Time Recognition"])

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
        "websocket_endpoint": "/ws/sign-recognition"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
