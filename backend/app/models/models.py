from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_guest = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    translations = relationship("Translation", back_populates="user", cascade="all, delete-orphan")
    custom_gestures = relationship("CustomGesture", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", uselist=False, cascade="all, delete-orphan")
    streak = relationship("Streak", back_populates="user", uselist=False, cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    saved_phrases = relationship("SavedPhrase", back_populates="user", cascade="all, delete-orphan")

class Gesture(Base):
    __tablename__ = "gestures"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), default="words")  # alphabet, numbers, words, phrases
    is_dynamic = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    video_url = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    animation_data = Column(JSON, nullable=True)
    text_en = Column(String(255), nullable=False)
    text_hi = Column(String(255), nullable=False)
    text_bn = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    
    samples = relationship("GestureSample", back_populates="gesture", cascade="all, delete-orphan")

class GestureSample(Base):
    __tablename__ = "gesture_samples"
    
    id = Column(Integer, primary_key=True, index=True)
    gesture_id = Column(Integer, ForeignKey("gestures.id"), nullable=False)
    landmarks_data = Column(JSON, nullable=False)  # array of frames with 21 landmarks [x,y,z]
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    
    gesture = relationship("Gesture", back_populates="samples")

class CustomGesture(Base):
    __tablename__ = "custom_gestures"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    text_en = Column(String(255), nullable=True)
    text_hi = Column(String(255), nullable=True)
    text_bn = Column(String(255), nullable=True)
    is_trained = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    samples_count = Column(Integer, default=0)
    samples_data = Column(JSON, nullable=True)  # List of captured landmark feature vectors
    trained_model_path = Column(String(255), nullable=True)
    accuracy_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    user = relationship("User", back_populates="custom_gestures")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    gesture_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(50), default="demo-baseline-v1")
    latency_ms = Column(Float, default=15.0)
    input_type = Column(String(50), default="landmarks")  # landmarks, image, sequence
    accepted = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=utcnow)
    
    user = relationship("User", back_populates="predictions")

class Translation(Base):
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source_type = Column(String(50), nullable=False)  # sign, text, speech
    target_type = Column(String(50), nullable=False)  # sign, text, speech
    source_language = Column(String(10), default="en")  # en, hi, bn
    target_language = Column(String(10), default="en")
    source_content = Column(Text, nullable=False)
    target_content = Column(Text, nullable=False)
    gesture_sequence = Column(JSON, nullable=True)  # list of gesture names
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=utcnow)
    
    user = relationship("User", back_populates="translations")

class LearningLesson(Base):
    __tablename__ = "learning_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)  # alphabet, numbers, words, phrases
    level = Column(String(30), default="beginner")  # beginner, intermediate, advanced
    description = Column(Text, nullable=True)
    order = Column(Integer, default=1)
    signs_data = Column(JSON, nullable=False)  # list of signs included with images/animations & instructions
    xp_reward = Column(Integer, default=50)
    created_at = Column(DateTime, default=utcnow)
    
    quizzes = relationship("Quiz", back_populates="lesson", cascade="all, delete-orphan")

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("learning_lessons.id"), nullable=True)
    quiz_type = Column(String(50), nullable=False)  # sign_to_word, word_to_sign, camera_practice
    prompt_text = Column(String(255), nullable=False)
    prompt_media = Column(String(255), nullable=True)
    target_gesture = Column(String(100), nullable=False)
    options = Column(JSON, nullable=True)  # List of choices for multiple choice
    correct_answer = Column(String(100), nullable=False)
    explanation = Column(Text, nullable=True)
    points = Column(Integer, default=20)
    
    lesson = relationship("LearningLesson", back_populates="quizzes")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    user_answer = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    score_earned = Column(Integer, default=0)
    timestamp = Column(DateTime, default=utcnow)
    
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    completed_lesson_ids = Column(JSON, default=list)
    completed_quiz_ids = Column(JSON, default=list)
    signs_learned = Column(Integer, default=0)
    practice_minutes = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    user = relationship("User", back_populates="progress")

class Streak(Base):
    __tablename__ = "streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_streak = Column(Integer, default=1)
    longest_streak = Column(Integer, default=1)
    last_activity_date = Column(DateTime, default=utcnow)
    total_active_days = Column(Integer, default=1)
    
    user = relationship("User", back_populates="streak")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), default="Communication Assistance")
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=utcnow)
    
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String(30), nullable=False)  # user, assistant
    text_content = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    sign_sequence = Column(JSON, nullable=True)  # mapped gestures
    timestamp = Column(DateTime, default=utcnow)
    
    session = relationship("ChatSession", back_populates="messages")

class SavedPhrase(Base):
    __tablename__ = "saved_phrases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    text_en = Column(String(255), nullable=False)
    text_hi = Column(String(255), nullable=True)
    text_bn = Column(String(255), nullable=True)
    category = Column(String(50), default="Everyday")
    sign_sequence = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    
    user = relationship("User", back_populates="saved_phrases")
