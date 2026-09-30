from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Gesture
from app.schemas.schemas import ModelStatusResponse
from app.ml.model_loader import model_registry
from app.ml.inference import inference_engine

router = APIRouter()

class UpdateModelConfigRequest(BaseModel):
    confidence_threshold: float
    active_model: str

@router.get("/model-status", response_model=ModelStatusResponse)
def get_model_status(db: Session = Depends(get_db)):
    gestures_count = db.query(Gesture).count()
    meta = model_registry.metadata
    
    return {
        "active_model": meta.get("active_model", "demo_baseline_v1"),
        "model_version": meta.get("model_version", "1.0.0-mvp"),
        "confidence_threshold": inference_engine.min_confidence,
        "supported_gestures_count": max(gestures_count, 14),
        "dataset_samples_count": meta.get("dataset_samples_count", 1500),
        "model_type": meta.get("model_type", "Geometric Random Forest & Deep MLP Baseline"),
        "is_demo_model": meta.get("is_demo_model", True),
        "last_trained": meta.get("last_trained", "2026-09-09"),
        "hardware_accelerator": meta.get("hardware_accelerator", "CPU (Optimized for Laptop)")
    }

@router.post("/model-config")
def update_model_config(payload: UpdateModelConfigRequest):
    if not (0.1 <= payload.confidence_threshold <= 0.99):
        raise HTTPException(status_code=400, detail="Confidence threshold must be between 0.10 and 0.99")

    inference_engine.min_confidence = payload.confidence_threshold
    meta = model_registry.metadata
    meta["confidence_threshold"] = payload.confidence_threshold
    meta["active_model"] = payload.active_model
    model_registry.save_metadata(meta)

    return {
        "status": "updated",
        "active_model": payload.active_model,
        "confidence_threshold": payload.confidence_threshold
    }
