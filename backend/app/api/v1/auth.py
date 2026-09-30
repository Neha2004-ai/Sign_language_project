from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User, Streak, UserProgress
from app.schemas.schemas import UserCreate, UserLogin, Token, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name or user_in.email.split("@")[0],
        is_guest=user_in.is_guest
    )
    db.add(user)
    db.flush()
    
    # Initialize streak & progress
    streak = Streak(user_id=user.id)
    progress = UserProgress(user_id=user.id)
    db.add(streak)
    db.add(progress)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account.")
        
    access_token = create_access_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/guest", response_model=Token)
def guest_login(db: Session = Depends(get_db)):
    # Find or create guest user
    guest_email = "guest@signbridge.ai"
    guest = db.query(User).filter(User.email == guest_email).first()
    if not guest:
        guest = User(
            email=guest_email,
            hashed_password=get_password_hash("guest_signbridge_2026"),
            full_name="Guest User",
            is_guest=True
        )
        db.add(guest)
        db.flush()
        streak = Streak(user_id=guest.id, current_streak=1)
        progress = UserProgress(user_id=guest.id, total_xp=50)
        db.add(streak)
        db.add(progress)
        db.commit()
        db.refresh(guest)
        
    access_token = create_access_token(guest.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": guest
    }
