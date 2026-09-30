import re
from typing import Dict, List, Any, Tuple, Optional

class TranslationService:
    """
    Multilingual bidirectional translation service supporting
    English, Hindi, and Bengali with semantic ISL gloss/token mapping.
    """
    
    # Core multilingual dictionary with semantic concepts
    DICTIONARY: Dict[str, Dict[str, str]] = {
        "hello": {"en": "Hello", "hi": "नमस्ते", "bn": "হ্যালো", "isl": "HELLO"},
        "hi": {"en": "Hello", "hi": "नमस्ते", "bn": "হ্যালো", "isl": "HELLO"},
        "namaste": {"en": "Hello", "hi": "नमस्ते", "bn": "নমস্কার", "isl": "HELLO"},
        "thank you": {"en": "Thank You", "hi": "धन्यवाद", "bn": "ধন্যবাদ", "isl": "THANK YOU"},
        "thanks": {"en": "Thank You", "hi": "धन्यवाद", "bn": "ধন্যবাদ", "isl": "THANK YOU"},
        "dhanyavaad": {"en": "Thank You", "hi": "धन्यवाद", "bn": "ধন্যবাদ", "isl": "THANK YOU"},
        "yes": {"en": "Yes", "hi": "हाँ", "bn": "হ্যাঁ", "isl": "YES"},
        "haan": {"en": "Yes", "hi": "हाँ", "bn": "হ্যাঁ", "isl": "YES"},
        "no": {"en": "No", "hi": "नहीं", "bn": "না", "isl": "NO"},
        "nahi": {"en": "No", "hi": "नहीं", "bn": "না", "isl": "NO"},
        "help": {"en": "I need help", "hi": "मुझे मदद चाहिए", "bn": "আমার সাহায্য দরকার", "isl": "HELP"},
        "i need help": {"en": "I need help", "hi": "मुझे मदद चाहिए", "bn": "আমার সাহায্য দরকার", "isl": "HELP"},
        "madad": {"en": "Help", "hi": "मदद", "bn": "সাহায্য", "isl": "HELP"},
        "goodbye": {"en": "Goodbye", "hi": "अलविदा", "bn": "বিদায়", "isl": "GOODBYE"},
        "bye": {"en": "Goodbye", "hi": "अलविदा", "bn": "বিদায়", "isl": "GOODBYE"},
        "please": {"en": "Please", "hi": "कृपया", "bn": "দয়া করে", "isl": "PLEASE"},
        "kripya": {"en": "Please", "hi": "कृपया", "bn": "দয়া করে", "isl": "PLEASE"},
        "sorry": {"en": "Sorry", "hi": "माफ़ कीजिये", "bn": "দুঃখিত", "isl": "SORRY"},
        "maaf": {"en": "Sorry", "hi": "माफ़ कीजिये", "bn": "দুঃখিত", "isl": "SORRY"},
        "i love you": {"en": "I love you", "hi": "मैं आपसे प्यार करता हूँ", "bn": "আমি তোমাকে ভালোবাসি", "isl": "I LOVE YOU"},
        "hospital": {"en": "Hospital", "hi": "अस्पताल", "bn": "হাসপাতাল", "isl": "HOSPITAL"},
        "water": {"en": "Water", "hi": "पानी", "bn": "জল", "isl": "WATER"},
        "food": {"en": "Food", "hi": "खाना", "bn": "খাবার", "isl": "FOOD"},
        "doctor": {"en": "Doctor", "hi": "डॉक्टर", "bn": "ডাক্তার", "isl": "DOCTOR"},
        "where": {"en": "Where", "hi": "कहाँ", "bn": "কোথায়", "isl": "WHERE"},
        "how": {"en": "How are you?", "hi": "आप कैसे हैं?", "bn": "আপনি কেমন আছেন?", "isl": "HOW"},
        "good": {"en": "Good", "hi": "अच्छा", "bn": "ভালো", "isl": "GOOD"},
        "ok": {"en": "OK", "hi": "ठीक है", "bn": "ঠিক আছে", "isl": "OK"}
    }

    # Hindi to English keyword direct mapping
    HI_MAP = {
        "नमस्ते": "hello", "हैलो": "hello", "धन्यवाद": "thank you", "शुक्रिया": "thank you",
        "हाँ": "yes", "हां": "yes", "नहीं": "no", "ना": "no", "मदद": "help",
        "मुझे मदद चाहिए": "help", "अलविदा": "goodbye", "कृपया": "please",
        "माफ़": "sorry", "माफ": "sorry", "प्यार": "i love you", "पानी": "water",
        "खाना": "food", "अस्पताल": "hospital", "डॉक्टर": "doctor", "कहाँ": "where",
        "कैसा": "how", "अच्छा": "good", "ठीक": "ok"
    }

    # Bengali to English keyword direct mapping
    BN_MAP = {
        "নমস্কার": "hello", "হ্যালো": "hello", "ধন্যবাদ": "thank you",
        "হ্যাঁ": "yes", "না": "no", "সাহায্য": "help", "আমার সাহায্য দরকার": "help",
        "বিদায়": "goodbye", "দয়া করে": "please", "দুঃখিত": "sorry",
        "ভালোবাসি": "i love you", "জল": "water", "পানি": "water",
        "খাবার": "food", "হাসপাতাল": "hospital", "ডাক্তার": "doctor",
        "কোথায়": "where", "কেমন": "how", "ভালো": "good", "ঠিক": "ok"
    }

    @classmethod
    def detect_language(cls, text: str) -> str:
        """Simple script-based language detection for EN, HI, BN."""
        for ch in text:
            # Devanagari range for Hindi
            if '\u0900' <= ch <= '\u097F':
                return "hi"
            # Bengali range
            if '\u0980' <= ch <= '\u09FF':
                return "bn"
        return "en"

    @classmethod
    def translate_text(cls, text: str, source_lang: str, target_lang: str) -> str:
        """Translates text between English, Hindi, and Bengali."""
        clean = text.strip().lower()
        if source_lang == target_lang:
            return text

        # 1. Direct semantic lookup
        canonical_key = None
        if source_lang == "hi":
            for hi_word, eng_key in cls.HI_MAP.items():
                if hi_word in text:
                    canonical_key = eng_key
                    break
        elif source_lang == "bn":
            for bn_word, eng_key in cls.BN_MAP.items():
                if bn_word in text:
                    canonical_key = eng_key
                    break
        else:
            for dict_key in cls.DICTIONARY.keys():
                if dict_key in clean:
                    canonical_key = dict_key
                    break

        if canonical_key and canonical_key in cls.DICTIONARY:
            return cls.DICTIONARY[canonical_key].get(target_lang, text)

        # Fallback word-by-word mapping or pass-through
        return text

    @classmethod
    def text_to_isl_tokens(cls, text: str, lang: Optional[str] = None) -> Tuple[List[str], List[Dict[str, Any]], str]:
        """
        Converts natural language sentence (EN/HI/BN) to normalized ISL tokens
        and gesture sequence items for the SignRenderer.
        """
        detected = lang or cls.detect_language(text)
        clean = text.strip().lower()
        
        # Check phrase match first
        matched_isl = None
        if detected == "hi":
            for k, v in cls.HI_MAP.items():
                if k in text:
                    matched_isl = cls.DICTIONARY.get(v, {}).get("isl")
                    break
        elif detected == "bn":
            for k, v in cls.BN_MAP.items():
                if k in text:
                    matched_isl = cls.DICTIONARY.get(v, {}).get("isl")
                    break
        else:
            for k in sorted(cls.DICTIONARY.keys(), key=len, reverse=True):
                if k in clean:
                    matched_isl = cls.DICTIONARY[k].get("isl")
                    break

        tokens: List[str] = []
        gestures: List[Dict[str, Any]] = []

        if matched_isl:
            tokens.append(matched_isl)
            gestures.append({
                "token": matched_isl,
                "type": "word",
                "label": matched_isl,
                "duration_ms": 1500,
                "description": f"Standard ISL Sign for '{matched_isl}'"
            })
            seq_desc = f"Performing ISL gesture for {matched_isl}"
        else:
            # Tokenize words or fingerspell
            words = re.findall(r'\b\w+\b', clean.upper())
            for w in words:
                if w.lower() in cls.DICTIONARY:
                    isl_name = cls.DICTIONARY[w.lower()]["isl"]
                    tokens.append(isl_name)
                    gestures.append({
                        "token": isl_name,
                        "type": "word",
                        "label": isl_name,
                        "duration_ms": 1200,
                        "description": f"ISL Sign '{isl_name}'"
                    })
                else:
                    # Fingerspell letters
                    for letter in w:
                        if letter.isalpha() or letter.isdigit():
                            tokens.append(letter)
                            gestures.append({
                                "token": letter,
                                "type": "fingerspell",
                                "label": letter,
                                "duration_ms": 800,
                                "description": f"ISL Fingerspelling '{letter}'"
                            })
            seq_desc = f"Fingerspelling and ISL tokens: {' → '.join(tokens[:8])}"

        return tokens, gestures, seq_desc

translation_service = TranslationService()
