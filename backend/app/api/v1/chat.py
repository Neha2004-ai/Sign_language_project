from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import ChatSession, ChatMessage, User
from app.schemas.schemas import ChatMessageCreate, ChatSessionResponse, ChatMessageResponse
from app.services.chat_service import chat_service

router = APIRouter()

@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_user_chat_sessions(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    if not user_id:
        demo = db.query(User).filter(User.email == "demo@signbridge.ai").first()
        user_id = demo.id if demo else 1
        
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()
    return sessions

@router.post("/send", response_model=ChatMessageResponse)
def send_chat_message(payload: ChatMessageCreate, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        # Find or create demo user
        if not user_id:
            demo = db.query(User).filter(User.email == "demo@signbridge.ai").first()
            if not demo:
                demo = db.query(User).first()
            if not demo:
                from app.core.security import get_password_hash
                demo = User(
                    email="demo@signbridge.ai",
                    hashed_password=get_password_hash("Password123!"),
                    full_name="Alex Rivers",
                    is_guest=True
                )
                db.add(demo)
                db.flush()
            user_id = demo.id

        # Find or create chat session
        session = None
        if payload.session_id:
            session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()
            
        if not session:
            session = ChatSession(
                user_id=user_id,
                title=payload.text[:30] + "..." if len(payload.text) > 30 else payload.text,
                language=payload.language
            )
            db.add(session)
            db.flush()

        # 1. Store user message
        user_msg = ChatMessage(
            session_id=session.id,
            sender="user",
            text_content=payload.text,
            language=payload.language
        )
        db.add(user_msg)

        # 2. Generate assistant response with ISL sign sequence
        response_data = chat_service.generate_response(payload.text, payload.language)
        
        # Ensure sign_sequence is properly structured for the frontend
        sign_sequence = response_data.get("sign_sequence", [])
        if sign_sequence:
            # Validate each gesture has the required fields
            validated_sequence = []
            for gesture in sign_sequence:
                validated_gesture = {
                    "token": gesture.get("token", ""),
                    "type": gesture.get("type", "word"),
                    "label": gesture.get("label", gesture.get("token", "")),
                    "duration_ms": gesture.get("duration_ms", 1200),
                    "description": gesture.get("description", f"ISL Sign '{gesture.get('token', '')}'")
                }
                validated_sequence.append(validated_gesture)
            sign_sequence = validated_sequence

        bot_msg = ChatMessage(
            session_id=session.id,
            sender="assistant",
            text_content=response_data["text"],
            language=payload.language,
            sign_sequence=sign_sequence
        )
        db.add(bot_msg)
        db.commit()
        db.refresh(bot_msg)

        return bot_msg

    except Exception as e:
        db.rollback()
        print(f"Chat endpoint error: {e}")
        
        # Return a graceful error response instead of crashing
        # Create a minimal response without DB
        error_response_text = "I apologize for the technical difficulty. Please try again in a moment."
        if payload.language == "hi":
            error_response_text = "तकनीकी कठिनाई के लिए क्षमा करें। कृपया कुछ क्षण में पुनः प्रयास करें।"
        elif payload.language == "bn":
            error_response_text = "প্রযুক্তিগত অসুবিধার জন্য ক্ষমা চাই। দয়া করে কিছুক্ষণ পরে আবার চেষ্টা করুন।"
        
        raise HTTPException(
            status_code=500,
            detail=f"Chat service error: {str(e)}"
        )
