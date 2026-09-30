from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Gesture
from app.schemas.schemas import GestureResponse, GestureCreate

router = APIRouter()

@router.get("", response_model=List[GestureResponse])
def get_gestures(
    category: Optional[str] = Query(None, description="Filter by alphabet, numbers, words, phrases"),
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Gesture)
    if active_only:
        query = query.filter(Gesture.is_active == True)
    if category:
        query = query.filter(Gesture.category == category)
    return query.all()

@router.get("/{gesture_id}", response_model=GestureResponse)
def get_gesture_by_id(gesture_id: int, db: Session = Depends(get_db)):
    gesture = db.query(Gesture).filter(Gesture.id == gesture_id).first()
    if not gesture:
        raise HTTPException(status_code=404, detail="Gesture not found")
    return gesture

@router.post("", response_model=GestureResponse)
def create_gesture(gesture_in: GestureCreate, db: Session = Depends(get_db)):
    existing = db.query(Gesture).filter(Gesture.name == gesture_in.name.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Gesture name already exists")
    
    gesture = Gesture(
        name=gesture_in.name.upper(),
        category=gesture_in.category,
        is_dynamic=gesture_in.is_dynamic,
        description=gesture_in.description,
        video_url=gesture_in.video_url,
        image_url=gesture_in.image_url,
        animation_data=gesture_in.animation_data,
        text_en=gesture_in.text_en,
        text_hi=gesture_in.text_hi,
        text_bn=gesture_in.text_bn,
        is_active=gesture_in.is_active
    )
    db.add(gesture)
    db.commit()
    db.refresh(gesture)
    return gesture
