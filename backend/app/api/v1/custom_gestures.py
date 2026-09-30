import numpy as np
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import CustomGesture, User
from app.schemas.schemas import (
    CustomGestureCreate, CustomGestureResponse, CustomGestureSampleUpload
)
from app.ml.feature_extractor import LandmarkFeatureExtractor
from app.ml.inference import inference_engine

router = APIRouter()

@router.get("", response_model=List[CustomGestureResponse])
def get_user_custom_gestures(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    if not user_id:
        demo = db.query(User).filter(User.email == "demo@signbridge.ai").first()
        user_id = demo.id if demo else 1
    return db.query(CustomGesture).filter(CustomGesture.user_id == user_id).all()

@router.post("", response_model=CustomGestureResponse)
def create_custom_gesture(payload: CustomGestureCreate, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    if not user_id:
        demo = db.query(User).filter(User.email == "demo@signbridge.ai").first()
        user_id = demo.id if demo else 1

    cg = CustomGesture(
        user_id=user_id,
        name=payload.name.strip().upper(),
        description=payload.description,
        text_en=payload.text_en or payload.name,
        text_hi=payload.text_hi or payload.name,
        text_bn=payload.text_bn or payload.name,
        samples_count=0,
        samples_data=[]
    )
    db.add(cg)
    db.commit()
    db.refresh(cg)
    return cg

@router.post("/{gesture_id}/samples", response_model=CustomGestureResponse)
def upload_gesture_samples(gesture_id: int, payload: CustomGestureSampleUpload, db: Session = Depends(get_db)):
    cg = db.query(CustomGesture).filter(CustomGesture.id == gesture_id).first()
    if not cg:
        raise HTTPException(status_code=404, detail="Custom gesture not found")

    # Extract 93-dim feature vectors for every uploaded frame
    new_vectors = []
    for sample in payload.samples:
        lm_dicts = [{"x": p.x, "y": p.y, "z": p.z} for p in sample]
        feat = LandmarkFeatureExtractor.extract_full_feature_vector(lm_dicts)
        new_vectors.append(feat.tolist())

    current_data = list(cg.samples_data or [])
    current_data.extend(new_vectors)
    cg.samples_data = current_data
    cg.samples_count = len(current_data)
    db.commit()
    db.refresh(cg)
    return cg

@router.post("/{gesture_id}/train", response_model=CustomGestureResponse)
def train_custom_gesture(gesture_id: int, db: Session = Depends(get_db)):
    cg = db.query(CustomGesture).filter(CustomGesture.id == gesture_id).first()
    if not cg:
        raise HTTPException(status_code=404, detail="Custom gesture not found")

    if not cg.samples_data or len(cg.samples_data) < 5:
        raise HTTPException(
            status_code=400,
            detail=f"At least 5 samples required for training. Currently have {len(cg.samples_data or [])}."
        )

    # Convert to numpy and register with custom matcher
    sample_arrays = [np.array(vec, dtype=np.float32) for vec in cg.samples_data]
    inference_engine.custom_matcher.register_user_gesture(
        user_id=cg.user_id,
        gesture_name=cg.name,
        sample_vectors=sample_arrays
    )

    # Calculate internal consistency score as accuracy metric
    mean_vec = np.mean(sample_arrays, axis=0)
    sims = [
        float(np.dot(v, mean_vec) / (np.linalg.norm(v) * np.linalg.norm(mean_vec) + 1e-6))
        for v in sample_arrays
    ]
    avg_accuracy = float(np.mean(sims)) * 100.0

    cg.is_trained = True
    cg.accuracy_score = round(avg_accuracy, 2)
    db.commit()
    db.refresh(cg)
    return cg

@router.delete("/{gesture_id}")
def delete_custom_gesture(gesture_id: int, db: Session = Depends(get_db)):
    cg = db.query(CustomGesture).filter(CustomGesture.id == gesture_id).first()
    if not cg:
        raise HTTPException(status_code=404, detail="Custom gesture not found")
    db.delete(cg)
    db.commit()
    return {"status": "deleted", "id": gesture_id}
