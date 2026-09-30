"""
Authentic Indian Sign Language (ISL) Vocabulary & Class Definitions.
Maps standard ISL signs (both 1-hand and 2-hand, static and dynamic)
to class indices, multilingual meanings (English, Hindi, Bengali),
and hand configuration requirements.
"""

from typing import Dict, Any, Optional

ISL_VOCABULARY: Dict[str, Dict[str, Any]] = {
    # --- Two-Hand ISL Signs ---
    "NAMASTE": {
        "id": 0,
        "name": "NAMASTE",
        "hands": "two_hand",
        "mode": "static",
        "text_en": "Namaste / Greetings",
        "text_hi": "नमस्ते / नमस्कार",
        "text_bn": "নমস্কার / প্রণতি",
        "category": "greeting",
        "description": "Both flat hands pressed together palms touching in front of chest (Anjali Mudra)."
    },
    "HELP": {
        "id": 1,
        "name": "HELP",
        "hands": "two_hand",
        "mode": "dynamic",
        "text_en": "I Need Help",
        "text_hi": "मुझे मदद चाहिए",
        "text_bn": "আমার সাহায্য প্রয়োজন",
        "category": "emergency",
        "description": "Non-dominant flat palm facing upward; dominant fist/thumb placed on top, both lifted upward together."
    },
    "BOOK": {
        "id": 2,
        "name": "BOOK",
        "hands": "two_hand",
        "mode": "dynamic",
        "text_en": "Book / Reading",
        "text_hi": "किताब / पुस्तक",
        "text_bn": "বই / পুস্তক",
        "category": "education",
        "description": "Both flat palms touching together, then opening outward like opening the pages of a book."
    },
    "HOUSE": {
        "id": 3,
        "name": "HOUSE",
        "hands": "two_hand",
        "mode": "static",
        "text_en": "House / Home",
        "text_hi": "घर / मकान",
        "text_bn": "বাড়ি / ঘর",
        "category": "places",
        "description": "Fingertips of both flat hands touching at an angle forming a roof / inverted V apex."
    },
    "TIME": {
        "id": 4,
        "name": "TIME",
        "hands": "two_hand",
        "mode": "dynamic",
        "text_en": "Time / Clock",
        "text_hi": "समय / वक्त",
        "text_bn": "সময় / ঘড়ি",
        "category": "common",
        "description": "Non-dominant hand held horizontally at wrist, dominant index finger taps non-dominant wrist twice."
    },
    "STOP": {
        "id": 5,
        "name": "STOP",
        "hands": "two_hand",
        "mode": "dynamic",
        "text_en": "Stop / Halt",
        "text_hi": "रुकिए / बंद करो",
        "text_bn": "থামুন / বন্ধ করুন",
        "category": "command",
        "description": "Non-dominant hand flat horizontal palm up; dominant open hand descends down perpendicularly onto the palm."
    },
    "WORK": {
        "id": 6,
        "name": "WORK",
        "hands": "two_hand",
        "mode": "dynamic",
        "text_en": "Work / Job",
        "text_hi": "काम / नौकरी",
        "text_bn": "কাজ / চাকরী",
        "category": "common",
        "description": "Both hands in loose fists, dominant wrist taps the back or heel of non-dominant wrist repeatedly."
    },
    "PEACE": {
        "id": 7,
        "name": "PEACE",
        "hands": "two_hand",
        "mode": "static",
        "text_en": "Peace / Harmony",
        "text_hi": "शांति",
        "text_bn": "শান্তি",
        "category": "concept",
        "description": "Both hands showing V-sign / palms spread symmetrically moving gently outward."
    },

    # --- One-Hand ISL Signs ---
    "HELLO": {
        "id": 8,
        "name": "HELLO",
        "hands": "one_hand",
        "mode": "dynamic",
        "text_en": "Hello",
        "text_hi": "हैलो / नमस्ते",
        "text_bn": "হ্যালো / নমস্কার",
        "category": "greeting",
        "description": "Open dominant hand waving outward near temple or forehead in a respectful salute wave."
    },
    "THANK YOU": {
        "id": 9,
        "name": "THANK YOU",
        "hands": "one_hand",
        "mode": "dynamic",
        "text_en": "Thank You",
        "text_hi": "धन्यवाद / शुक्रिया",
        "text_bn": "ধন্যবাদ",
        "category": "polite",
        "description": "Flat dominant hand moves from chin/lips forward and outward towards the listener."
    },
    "YES": {
        "id": 10,
        "name": "YES",
        "hands": "one_hand",
        "mode": "dynamic",
        "text_en": "Yes",
        "text_hi": "हाँ / सही",
        "text_bn": "হ্যাঁ / ঠিক",
        "category": "response",
        "description": "Closed fist with thumb upright or nodding vertically like a head nod."
    },
    "NO": {
        "id": 11,
        "name": "NO",
        "hands": "one_hand",
        "mode": "dynamic",
        "text_en": "No",
        "text_hi": "नहीं / ना",
        "text_bn": "না / নয়",
        "category": "response",
        "description": "Extended index and middle fingers snapping together against thumb, or shaking side to side."
    },
    "SORRY": {
        "id": 12,
        "name": "SORRY",
        "hands": "one_hand",
        "mode": "dynamic",
        "text_en": "Sorry / Apologies",
        "text_hi": "माफ़ कीजिये",
        "text_bn": "দুঃখিত / ক্ষমা করবেন",
        "category": "polite",
        "description": "Closed fist rubbing in a circular motion on the chest."
    },
    "PLEASE": {
        "id": 13,
        "name": "PLEASE",
        "hands": "one_hand",
        "mode": "dynamic",
        "text_en": "Please",
        "text_hi": "कृपया",
        "text_bn": "দয়া করে",
        "category": "polite",
        "description": "Flat open palm resting or rubbing softly on chest in circular motion."
    },
    "WATER": {
        "id": 14,
        "name": "WATER",
        "hands": "one_hand",
        "mode": "dynamic",
        "text_en": "Water",
        "text_hi": "पानी / जल",
        "text_bn": "জল / পানি",
        "category": "needs",
        "description": "W-handshape or thumb near mouth tilted slightly mimicking drinking water."
    },
    "I LOVE YOU": {
        "id": 15,
        "name": "I LOVE YOU",
        "hands": "one_hand",
        "mode": "static",
        "text_en": "I Love You",
        "text_hi": "मैं आपसे प्यार करता हूँ",
        "text_bn": "আমি তোমাকে ভালোবাসি",
        "category": "phrase",
        "description": "Thumb, index, and pinky fingers extended; middle and ring fingers curled."
    },
    "OK": {
        "id": 16,
        "name": "OK",
        "hands": "one_hand",
        "mode": "static",
        "text_en": "OK / Understood",
        "text_hi": "ठीक है / समझ गया",
        "text_bn": "ঠিক আছে / বুঝেছি",
        "category": "response",
        "description": "Thumb and index tips touching to form a circle with middle, ring, pinky extended."
    },
    "1": {
        "id": 17,
        "name": "1",
        "hands": "one_hand",
        "mode": "static",
        "text_en": "One (1)",
        "text_hi": "एक (१)",
        "text_bn": "এক (১)",
        "category": "number",
        "description": "Index finger extended vertically, all other fingers curled into palm."
    },
    "2": {
        "id": 18,
        "name": "2",
        "hands": "one_hand",
        "mode": "static",
        "text_en": "Two (2)",
        "text_hi": "दो (२)",
        "text_bn": "দুই (২)",
        "category": "number",
        "description": "Index and middle fingers extended in a V-shape, others curled."
    },
    "3": {
        "id": 19,
        "name": "3",
        "hands": "one_hand",
        "mode": "static",
        "text_en": "Three (3)",
        "text_hi": "तीन (३)",
        "text_bn": "তিন (৩)",
        "category": "number",
        "description": "Thumb, index, and middle fingers extended, ring and pinky curled."
    },
    "4": {
        "id": 20,
        "name": "4",
        "hands": "one_hand",
        "mode": "static",
        "text_en": "Four (4)",
        "text_hi": "चार (४)",
        "text_bn": "চার (৪)",
        "category": "number",
        "description": "Four fingers (index, middle, ring, pinky) extended vertically, thumb curled across palm."
    },
    "5": {
        "id": 21,
        "name": "5",
        "hands": "one_hand",
        "mode": "static",
        "text_en": "Five (5)",
        "text_hi": "पाँच (५)",
        "text_bn": "পাঁচ (৫)",
        "category": "number",
        "description": "All five fingers fully extended and spread out."
    },

    # --- Alphabet Signs (A - Z) ---
    "A": {"id": 22, "name": "A", "hands": "one_hand", "mode": "static", "text_en": "Letter A", "text_hi": "अक्षर A (ए)", "text_bn": "বর্ণ A (এ)", "category": "alphabet", "description": "Fist with thumb resting along the side of the index finger."},
    "B": {"id": 23, "name": "B", "hands": "one_hand", "mode": "static", "text_en": "Letter B", "text_hi": "अक्षर B (बी)", "text_bn": "বর্ণ B (বি)", "category": "alphabet", "description": "Flat open hand with four fingers straight up and thumb folded across palm."},
    "C": {"id": 24, "name": "C", "hands": "one_hand", "mode": "static", "text_en": "Letter C", "text_hi": "अक्षर C (सी)", "text_bn": "বর্ণ C (সি)", "category": "alphabet", "description": "Hand curved into a C-shape like holding a small cup."},
    "D": {"id": 25, "name": "D", "hands": "one_hand", "mode": "static", "text_en": "Letter D", "text_hi": "अक्षर D (डी)", "text_bn": "বর্ণ D (ডি)", "category": "alphabet", "description": "Index finger pointing up, thumb and remaining fingers touching to form an O."},
    "E": {"id": 26, "name": "E", "hands": "one_hand", "mode": "static", "text_en": "Letter E", "text_hi": "अक्षर E (ई)", "text_bn": "বর্ণ E (ই)", "category": "alphabet", "description": "All four fingers curled down touching the thumb folded below."},
    "F": {"id": 27, "name": "F", "hands": "one_hand", "mode": "static", "text_en": "Letter F", "text_hi": "अक्षर F (एफ़)", "text_bn": "বর্ণ F (এফ)", "category": "alphabet", "description": "Index finger and thumb touching tips forming a circle, other 3 fingers extended."},
    "G": {"id": 28, "name": "G", "hands": "one_hand", "mode": "static", "text_en": "Letter G", "text_hi": "अक्षर G (जी)", "text_bn": "বর্ণ G (জি)", "category": "alphabet", "description": "Index and thumb extended horizontally parallel like pointing sideways."},
    "H": {"id": 29, "name": "H", "hands": "one_hand", "mode": "static", "text_en": "Letter H", "text_hi": "अक्षर H (एच)", "text_bn": "বর্ণ H (এইচ)", "category": "alphabet", "description": "Index and middle fingers extended together horizontally."},
    "I": {"id": 30, "name": "I", "hands": "one_hand", "mode": "static", "text_en": "Letter I", "text_hi": "अक्षर I (आई)", "text_bn": "বর্ণ I (আই)", "category": "alphabet", "description": "Pinky finger extended vertically, all other fingers closed in a fist."},
    "J": {"id": 31, "name": "J", "hands": "one_hand", "mode": "static", "text_en": "Letter J", "text_hi": "अक्षर J (जे)", "text_bn": "বর্ণ J (জে)", "category": "alphabet", "description": "Pinky finger extended tracing a J-curve in the air."},
    "K": {"id": 32, "name": "K", "hands": "one_hand", "mode": "static", "text_en": "Letter K", "text_hi": "अक्षर K (के)", "text_bn": "বর্ণ K (কে)", "category": "alphabet", "description": "Index finger up, middle finger angled forward, thumb tucked between them."},
    "L": {"id": 33, "name": "L", "hands": "one_hand", "mode": "static", "text_en": "Letter L", "text_hi": "अक्षर L (एल)", "text_bn": "বর্ণ L (এল)", "category": "alphabet", "description": "Thumb and index finger held perpendicular forming an L shape."},
    "M": {"id": 34, "name": "M", "hands": "one_hand", "mode": "static", "text_en": "Letter M", "text_hi": "अक्षर M (एम)", "text_bn": "বর্ণ M (এম)", "category": "alphabet", "description": "Three fingers (index, middle, ring) folded over thumb pointing down."},
    "N": {"id": 35, "name": "N", "hands": "one_hand", "mode": "static", "text_en": "Letter N", "text_hi": "अक्षर N (एन)", "text_bn": "বর্ণ N (এন)", "category": "alphabet", "description": "Two fingers (index, middle) folded over thumb pointing down."},
    "O": {"id": 36, "name": "O", "hands": "one_hand", "mode": "static", "text_en": "Letter O", "text_hi": "अक्षर O (ओ)", "text_bn": "বর্ণ O (ও)", "category": "alphabet", "description": "All fingertips touch the thumb forming an O shape."},
    "P": {"id": 37, "name": "P", "hands": "one_hand", "mode": "static", "text_en": "Letter P", "text_hi": "अक्षर P (पी)", "text_bn": "বর্ণ P (পি)", "category": "alphabet", "description": "K-handshape pointing downward."},
    "Q": {"id": 38, "name": "Q", "hands": "one_hand", "mode": "static", "text_en": "Letter Q", "text_hi": "अक्षर Q (क्यू)", "text_bn": "বর্ণ Q (কিউ)", "category": "alphabet", "description": "G-handshape pointing downward towards ground."},
    "R": {"id": 39, "name": "R", "hands": "one_hand", "mode": "static", "text_en": "Letter R", "text_hi": "अक्षर R (आर)", "text_bn": "বর্ণ R (আর)", "category": "alphabet", "description": "Index and middle fingers crossed over each other."},
    "S": {"id": 40, "name": "S", "hands": "one_hand", "mode": "static", "text_en": "Letter S", "text_hi": "अक्षर S (एस)", "text_bn": "বর্ণ S (এস)", "category": "alphabet", "description": "Fist with thumb wrapped tightly across the front of fingers."},
    "T": {"id": 41, "name": "T", "hands": "one_hand", "mode": "static", "text_en": "Letter T", "text_hi": "अक्षर T (टी)", "text_bn": "বর্ণ T (টি)", "category": "alphabet", "description": "Thumb tucked between index and middle fingers of a fist."},
    "U": {"id": 42, "name": "U", "hands": "one_hand", "mode": "static", "text_en": "Letter U", "text_hi": "अक्षर U (यू)", "text_bn": "বর্ণ U (ইউ)", "category": "alphabet", "description": "Index and middle fingers held together straight up."},
    "V": {"id": 43, "name": "V", "hands": "one_hand", "mode": "static", "text_en": "Letter V", "text_hi": "अक्षर V (वी)", "text_bn": "বর্ণ V (ভি)", "category": "alphabet", "description": "Index and middle fingers held spread in a V shape."},
    "W": {"id": 44, "name": "W", "hands": "one_hand", "mode": "static", "text_en": "Letter W", "text_hi": "अक्षर W (डब्ल्यू)", "text_bn": "বর্ণ W (ডব্লিউ)", "category": "alphabet", "description": "Three middle fingers (index, middle, ring) held upright in W shape."},
    "X": {"id": 45, "name": "X", "hands": "one_hand", "mode": "static", "text_en": "Letter X", "text_hi": "अक्षर X (एक्स)", "text_bn": "বর্ণ X (এক্স)", "category": "alphabet", "description": "Index finger curled into a hook, others closed into a fist."},
    "Y": {"id": 46, "name": "Y", "hands": "one_hand", "mode": "static", "text_en": "Letter Y", "text_hi": "अक्षर Y (वाई)", "text_bn": "বর্ণ Y (ওয়াই)", "category": "alphabet", "description": "Thumb and pinky extended out (shaka hand), middle three folded."},
    "Z": {"id": 47, "name": "Z", "hands": "one_hand", "mode": "static", "text_en": "Letter Z", "text_hi": "अक्षर Z (ज़ेड)", "text_bn": "বর্ণ Z (জেড)", "category": "alphabet", "description": "Index finger extended tracing a Z in the air."}
}

# Explicit Unknown / Unrecognized Sign Representation
UNKNOWN_SIGN = {
    "name": "UNKNOWN_GESTURE",
    "text_en": "Sign not confidently recognized",
    "text_hi": "संकेत पहचाना नहीं गया",
    "text_bn": "চিহ্নটি শনাক্ত করা যায়নি",
    "status": "low_confidence",
    "description": "Hand gesture does not match supported ISL vocabulary or confidence is below threshold."
}

NO_HAND_SIGN = {
    "name": "NO_HAND",
    "text_en": "No hand detected",
    "text_hi": "कोई हाथ नहीं मिला",
    "text_bn": "কোন হাত সনাক্ত হয়নি",
    "status": "no_hand",
    "description": "No hands detected in webcam frame."
}

CONFIDENCE_THRESHOLD = 0.70

def get_isl_metadata(sign_name: str) -> Optional[Dict[str, Any]]:
    return ISL_VOCABULARY.get(sign_name)
