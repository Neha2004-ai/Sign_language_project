from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# User & Auth
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_guest: bool = False

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Gestures
class GestureBase(BaseModel):
    name: str
    category: str = "words"
    is_dynamic: bool = False
    description: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    animation_data: Optional[Dict[str, Any]] = None
    text_en: str
    text_hi: str
    text_bn: str
    is_active: bool = True

class GestureCreate(GestureBase):
    pass

class GestureResponse(GestureBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Prediction & Landmarks
class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float = 0.0

class LandmarkFrame(BaseModel):
    landmarks: List[LandmarkPoint] = Field(..., min_length=21, max_length=42)
    handedness: Optional[str] = "Right"

class PredictLandmarksRequest(BaseModel):
    left_hand_landmarks: Optional[List[LandmarkPoint]] = None
    right_hand_landmarks: Optional[List[LandmarkPoint]] = None
    landmarks: Optional[List[LandmarkPoint]] = None
    handedness: Optional[str] = "Right"
    mirrored_camera: Optional[bool] = True
    user_id: Optional[int] = None
    use_custom_gestures: bool = True

class PredictSequenceRequest(BaseModel):
    frames: Optional[List[List[LandmarkPoint]]] = None
    left_frames: Optional[List[List[LandmarkPoint]]] = None
    right_frames: Optional[List[List[LandmarkPoint]]] = None
    handedness: Optional[str] = "Right"
    mirrored_camera: Optional[bool] = True
    user_id: Optional[int] = None

class PredictionResponse(BaseModel):
    gesture: str
    confidence: float
    text_en: str
    text_hi: str
    text_bn: str
    category: str = "words"
    is_dynamic: bool = False
    status: str = "success"  # success, low_confidence, no_hand
    message: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = []
    num_hands: Optional[int] = 0
    left_detected: Optional[bool] = False
    right_detected: Optional[bool] = False
    recognition_mode: Optional[str] = "STATIC"
    sequence_len: Optional[int] = 0
    state_machine_state: Optional[str] = "IDLE"
    is_new_confirmed_output: Optional[bool] = False
    fps: Optional[float] = 30.0
    latency_ms: Optional[float] = 12.0
    model_status: Optional[str] = "ML Ensemble Ready"

# Translation
class TranslateRequest(BaseModel):
    text: str
    source_language: str = "en"  # en, hi, bn
    target_language: str = "hi"  # en, hi, bn
    user_id: Optional[int] = None

class TextToSignRequest(BaseModel):
    text: str
    language: str = "en"  # en, hi, bn
    user_id: Optional[int] = None

class TextToSignResponse(BaseModel):
    normalized_text: str
    source_language: str
    detected_language: str
    isl_tokens: List[str]
    gestures: List[Dict[str, Any]]
    sign_sequence_description: str

class TranslationResponse(BaseModel):
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    sign_tokens: Optional[List[str]] = []

# Speech
class SpeechToSignRequest(BaseModel):
    transcript: str
    language: Optional[str] = "en"

# Chat
class ChatMessageCreate(BaseModel):
    text: str
    language: str = "en"
    session_id: Optional[int] = None

class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    text_content: str
    language: str
    sign_sequence: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    language: str
    created_at: datetime
    messages: List[ChatMessageResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Custom Gestures
class CustomGestureCreate(BaseModel):
    name: str
    description: Optional[str] = None
    text_en: Optional[str] = None
    text_hi: Optional[str] = None
    text_bn: Optional[str] = None

class CustomGestureSampleUpload(BaseModel):
    samples: List[List[LandmarkPoint]]

class CustomGestureResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    text_en: Optional[str]
    text_hi: Optional[str]
    text_bn: Optional[str]
    is_trained: bool
    is_active: bool
    samples_count: int
    accuracy_score: Optional[float]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Learning & Quizzes
class QuizOption(BaseModel):
    id: str
    label: str
    image_url: Optional[str] = None
    gesture_name: Optional[str] = None

class QuizResponse(BaseModel):
    id: int
    lesson_id: Optional[int]
    quiz_type: str
    prompt_text: str
    prompt_media: Optional[str]
    target_gesture: str
    options: Optional[List[QuizOption]]
    points: int
    model_config = ConfigDict(from_attributes=True)

class QuizSubmitRequest(BaseModel):
    quiz_id: int
    user_answer: str

class QuizSubmitResponse(BaseModel):
    quiz_id: int
    is_correct: bool
    correct_answer: str
    explanation: Optional[str]
    score_earned: int
    total_xp: int
    current_streak: int

class LessonResponse(BaseModel):
    id: int
    title: str
    category: str
    level: str
    description: Optional[str]
    order: int
    signs_data: List[Dict[str, Any]]
    xp_reward: int
    quizzes: List[QuizResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Gamification & Analytics
class UserProgressResponse(BaseModel):
    total_xp: int
    level: int
    completed_lessons_count: int
    completed_quizzes_count: int
    signs_learned: int
    practice_minutes: float
    current_streak: int
    longest_streak: int

class AnalyticsSummary(BaseModel):
    total_translations: int
    recognition_accuracy: float
    signs_learned: int
    current_streak: int
    daily_activity: List[Dict[str, Any]]
    sign_distribution: List[Dict[str, Any]]
    model_metrics: Dict[str, Any]

# Admin & Model Registry
class ModelStatusResponse(BaseModel):
    active_model: str
    model_version: str
    confidence_threshold: float
    supported_gestures_count: int
    dataset_samples_count: int
    model_type: str
    is_demo_model: bool
    last_trained: str
    hardware_accelerator: str
