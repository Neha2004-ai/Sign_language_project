from sqlalchemy.orm import Session
from app.models.models import (
    User, Gesture, LearningLesson, Quiz, UserProgress, Streak, SavedPhrase
)
from app.core.security import get_password_hash

def seed_database(db: Session):
    """Populates database with initial ISL vocabulary, lessons, quizzes, and demo user."""
    
    # 1. Check if already seeded
    if db.query(Gesture).first():
        return

    print("Seeding SignBridge AI Database...")

    # 2. Seed Default User
    demo_user = User(
        email="demo@signbridge.ai",
        hashed_password=get_password_hash("Password123!"),
        full_name="Alex Rivers",
        is_guest=False,
        is_active=True,
        is_superuser=True
    )
    db.add(demo_user)
    db.flush()

    # User streak and progress
    demo_streak = Streak(
        user_id=demo_user.id,
        current_streak=0,
        longest_streak=0,
        total_active_days=0
    )
    demo_progress = UserProgress(
        user_id=demo_user.id,
        total_xp=0,
        level=1,
        signs_learned=0,
        practice_minutes=0.0,
        completed_lesson_ids=[],
        completed_quiz_ids=[]
    )
    db.add(demo_streak)
    db.add(demo_progress)

    # 3. Seed Gestures
    gestures_list = [
        # Common Words & Phrases
        {
            "name": "HELLO", "category": "words", "is_dynamic": True,
            "description": "Open hand with palm facing outward, wave gently from right to left or salute from brow.",
            "text_en": "Hello", "text_hi": "नमस्ते / हैलो", "text_bn": "হ্যালো / নমস্কার",
            "animation_data": {"type": "wave", "fingers": [1, 1, 1, 1, 1], "motion": "horizontal_wave"}
        },
        {
            "name": "THANK YOU", "category": "words", "is_dynamic": True,
            "description": "Flat open hand with fingertips touching chin or lips, moving forward and slightly downward.",
            "text_en": "Thank You", "text_hi": "धन्यवाद", "text_bn": "ধন্যবাদ",
            "animation_data": {"type": "chin_forward", "fingers": [0, 1, 1, 1, 1], "motion": "forward_drop"}
        },
        {
            "name": "YES", "category": "words", "is_dynamic": True,
            "description": "Closed fist with thumb upright, nodding up and down like a head nod.",
            "text_en": "Yes", "text_hi": "हाँ", "text_bn": "হ্যাঁ",
            "animation_data": {"type": "nodding_fist", "fingers": [1, 0, 0, 0, 0], "motion": "vertical_nod"}
        },
        {
            "name": "NO", "category": "words", "is_dynamic": True,
            "description": "Extended index and middle finger snapping down onto the thumb repeatedly.",
            "text_en": "No", "text_hi": "नहीं", "text_bn": "না",
            "animation_data": {"type": "snap_fingers", "fingers": [0, 1, 1, 0, 0], "motion": "snap_close"}
        },
        {
            "name": "HELP", "category": "phrases", "is_dynamic": True,
            "description": "Closed fist with thumb up resting on top of a flat open palm, raised together upward.",
            "text_en": "I Need Help", "text_hi": "मुझे मदद चाहिए", "text_bn": "আমার সাহায্য দরকার",
            "animation_data": {"type": "palm_lift", "fingers": [1, 0, 0, 0, 0], "motion": "upward_lift"}
        },
        {
            "name": "GOODBYE", "category": "words", "is_dynamic": True,
            "description": "Open hand raised, bending fingers up and down in a waving motion.",
            "text_en": "Goodbye", "text_hi": "अलविदा", "text_bn": "বিদায়",
            "animation_data": {"type": "wave", "fingers": [1, 1, 1, 1, 1], "motion": "open_close_wave"}
        },
        {
            "name": "PLEASE", "category": "words", "is_dynamic": True,
            "description": "Flat hand rubbing over the center of the chest in a circular clockwise motion.",
            "text_en": "Please", "text_hi": "कृपया", "text_bn": "দয়া করে",
            "animation_data": {"type": "chest_circle", "fingers": [0, 1, 1, 1, 1], "motion": "circle_chest"}
        },
        {
            "name": "SORRY", "category": "words", "is_dynamic": True,
            "description": "Closed fist with thumb across fingers rubbing the center of the chest in a circle.",
            "text_en": "Sorry", "text_hi": "माफ़ कीजिये", "text_bn": "দুঃখিত",
            "animation_data": {"type": "chest_circle", "fingers": [1, 0, 0, 0, 0], "motion": "fist_circle"}
        },
        {
            "name": "I LOVE YOU", "category": "phrases", "is_dynamic": False,
            "description": "Thumb, index finger, and pinky finger extended with middle and ring fingers folded down.",
            "text_en": "I Love You", "text_hi": "मैं आपसे प्यार करता हूँ", "text_bn": "আমি তোমাকে ভালোবাসি",
            "animation_data": {"type": "static_pose", "fingers": [1, 1, 0, 0, 1], "motion": "static"}
        },
        {
            "name": "WATER", "category": "words", "is_dynamic": True,
            "description": "W-handshape or thumb near mouth tilted slightly mimicking drinking water.",
            "text_en": "Water", "text_hi": "पानी", "text_bn": "জল",
            "animation_data": {"type": "drink_motion", "fingers": [1, 0, 0, 0, 0], "motion": "tilt_drink"}
        },
        {
            "name": "OK", "category": "words", "is_dynamic": False,
            "description": "Thumb and index tips touching to form a circle with middle, ring, pinky extended.",
            "text_en": "OK / Understood", "text_hi": "ठीक है", "text_bn": "ঠিক আছে",
            "animation_data": {"type": "static_pose", "fingers": [0, 0, 1, 1, 1], "motion": "static"}
        },
        {
            "name": "NAMASTE", "category": "phrases", "is_dynamic": False,
            "description": "Both flat hands pressed together palms touching in front of chest (Anjali Mudra).",
            "text_en": "Namaste / Greetings", "text_hi": "नमस्ते / नमस्कार", "text_bn": "নমস্কার / প্রণতি",
            "animation_data": {"type": "two_hand", "fingers": [1, 1, 1, 1, 1], "motion": "prayer"}
        },
        {
            "name": "STOP", "category": "words", "is_dynamic": True,
            "description": "Non-dominant hand flat horizontal palm up; dominant open hand descends down perpendicularly onto the palm.",
            "text_en": "Stop / Halt", "text_hi": "रुकिए / बंद करो", "text_bn": "থামুন / বন্ধ করুন",
            "animation_data": {"type": "two_hand", "fingers": [1, 1, 1, 1, 1], "motion": "chop_down"}
        },
        {
            "name": "BOOK", "category": "words", "is_dynamic": True,
            "description": "Both flat palms touching together, then opening outward like opening the pages of a book.",
            "text_en": "Book / Reading", "text_hi": "किताब / पुस्तक", "text_bn": "বই / পুস্তক",
            "animation_data": {"type": "two_hand", "fingers": [1, 1, 1, 1, 1], "motion": "open_book"}
        },
        {
            "name": "PEACE", "category": "phrases", "is_dynamic": False,
            "description": "Both hands showing V-sign / palms spread symmetrically.",
            "text_en": "Peace / Harmony", "text_hi": "शांति", "text_bn": "শান্তি",
            "animation_data": {"type": "two_hand", "fingers": [0, 1, 1, 0, 0], "motion": "v_spread"}
        },
        # Numbers 0-9
        {
            "name": "0", "category": "numbers", "is_dynamic": False,
            "description": "All fingers curved to meet thumb forming an 'O' shape.",
            "text_en": "0", "text_hi": "० (शून्य)", "text_bn": "০ (শূন্য)",
            "animation_data": {"type": "number", "fingers": [0, 0, 0, 0, 0]}
        },
        {
            "name": "1", "category": "numbers", "is_dynamic": False,
            "description": "Index finger extended vertically, other fingers closed with thumb over ring finger.",
            "text_en": "1", "text_hi": "१ (एक)", "text_bn": "১ (এক)",
            "animation_data": {"type": "number", "fingers": [0, 1, 0, 0, 0]}
        },
        {
            "name": "2", "category": "numbers", "is_dynamic": False,
            "description": "Index and middle finger extended in a 'V' shape, others closed.",
            "text_en": "2", "text_hi": "२ (दो)", "text_bn": "২ (দুই)",
            "animation_data": {"type": "number", "fingers": [0, 1, 1, 0, 0]}
        },
        {
            "name": "3", "category": "numbers", "is_dynamic": False,
            "description": "Thumb, index, and middle finger extended, ring and pinky closed.",
            "text_en": "3", "text_hi": "३ (तीन)", "text_bn": "৩ (তিন)",
            "animation_data": {"type": "number", "fingers": [1, 1, 1, 0, 0]}
        },
        {
            "name": "4", "category": "numbers", "is_dynamic": False,
            "description": "Four fingers (index, middle, ring, pinky) extended upward, thumb folded into palm.",
            "text_en": "4", "text_hi": "४ (चार)", "text_bn": "৪ (চার)",
            "animation_data": {"type": "number", "fingers": [0, 1, 1, 1, 1]}
        },
        {
            "name": "5", "category": "numbers", "is_dynamic": False,
            "description": "All five fingers extended and spread wide.",
            "text_en": "5", "text_hi": "५ (पाँच)", "text_bn": "৫ (পাঁচ)",
            "animation_data": {"type": "number", "fingers": [1, 1, 1, 1, 1]}
        }
    ]

    for g_data in gestures_list:
        gesture = Gesture(
            name=g_data["name"],
            category=g_data.get("category", "words"),
            is_dynamic=g_data.get("is_dynamic", False),
            description=g_data.get("description", ""),
            text_en=g_data["text_en"],
            text_hi=g_data["text_hi"],
            text_bn=g_data["text_bn"],
            image_url=g_data.get("image_url"),
            animation_data=g_data.get("animation_data", {})
        )
        db.add(gesture)

    # 4. Seed Learning Lessons — 6 Modules with multiple quizzes each
    lessons_data = [
        {
            "title": "Module 1: Everyday Social Greetings",
            "category": "words",
            "level": "beginner",
            "order": 1,
            "xp_reward": 100,
            "description": "Master essential Indian Sign Language greeting signs including Hello, Thank You, and Goodbye.",
            "signs_data": [
                {"name": "HELLO", "label": "Hello", "meaning": "Friendly greeting gesture", "tips": "Open palm, gentle side-to-side movement near temple"},
                {"name": "THANK YOU", "label": "Thank You", "meaning": "Expressing gratitude", "tips": "Touch chin with flat fingers, move outward and down"},
                {"name": "GOODBYE", "label": "Goodbye", "meaning": "Parting greeting", "tips": "Wave open hand at shoulder height with fingers bending"}
            ],
            "quizzes": [
                {
                    "quiz_type": "sign_to_word",
                    "prompt_text": "Which greeting is performed by touching the chin with flat fingertips and extending the hand forward?",
                    "target_gesture": "THANK YOU",
                    "options": [
                        {"id": "a", "label": "Hello"},
                        {"id": "b", "label": "Thank You"},
                        {"id": "c", "label": "Sorry"},
                        {"id": "d", "label": "Please"}
                    ],
                    "correct_answer": "Thank You",
                    "explanation": "Thank You in ISL is conveyed by bringing the fingertips to the chin/lips and extending outward.",
                    "points": 25
                },
                {
                    "quiz_type": "word_to_sign",
                    "prompt_text": "How do you sign 'HELLO' in ISL?",
                    "target_gesture": "HELLO",
                    "options": [
                        {"id": "a", "label": "Open hand wave with all 5 fingers spread"},
                        {"id": "b", "label": "Closed fist with thumb up"},
                        {"id": "c", "label": "Both palms pressed together"},
                        {"id": "d", "label": "Index finger pointing forward"}
                    ],
                    "correct_answer": "Open hand wave with all 5 fingers spread",
                    "explanation": "HELLO in ISL is an open hand with all 5 fingers spread, waved gently near the temple.",
                    "points": 25
                },
                {
                    "quiz_type": "camera_practice",
                    "prompt_text": "Show the 'HELLO' sign to the camera (Open hand, 5 fingers spread).",
                    "target_gesture": "HELLO",
                    "options": [],
                    "correct_answer": "HELLO",
                    "explanation": "Perform the open hand gesture clearly in the camera frame.",
                    "points": 50
                }
            ]
        },
        {
            "title": "Module 2: Essential Communication & Answers",
            "category": "words",
            "level": "beginner",
            "order": 2,
            "xp_reward": 120,
            "description": "Learn affirmative and negative signs (Yes, No, Please, Sorry) for daily conversations.",
            "signs_data": [
                {"name": "YES", "label": "Yes", "meaning": "Affirmation / Agreement", "tips": "Closed fist with thumb up, nod hand up and down"},
                {"name": "NO", "label": "No", "meaning": "Negation / Disagreement", "tips": "Index and middle finger snapping onto thumb"},
                {"name": "PLEASE", "label": "Please", "meaning": "Polite request", "tips": "Flat palm rubbing chest circularly (clockwise)"},
                {"name": "SORRY", "label": "Sorry", "meaning": "Apology", "tips": "Closed fist rubbing center of chest in a circle"}
            ],
            "quizzes": [
                {
                    "quiz_type": "word_to_sign",
                    "prompt_text": "What hand shape represents 'YES' in ISL?",
                    "target_gesture": "YES",
                    "options": [
                        {"id": "a", "label": "Nodding fist with upright thumb"},
                        {"id": "b", "label": "Open spread fingers"},
                        {"id": "c", "label": "Two fingers pointed down"},
                        {"id": "d", "label": "Touching the ear"}
                    ],
                    "correct_answer": "Nodding fist with upright thumb",
                    "explanation": "In ISL, 'Yes' resembles a nodding fist motion with thumb upright.",
                    "points": 30
                },
                {
                    "quiz_type": "sign_to_word",
                    "prompt_text": "Index and middle fingers snapping onto the thumb repeatedly — which sign is this?",
                    "target_gesture": "NO",
                    "options": [
                        {"id": "a", "label": "Yes"},
                        {"id": "b", "label": "No"},
                        {"id": "c", "label": "OK"},
                        {"id": "d", "label": "Stop"}
                    ],
                    "correct_answer": "No",
                    "explanation": "In ISL, 'No' is performed by extending index and middle fingers and snapping them onto the thumb.",
                    "points": 30
                },
                {
                    "quiz_type": "sign_to_word",
                    "prompt_text": "A closed fist rubbing in a circular motion on the chest represents which ISL sign?",
                    "target_gesture": "SORRY",
                    "options": [
                        {"id": "a", "label": "Please"},
                        {"id": "b", "label": "Thank You"},
                        {"id": "c", "label": "Sorry"},
                        {"id": "d", "label": "Help"}
                    ],
                    "correct_answer": "Sorry",
                    "explanation": "SORRY in ISL is a closed fist rubbing in a circle on the chest. PLEASE is similar but uses a flat palm.",
                    "points": 30
                },
                {
                    "quiz_type": "camera_practice",
                    "prompt_text": "Show the 'YES' sign to the camera (Closed fist, thumb up).",
                    "target_gesture": "YES",
                    "options": [],
                    "correct_answer": "YES",
                    "explanation": "Make a fist with your thumb pointing up and nod your hand.",
                    "points": 50
                }
            ]
        },
        {
            "title": "Module 3: Numbers & Counting (0–5)",
            "category": "numbers",
            "level": "beginner",
            "order": 3,
            "xp_reward": 150,
            "description": "Master numerical counting from 0 to 5 in Indian Sign Language.",
            "signs_data": [
                {"name": "0", "label": "Zero (0)", "meaning": "Number 0", "tips": "Form an O shape with all fingers touching thumb"},
                {"name": "1", "label": "One (1)", "meaning": "Number 1", "tips": "Only index finger extended vertically"},
                {"name": "2", "label": "Two (2)", "meaning": "Number 2", "tips": "Index and middle extended (V-shape)"},
                {"name": "3", "label": "Three (3)", "meaning": "Number 3", "tips": "Thumb, index, and middle extended"},
                {"name": "4", "label": "Four (4)", "meaning": "Number 4", "tips": "Four fingers up, thumb folded across palm"},
                {"name": "5", "label": "Five (5)", "meaning": "Number 5", "tips": "All five fingers spread open wide"}
            ],
            "quizzes": [
                {
                    "quiz_type": "sign_to_word",
                    "prompt_text": "A V-shape with index and middle fingers extended — which number is this?",
                    "target_gesture": "2",
                    "options": [
                        {"id": "a", "label": "1"},
                        {"id": "b", "label": "2"},
                        {"id": "c", "label": "3"},
                        {"id": "d", "label": "5"}
                    ],
                    "correct_answer": "2",
                    "explanation": "The V-shape (index + middle) represents the number 2 in ISL.",
                    "points": 25
                },
                {
                    "quiz_type": "word_to_sign",
                    "prompt_text": "How do you sign the number '3' in ISL?",
                    "target_gesture": "3",
                    "options": [
                        {"id": "a", "label": "Index, middle, and ring fingers extended"},
                        {"id": "b", "label": "Thumb, index, and middle fingers extended"},
                        {"id": "c", "label": "All fingers in a fist"},
                        {"id": "d", "label": "Pinky, ring, and middle extended"}
                    ],
                    "correct_answer": "Thumb, index, and middle fingers extended",
                    "explanation": "ISL '3' uses thumb + index + middle fingers extended, with ring and pinky curled.",
                    "points": 25
                },
                {
                    "quiz_type": "camera_practice",
                    "prompt_text": "Show the number '1' sign to the camera (Single index finger extended vertically).",
                    "target_gesture": "1",
                    "options": [],
                    "correct_answer": "1",
                    "explanation": "Hold up only your index finger steadily.",
                    "points": 40
                },
                {
                    "quiz_type": "camera_practice",
                    "prompt_text": "Show the number '5' sign to the camera (All five fingers spread wide).",
                    "target_gesture": "5",
                    "options": [],
                    "correct_answer": "5",
                    "explanation": "Spread all five fingers wide and hold steady.",
                    "points": 40
                }
            ]
        },
        {
            "title": "Module 4: Expressing Needs & Emotions",
            "category": "words",
            "level": "intermediate",
            "order": 4,
            "xp_reward": 140,
            "description": "Learn to express basic needs (Water, Help) and emotions (I Love You, OK) in ISL.",
            "signs_data": [
                {"name": "WATER", "label": "Water", "meaning": "Requesting water / thirst", "tips": "Thumb near mouth, tilt as if drinking from a glass"},
                {"name": "HELP", "label": "Help", "meaning": "Requesting assistance", "tips": "Fist on top of flat palm, both lifted upward together"},
                {"name": "I LOVE YOU", "label": "I Love You", "meaning": "Expression of love", "tips": "Thumb + index + pinky extended, middle + ring curled"},
                {"name": "OK", "label": "OK", "meaning": "Agreement / Understanding", "tips": "Thumb and index tips touching (circle), other 3 fingers up"}
            ],
            "quizzes": [
                {
                    "quiz_type": "sign_to_word",
                    "prompt_text": "Thumb, index finger, and pinky extended with middle and ring curled — which sign is this?",
                    "target_gesture": "I LOVE YOU",
                    "options": [
                        {"id": "a", "label": "OK"},
                        {"id": "b", "label": "I Love You"},
                        {"id": "c", "label": "Hello"},
                        {"id": "d", "label": "Peace"}
                    ],
                    "correct_answer": "I Love You",
                    "explanation": "The 'I Love You' sign combines the letters I, L, and Y in one gesture.",
                    "points": 30
                },
                {
                    "quiz_type": "word_to_sign",
                    "prompt_text": "How do you sign 'WATER' in ISL?",
                    "target_gesture": "WATER",
                    "options": [
                        {"id": "a", "label": "Thumb near mouth, tilted like drinking"},
                        {"id": "b", "label": "Both hands making waves"},
                        {"id": "c", "label": "Pointing at a glass"},
                        {"id": "d", "label": "Flat palm facing down"}
                    ],
                    "correct_answer": "Thumb near mouth, tilted like drinking",
                    "explanation": "ISL WATER mimics the act of drinking — thumb near mouth tilted slightly.",
                    "points": 30
                },
                {
                    "quiz_type": "sign_to_word",
                    "prompt_text": "A fist placed on top of a flat palm, both lifted upward together — what does this mean?",
                    "target_gesture": "HELP",
                    "options": [
                        {"id": "a", "label": "Stop"},
                        {"id": "b", "label": "Work"},
                        {"id": "c", "label": "Help"},
                        {"id": "d", "label": "Book"}
                    ],
                    "correct_answer": "Help",
                    "explanation": "The HELP sign in ISL uses a fist on a flat palm, lifted upward to signal need for assistance.",
                    "points": 30
                }
            ]
        },
        {
            "title": "Module 5: Two-Hand ISL Signs",
            "category": "words",
            "level": "intermediate",
            "order": 5,
            "xp_reward": 180,
            "description": "Learn signs that require both hands — Namaste, Stop, Book, and Peace.",
            "signs_data": [
                {"name": "NAMASTE", "label": "Namaste", "meaning": "Respectful greeting (Anjali Mudra)", "tips": "Both flat palms pressed together at chest level, fingers pointing up"},
                {"name": "STOP", "label": "Stop", "meaning": "Command to halt", "tips": "One flat palm horizontal, other open hand descends perpendicularly onto it"},
                {"name": "BOOK", "label": "Book", "meaning": "Book / Reading", "tips": "Both flat palms together, then open outward like opening a book"},
                {"name": "PEACE", "label": "Peace", "meaning": "Peace / Harmony", "tips": "Both hands showing V-sign (index + middle) spread symmetrically apart"}
            ],
            "quizzes": [
                {
                    "quiz_type": "sign_to_word",
                    "prompt_text": "Both flat palms pressed together in front of the chest — which ISL sign is this?",
                    "target_gesture": "NAMASTE",
                    "options": [
                        {"id": "a", "label": "Namaste"},
                        {"id": "b", "label": "Help"},
                        {"id": "c", "label": "Book"},
                        {"id": "d", "label": "Peace"}
                    ],
                    "correct_answer": "Namaste",
                    "explanation": "Namaste is performed with both palms pressed together (Anjali Mudra) at chest level.",
                    "points": 35
                },
                {
                    "quiz_type": "word_to_sign",
                    "prompt_text": "How do you sign 'BOOK' in ISL?",
                    "target_gesture": "BOOK",
                    "options": [
                        {"id": "a", "label": "Both palms together, then opening outward"},
                        {"id": "b", "label": "One hand flat, other hand chopping onto it"},
                        {"id": "c", "label": "Both fists tapping together"},
                        {"id": "d", "label": "Index finger tapping opposite wrist"}
                    ],
                    "correct_answer": "Both palms together, then opening outward",
                    "explanation": "BOOK in ISL mimics opening a book — both flat palms together, then opening outward.",
                    "points": 35
                },
                {
                    "quiz_type": "sign_to_word",
                    "prompt_text": "One flat palm horizontal, the other open hand descending perpendicularly onto it — what sign is this?",
                    "target_gesture": "STOP",
                    "options": [
                        {"id": "a", "label": "Work"},
                        {"id": "b", "label": "Time"},
                        {"id": "c", "label": "Stop"},
                        {"id": "d", "label": "Help"}
                    ],
                    "correct_answer": "Stop",
                    "explanation": "STOP uses a chopping motion — one hand descending onto the other flat palm.",
                    "points": 35
                }
            ]
        },
        {
            "title": "Module 6: Emergency & Essential Phrases",
            "category": "words",
            "level": "advanced",
            "order": 6,
            "xp_reward": 200,
            "description": "Critical emergency signs and essential ISL phrases for real-world communication situations.",
            "signs_data": [
                {"name": "HELP", "label": "Help (Emergency)", "meaning": "Urgent call for assistance", "tips": "Fist on flat palm, lifted urgently upward — perform with emphasis"},
                {"name": "STOP", "label": "Stop (Urgent)", "meaning": "Immediate halt command", "tips": "Quick chopping motion — dominant hand onto flat palm"},
                {"name": "WATER", "label": "Water (Need)", "meaning": "Basic need request", "tips": "Thumb to mouth, tilt gesture — repeat for emphasis"},
                {"name": "YES", "label": "Yes (Confirm)", "meaning": "Confirmation response", "tips": "Fist with thumb up, strong vertical nod"},
                {"name": "NO", "label": "No (Deny)", "meaning": "Denial response", "tips": "Index + middle finger snap — sharp and clear"}
            ],
            "quizzes": [
                {
                    "quiz_type": "word_to_sign",
                    "prompt_text": "In an emergency, how would you sign 'HELP' to get attention quickly?",
                    "target_gesture": "HELP",
                    "options": [
                        {"id": "a", "label": "Wave both hands in the air"},
                        {"id": "b", "label": "Fist on flat palm, both raised upward urgently"},
                        {"id": "c", "label": "Clap hands together"},
                        {"id": "d", "label": "Point to the sky"}
                    ],
                    "correct_answer": "Fist on flat palm, both raised upward urgently",
                    "explanation": "The emergency HELP sign is a fist placed on a flat palm, both lifted urgently upward.",
                    "points": 50
                },
                {
                    "quiz_type": "sign_to_word",
                    "prompt_text": "Quick quiz: Which of these signs uses BOTH hands?",
                    "target_gesture": "HELP",
                    "options": [
                        {"id": "a", "label": "Hello (one hand wave)"},
                        {"id": "b", "label": "Yes (fist nod)"},
                        {"id": "c", "label": "Help (fist on palm)"},
                        {"id": "d", "label": "Sorry (fist on chest)"}
                    ],
                    "correct_answer": "Help (fist on palm)",
                    "explanation": "HELP is a two-hand sign — fist on flat palm. Hello, Yes, and Sorry are all one-hand signs.",
                    "points": 40
                },
                {
                    "quiz_type": "camera_practice",
                    "prompt_text": "Show the 'NO' sign to the camera (Index + middle fingers snapping onto thumb).",
                    "target_gesture": "NO",
                    "options": [],
                    "correct_answer": "NO",
                    "explanation": "Extend your index and middle fingers, then snap them onto your thumb clearly.",
                    "points": 50
                }
            ]
        }
    ]

    for l_data in lessons_data:
        lesson = LearningLesson(
            title=l_data["title"],
            category=l_data["category"],
            level=l_data["level"],
            order=l_data["order"],
            xp_reward=l_data["xp_reward"],
            description=l_data["description"],
            signs_data=l_data["signs_data"]
        )
        db.add(lesson)
        db.flush()

        for q_data in l_data.get("quizzes", []):
            quiz = Quiz(
                lesson_id=lesson.id,
                quiz_type=q_data["quiz_type"],
                prompt_text=q_data["prompt_text"],
                target_gesture=q_data["target_gesture"],
                options=q_data.get("options", []),
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation", ""),
                points=q_data["points"]
            )
            db.add(quiz)

    # 5. Seed Saved Phrases
    phrases = [
        {"title": "Emergency Help", "text_en": "I need help right now", "text_hi": "मुझे अभी मदद चाहिए", "text_bn": "আমার এখনই সাহায্য দরকার", "category": "Emergency"},
        {"title": "Where is the Hospital", "text_en": "Where is the nearest hospital?", "text_hi": "निकटतम अस्पताल कहाँ है?", "text_bn": "নিকটতম হাসপাতাল কোথায়?", "category": "Medical"},
        {"title": "Thank You So Much", "text_en": "Thank you for your assistance", "text_hi": "आपकी सहायता के लिए धन्यवाद", "text_bn": "আপনার সাহায্যের জন্য ধন্যবাদ", "category": "Social"}
    ]
    for p in phrases:
        sp = SavedPhrase(
            user_id=demo_user.id,
            title=p["title"],
            text_en=p["text_en"],
            text_hi=p["text_hi"],
            text_bn=p["text_bn"],
            category=p["category"],
            sign_sequence=["HELP", "HOSPITAL", "THANK YOU"]
        )
        db.add(sp)

    db.commit()
    print("Database successfully seeded with ISL vocabulary, 6 lesson modules, quizzes, and demo user!")
