from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import LearningLesson, Quiz, QuizAttempt, UserProgress, Streak, User
from app.schemas.schemas import LessonResponse, QuizResponse, QuizSubmitRequest, QuizSubmitResponse, UserProgressResponse

router = APIRouter()

@router.get("/lessons", response_model=List[LessonResponse])
def get_lessons(db: Session = Depends(get_db)):
    try:
        lessons = db.query(LearningLesson).order_by(LearningLesson.order.asc()).all()
        return lessons
    except Exception as e:
        print(f"Error loading lessons: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load lessons: {str(e)}")

@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson_detail(lesson_id: int, db: Session = Depends(get_db)):
    try:
        lesson = db.query(LearningLesson).filter(LearningLesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return lesson
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error loading lesson {lesson_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load lesson: {str(e)}")

@router.post("/quiz/submit", response_model=QuizSubmitResponse)
def submit_quiz(payload: QuizSubmitRequest, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        # Find user
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

        # Find quiz
        quiz = db.query(Quiz).filter(Quiz.id == payload.quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        is_correct = payload.user_answer.strip().upper() == quiz.correct_answer.strip().upper()
        earned = quiz.points if is_correct else 0

        # Record attempt
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz.id,
            user_answer=payload.user_answer,
            is_correct=is_correct,
            score_earned=earned
        )
        db.add(attempt)

        # Get or create progress
        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                total_xp=0,
                level=1,
                signs_learned=0,
                practice_minutes=0.0,
                completed_lesson_ids=[],
                completed_quiz_ids=[]
            )
            db.add(progress)
            db.flush()

        # Get or create streak
        streak = db.query(Streak).filter(Streak.user_id == user_id).first()
        if not streak:
            streak = Streak(
                user_id=user_id,
                current_streak=1,
                longest_streak=1,
                total_active_days=1
            )
            db.add(streak)
            db.flush()

        if is_correct:
            # Safely update XP
            progress.total_xp = (progress.total_xp or 0) + earned
            progress.level = 1 + ((progress.total_xp or 0) // 250)

            # Safely update completed quiz IDs
            completed_quizzes = list(progress.completed_quiz_ids or [])
            if quiz.id not in completed_quizzes:
                completed_quizzes.append(quiz.id)
                progress.completed_quiz_ids = completed_quizzes
                progress.signs_learned = (progress.signs_learned or 0) + 1

        # Update streak
        streak.last_activity_date = datetime.now(timezone.utc)
        
        # Update longest streak if current is higher
        if (streak.current_streak or 0) > (streak.longest_streak or 0):
            streak.longest_streak = streak.current_streak

        db.commit()

        return {
            "quiz_id": quiz.id,
            "is_correct": is_correct,
            "correct_answer": quiz.correct_answer,
            "explanation": quiz.explanation or "",
            "score_earned": earned,
            "total_xp": progress.total_xp or 0,
            "current_streak": streak.current_streak or 1
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Quiz submission error: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz submission failed: {str(e)}")

@router.get("/progress", response_model=UserProgressResponse)
def get_user_progress(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        if not user_id:
            demo = db.query(User).filter(User.email == "demo@signbridge.ai").first()
            if demo:
                user_id = demo.id
            else:
                # Return default progress if no user found
                return {
                    "total_xp": 0,
                    "level": 1,
                    "completed_lessons_count": 0,
                    "completed_quizzes_count": 0,
                    "signs_learned": 0,
                    "practice_minutes": 0.0,
                    "current_streak": 0,
                    "longest_streak": 0
                }

        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        streak = db.query(Streak).filter(Streak.user_id == user_id).first()

        total_xp = progress.total_xp if progress else 0
        level = progress.level if progress else 1
        signs_learned = progress.signs_learned if progress else 0
        practice_minutes = progress.practice_minutes if progress else 0.0
        c_lessons = len(progress.completed_lesson_ids or []) if progress else 0
        c_quizzes = len(progress.completed_quiz_ids or []) if progress else 0
        c_streak = streak.current_streak if streak else 0
        l_streak = streak.longest_streak if streak else 0

        return {
            "total_xp": total_xp,
            "level": level,
            "completed_lessons_count": c_lessons,
            "completed_quizzes_count": c_quizzes,
            "signs_learned": signs_learned,
            "practice_minutes": practice_minutes,
            "current_streak": c_streak,
            "longest_streak": l_streak
        }

    except Exception as e:
        print(f"Progress loading error: {e}")
        # Return safe defaults instead of crashing
        return {
            "total_xp": 0,
            "level": 1,
            "completed_lessons_count": 0,
            "completed_quizzes_count": 0,
            "signs_learned": 0,
            "practice_minutes": 0.0,
            "current_streak": 0,
            "longest_streak": 0
        }
