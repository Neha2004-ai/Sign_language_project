from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Translation
from app.schemas.schemas import (
    TranslateRequest, TranslationResponse, TextToSignRequest, TextToSignResponse
)
from app.services.translation_service import translation_service

router = APIRouter()

@router.post("/text", response_model=TranslationResponse)
def translate_text(payload: TranslateRequest, db: Session = Depends(get_db)):
    translated = translation_service.translate_text(
        text=payload.text,
        source_lang=payload.source_language,
        target_lang=payload.target_language
    )
    
    tokens, gestures, _ = translation_service.text_to_isl_tokens(
        text=payload.text,
        lang=payload.source_language
    )
    
    # Store in history
    try:
        t_record = Translation(
            user_id=payload.user_id,
            source_type="text",
            target_type="text",
            source_language=payload.source_language,
            target_language=payload.target_language,
            source_content=payload.text,
            target_content=translated,
            gesture_sequence=tokens
        )
        db.add(t_record)
        db.commit()
    except Exception:
        pass

    return {
        "source_text": payload.text,
        "translated_text": translated,
        "source_language": payload.source_language,
        "target_language": payload.target_language,
        "sign_tokens": tokens
    }

@router.post("/text-to-sign", response_model=TextToSignResponse)
def convert_text_to_sign(payload: TextToSignRequest, db: Session = Depends(get_db)):
    detected = translation_service.detect_language(payload.text)
    tokens, gestures, seq_desc = translation_service.text_to_isl_tokens(
        text=payload.text,
        lang=payload.language or detected
    )
    
    # Save translation log
    try:
        t_record = Translation(
            user_id=payload.user_id,
            source_type="text",
            target_type="sign",
            source_language=payload.language or detected,
            target_language="isl",
            source_content=payload.text,
            target_content=",".join(tokens),
            gesture_sequence=tokens
        )
        db.add(t_record)
        db.commit()
    except Exception:
        pass

    return {
        "normalized_text": payload.text.strip(),
        "source_language": payload.language,
        "detected_language": detected,
        "isl_tokens": tokens,
        "gestures": gestures,
        "sign_sequence_description": seq_desc
    }
