from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Translation
from app.schemas.schemas import SpeechToSignRequest, TextToSignResponse
from app.services.translation_service import translation_service

router = APIRouter()

@router.post("/to-sign", response_model=TextToSignResponse)
def speech_to_sign(payload: SpeechToSignRequest, db: Session = Depends(get_db)):
    """
    Accepts speech transcript in English, Hindi, or Bengali,
    normalizes it, detects language, and maps to ISL sign sequence.
    """
    detected = translation_service.detect_language(payload.transcript)
    tokens, gestures, seq_desc = translation_service.text_to_isl_tokens(
        text=payload.transcript,
        lang=payload.language or detected
    )

    return {
        "normalized_text": payload.transcript.strip(),
        "source_language": payload.language or detected,
        "detected_language": detected,
        "isl_tokens": tokens,
        "gestures": gestures,
        "sign_sequence_description": seq_desc
    }
