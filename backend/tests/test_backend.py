import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine, Base, SessionLocal
from app.db.seed_data import seed_database
from app.ml.feature_extractor import LandmarkFeatureExtractor
from app.ml.inference import inference_engine
from app.services.translation_service import translation_service

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "SignBridge AI" in data["name"]

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

def test_guest_auth():
    with TestClient(app) as client:
        response = client.post("/api/auth/guest")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["is_guest"] is True

def test_get_gestures():
    with TestClient(app) as client:
        response = client.get("/api/gestures")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        gesture_names = [g["name"] for g in data]
        assert "HELLO" in gesture_names
        assert "YES" in gesture_names

def test_predict_landmarks():
    with TestClient(app) as client:
        dummy_landmarks = [{"x": 0.5 + i*0.01, "y": 0.5 - i*0.02, "z": 0.0} for i in range(21)]
        payload = {
            "landmarks": dummy_landmarks,
            "handedness": "Right"
        }
        response = client.post("/api/predict/landmarks", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "gesture" in data
        assert "confidence" in data
        assert "text_en" in data
        assert "text_hi" in data
        assert "text_bn" in data

def test_multilingual_translation():
    with TestClient(app) as client:
        payload = {
            "text": "Hello",
            "source_language": "en",
            "target_language": "hi"
        }
        response = client.post("/api/translate/text", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "नमस्ते" in data["translated_text"]

def test_text_to_sign():
    with TestClient(app) as client:
        payload = {
            "text": "Thank you",
            "language": "en"
        }
        response = client.post("/api/translate/text-to-sign", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "THANK YOU" in data["isl_tokens"]
        assert len(data["gestures"]) > 0

def test_chat_message():
    with TestClient(app) as client:
        payload = {
            "text": "Hello, I need medical help",
            "language": "en"
        }
        response = client.post("/api/chat/send", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["sender"] == "assistant"
        assert len(data["text_content"]) > 0

def test_learning_lessons_and_quiz():
    with TestClient(app) as client:
        response = client.get("/api/learning/lessons")
        assert response.status_code == 200
        lessons = response.json()
        assert len(lessons) > 0
        
        # Submit quiz
        quiz_payload = {
            "quiz_id": 1,
            "user_answer": "Thank You"
        }
        q_resp = client.post("/api/learning/quiz/submit", json=quiz_payload)
        assert q_resp.status_code == 200
        assert "is_correct" in q_resp.json()

def test_custom_gesture_flow():
    with TestClient(app) as client:
        # 1. Create gesture
        create_payload = {
            "name": "CUSTOM_ALERT",
            "description": "Emergency Wave",
            "text_en": "Alert",
            "text_hi": "चेतावनी",
            "text_bn": "সতর্কতা"
        }
        resp = client.post("/api/custom-gestures", json=create_payload)
        assert resp.status_code == 200
        g_id = resp.json()["id"]

        # 2. Upload samples
        sample = [{"x": 0.5, "y": 0.5, "z": 0.0} for _ in range(21)]
        samples_payload = {
            "samples": [sample for _ in range(6)]
        }
        resp_sample = client.post(f"/api/custom-gestures/{g_id}/samples", json=samples_payload)
        assert resp_sample.status_code == 200
        assert resp_sample.json()["samples_count"] >= 6

        # 3. Train custom gesture
        train_resp = client.post(f"/api/custom-gestures/{g_id}/train")
        assert train_resp.status_code == 200
        assert train_resp.json()["is_trained"] is True
