from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Prediction
from app.schemas.schemas import PredictLandmarksRequest, PredictSequenceRequest, PredictionResponse
from app.ml.inference import inference_engine

router = APIRouter()

@router.post("/landmarks", response_model=PredictionResponse)
def predict_landmarks(payload: PredictLandmarksRequest, db: Session = Depends(get_db)):
    """
    Real-time inference endpoint for MediaPipe 21-landmark arrays.
    Returns predicted ISL gesture, calibrated confidence, multilingual text, and status.
    """
    left_dicts = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in payload.left_hand_landmarks] if payload.left_hand_landmarks else None
    right_dicts = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in payload.right_hand_landmarks] if payload.right_hand_landmarks else None
    single_dicts = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in payload.landmarks] if payload.landmarks else None
    
    result = inference_engine.process_frame(
        left_landmarks=left_dicts,
        right_landmarks=right_dicts,
        landmarks=single_dicts,
        handedness=payload.handedness or "Right",
        mirrored_camera=payload.mirrored_camera if payload.mirrored_camera is not None else True,
        user_id=payload.user_id,
        use_custom_gestures=payload.use_custom_gestures
    )
    
    # Store prediction log in DB if confidence is above threshold
    if result["status"] == "success" and result["gesture"] not in ["NO_HAND", "UNKNOWN_GESTURE"]:
        try:
            pred = Prediction(
                user_id=payload.user_id,
                gesture_name=result["gesture"],
                confidence=result["confidence"],
                latency_ms=result.get("latency_ms", 12.0),
                input_type="landmarks",
                accepted=True
            )
            db.add(pred)
            db.commit()
        except Exception:
            pass
            
    return result

@router.post("/sequence", response_model=PredictionResponse)
def predict_sequence(payload: PredictSequenceRequest, db: Session = Depends(get_db)):
    """
    Inference endpoint for temporal frame sequences (dynamic ISL gestures).
    Feeds frames into the inference engine temporal sequence buffer.
    """
    frames = payload.frames or []
    left_frames = payload.left_frames or []
    right_frames = payload.right_frames or []
    
    max_len = max(len(frames), len(left_frames), len(right_frames))
    if max_len == 0:
        raise HTTPException(status_code=400, detail="Empty frame sequence")
        
    last_res = None
    for idx in range(max_len):
        l_lms = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in left_frames[idx]] if idx < len(left_frames) else None
        r_lms = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in right_frames[idx]] if idx < len(right_frames) else None
        s_lms = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in frames[idx]] if idx < len(frames) else None
        
        last_res = inference_engine.process_frame(
            left_landmarks=l_lms,
            right_landmarks=r_lms,
            landmarks=s_lms,
            handedness=payload.handedness or "Right",
            mirrored_camera=payload.mirrored_camera if payload.mirrored_camera is not None else True,
            user_id=payload.user_id
        )
        
    return last_res or inference_engine.process_frame()
