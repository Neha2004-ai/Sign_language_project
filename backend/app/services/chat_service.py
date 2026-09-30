import os
import re
import httpx
from typing import Dict, List, Any, Optional
from app.services.translation_service import translation_service
from app.core.config import settings

class ChatService:
    """
    Assistive communication chatbot engine.
    Supports both offline intelligent assistive matching and
    optional external LLM (OpenAI/Compatible) with bidirectional ISL token mapping.
    """

    INTENT_RESPONSES = [
        {
            "patterns": [r"\b(hi|hello|hey|namaste|greetings)\b"],
            "en": "Hello! I am your SignBridge AI assistant. I can translate your speech or text to Indian Sign Language (ISL) animations, or recognize your signs through the camera. How can I assist you?",
            "hi": "नमस्ते! मैं आपका साइनब्रिज AI सहायक हूँ। मैं आपकी बात को भारतीय सांकेतिक भाषा (ISL) में अनुवाद कर सकता हूँ। मैं आज आपकी क्या मदद कर सकता हूँ?",
            "bn": "হ্যালো! আমি আপনার সাইনব্রীজ AI সহকারী। আমি আপনার কথা ভারতীয় সাংকেতিক ভাষা (ISL) অ্যানিমেশনে অনুবাদ করতে পারি। আমি কীভাবে আপনাকে সাহায্য করতে পারি?"
        },
        {
            "patterns": [r"\b(who are you|what can you do|about you|help me with|what is signbridge)\b"],
            "en": "I am SignBridge AI, a bidirectional Indian Sign Language communication platform. I help deaf and non-signing users interact seamlessly using camera sign recognition, text-to-sign avatar animations, and multilingual voice output.",
            "hi": "मैं साइनब्रिज AI हूँ, एक भारतीय सांकेतिक भाषा संचार प्रणाली। मैं कैमरे से संकेत पहचान, टेक्स्ट-टू-साइन एनीमेशन और 3 भाषाओं में संवाद में मदद करता हूँ।",
            "bn": "আমি সাইনব্রীজ AI, একটি ভারতীয় সাংকেতিক ভাষা যোগাযোগ ব্যবস্থা। আমি ক্যামেরা দিয়ে চিহ্ন সনাক্তকরণ, অ্যানিমেশন এবং ৩টি ভাষায় অনুবাদ করতে সাহায্য করি।"
        },
        {
            "patterns": [r"\b(help|emergency|urgent|danger|save me|sos)\b"],
            "en": "I understand this is urgent! I am displaying the 'HELP' emergency gesture. Do you need a doctor, hospital, police, or ambulance? Please let me know immediately.",
            "hi": "मैं समझता हूँ कि यह जरूरी है! मैं आपातकालीन 'मदद' (HELP) संकेत प्रदर्शित कर रहा हूँ। क्या आपको डॉक्टर, अस्पताल या एम्बुलेंस की आवश्यकता है?",
            "bn": "আমি বুঝতে পারছি এটি জরুরি! আমি 'সাহায্য' (HELP) চিহ্ন দেখাচ্ছি। আপনার কি ডাক্তার, হাসপাতাল বা অ্যাম্বুলেন্স প্রয়োজন?"
        },
        {
            "patterns": [r"\b(doctor|hospital|medicine|pain|sick|ill|fever|ambulance|injury)\b"],
            "en": "Medical assistance is prioritized. I have mapped the emergency signs for HOSPITAL and DOCTOR. Please stay calm while I assist in communicating your symptoms.",
            "hi": "चिकित्सा सहायता प्राथमिकता पर है। मैंने अस्पताल और डॉक्टर के लिए आपातकालीन संकेत तैयार किए हैं।",
            "bn": "চিকিৎসা সহায়তা অগ্রাধিকার পাচ্ছে। আমি হাসপাতাল ও ডাক্তারের জরুরি চিহ্ন প্রস্তুত করেছি।"
        },
        {
            "patterns": [r"\b(thank you|thanks|grateful|dhanyavaad|shukriya)\b"],
            "en": "You are very welcome! I'm here 24/7 to make communication accessible for everyone.",
            "hi": "आपका बहुत-बहुत स्वागत है! मैं सभी के लिए संवाद को सुलभ बनाने के लिए यहाँ सदैव उपलब्ध हूँ।",
            "bn": "আপনাকে অনেক স্বাগতম! যোগাযোগ সহজ করতে আমি সর্বদা আপনার পাশে আছি।"
        },
        {
            "patterns": [r"\b(learn|study|practice|quiz|lessons|teach|course)\b"],
            "en": "You can start learning ISL right now! Go to the 'Learn ISL' section in the sidebar to practice alphabets, numbers 0-9, and common words with live camera quizzes. We have 6 modules from beginner to advanced!",
            "hi": "आप अभी ISL सीखना शुरू कर सकते हैं! वर्णमाला, ०-९ संख्याएँ और सामान्य शब्द सीखने के लिए 'Learn ISL' मेनू पर जाएँ। शुरुआती से उन्नत स्तर तक 6 मॉड्यूल उपलब्ध हैं!",
            "bn": "আপনি এখনই ISL শেখা শুরু করতে পারেন! বর্ণমালা এবং সাধারণ শব্দ শিখতে সাইডবারের 'Learn ISL' অপশনে যান। নতুন থেকে উন্নত পর্যায় পর্যন্ত ৬টি মডিউল আছে!"
        },
        {
            "patterns": [r"\b(how are you|how do you do|how r u)\b"],
            "en": "I am functioning smoothly and ready to translate your signs or words! How are you doing today?",
            "hi": "मैं बहुत अच्छा हूँ और आपके संकेतों या शब्दों का अनुवाद करने के लिए पूरी तरह तैयार हूँ! आप कैसे हैं?",
            "bn": "আমি খুব ভালো আছি এবং আপনার চিহ্ন বা শব্দ অনুবাদ করতে প্রস্তুত! আপনি কেমন আছেন?"
        },
        {
            "patterns": [r"\b(water|food|eat|drink|thirsty|hungry)\b"],
            "en": "Expressing basic needs: I am displaying the sign sequence for WATER and FOOD. These are essential ISL signs for daily communication.",
            "hi": "दैनिक आवश्यकताएँ: मैं पानी (WATER) और भोजन (FOOD) के लिए सांकेतिक क्रम प्रदर्शित कर रहा हूँ।",
            "bn": "নিত্যপ্রয়োজনীয় চাহিদা: আমি জল (WATER) এবং খাবারের (FOOD) জন্য সাংকেতিক অ্যানিমেশন দেখাচ্ছি।"
        },
        {
            "patterns": [r"\b(goodbye|bye|see you|alvida|tata)\b"],
            "en": "Goodbye! Have a wonderful day, and remember to keep practicing your ISL signs!",
            "hi": "अलविदा! आपका दिन शुभ हो, और अपने ISL संकेतों का अभ्यास जारी रखें!",
            "bn": "বিদায়! আপনার দিনটি শুভ হোক এবং ISL অনুশীলন চালিয়ে যান!"
        },
        # --- Additional intent patterns ---
        {
            "patterns": [r"\b(how.*(sign|say|express)|sign for|isl for)\b"],
            "en": "Great question! You can see how to sign any word by going to 'Text to Sign' in the sidebar. Type the word and I'll show you the ISL animation. You can also go to 'Learn ISL' for guided lessons.",
            "hi": "बढ़िया सवाल! किसी भी शब्द का संकेत देखने के लिए साइडबार में 'Text to Sign' पर जाएँ। शब्द टाइप करें और मैं ISL एनीमेशन दिखाऊँगा।",
            "bn": "দারুণ প্রশ্ন! যেকোনো শব্দের চিহ্ন দেখতে সাইডবারে 'Text to Sign'-এ যান। শব্দ টাইপ করুন এবং আমি ISL অ্যানিমেশন দেখাব।"
        },
        {
            "patterns": [r"\b(translate|translation|convert)\b"],
            "en": "I can translate between English, Hindi, and Bengali — and also convert any text into ISL sign animations! Use the 'Translator' page for text translation or 'Text to Sign' for ISL animations.",
            "hi": "मैं अंग्रेजी, हिंदी और बांग्ला के बीच अनुवाद कर सकता हूँ — और किसी भी टेक्स्ट को ISL संकेत एनीमेशन में भी बदल सकता हूँ! 'Translator' या 'Text to Sign' पेज का उपयोग करें।",
            "bn": "আমি ইংরেজি, হিন্দি এবং বাংলার মধ্যে অনুবাদ করতে পারি — এবং যেকোনো টেক্সটকে ISL চিহ্ন অ্যানিমেশনে রূপান্তর করতে পারি!"
        },
        {
            "patterns": [r"\b(camera|webcam|recognize|detection|detect)\b"],
            "en": "You can use your webcam for real-time sign recognition! Go to the 'Sign Translator' page, enable your camera, and start performing ISL signs. I'll recognize them and translate to text in English, Hindi, or Bengali.",
            "hi": "आप अपने वेबकैम से रियल-टाइम साइन पहचान कर सकते हैं! 'Sign Translator' पेज पर जाएँ, कैमरा चालू करें और ISL संकेत करना शुरू करें।",
            "bn": "আপনি আপনার ওয়েবক্যাম দিয়ে রিয়েল-টাইম চিহ্ন সনাক্তকরণ করতে পারেন! 'Sign Translator' পেজে যান, ক্যামেরা চালু করুন এবং ISL চিহ্ন করা শুরু করুন।"
        },
        {
            "patterns": [r"\b(number|count|one|two|three|four|five|zero|0|1|2|3|4|5)\b"],
            "en": "ISL numbers are done with one hand! For example: '1' is index finger up, '2' is a V-shape (index + middle), '5' is all fingers spread. Check the 'Numbers (0-5)' module in Learn ISL for guided practice!",
            "hi": "ISL संख्याएँ एक हाथ से की जाती हैं! उदाहरण: '1' तर्जनी ऊपर, '2' V-आकार, '5' सभी उंगलियाँ फैली। Learn ISL में 'Numbers (0-5)' मॉड्यूल देखें!",
            "bn": "ISL সংখ্যা এক হাতে করা হয়! উদাহরণ: '1' তর্জনী উপরে, '2' V-আকার, '5' সব আঙ্গুল ছড়ানো। Learn ISL-এ 'Numbers (0-5)' মডিউল দেখুন!"
        },
        {
            "patterns": [r"\b(alphabet|letter|fingerspell|spell|a-z)\b"],
            "en": "ISL fingerspelling uses specific hand shapes for each letter A-Z. You can learn them in the 'Alphabets' module under Learn ISL. I can also fingerspell any word — just type it in 'Text to Sign'!",
            "hi": "ISL फिंगरस्पेलिंग प्रत्येक अक्षर A-Z के लिए विशिष्ट हाथ के आकार का उपयोग करती है। Learn ISL में 'Alphabets' मॉड्यूल में सीखें!",
            "bn": "ISL ফিঙ্গারস্পেলিং প্রতিটি অক্ষর A-Z-এর জন্য নির্দিষ্ট হাতের আকার ব্যবহার করে। Learn ISL-এ 'Alphabets' মডিউলে শিখুন!"
        },
        {
            "patterns": [r"\b(namaste|namaskar|pranam)\b"],
            "en": "Namaste! The NAMASTE sign in ISL uses both hands pressed together (Anjali Mudra) in front of the chest. It's a universal greeting in Indian culture!",
            "hi": "नमस्ते! ISL में नमस्ते का संकेत दोनों हाथों को छाती के सामने जोड़कर (अंजलि मुद्रा) किया जाता है।",
            "bn": "নমস্কার! ISL-এ নমস্কার চিহ্নটি বুকের সামনে দুই হাত জোড়া করে (অঞ্জলি মুদ্রা) করা হয়।"
        },
        {
            "patterns": [r"\b(yes|haan|correct|right|sahi)\b"],
            "en": "The ISL sign for 'YES' is a closed fist with thumb up, nodding vertically — like a head nod with your hand!",
            "hi": "ISL में 'हाँ' का संकेत बंद मुट्ठी में अंगूठा ऊपर करके ऊर्ध्वाधर हिलाना है — जैसे हाथ से सिर हिलाना!",
            "bn": "'হ্যাঁ'-এর ISL চিহ্ন হলো বন্ধ মুষ্টিতে বুড়ো আঙ্গুল উপরে, উল্লম্বভাবে মাথা নাড়ানো — যেন হাত দিয়ে মাথা নাড়ছেন!"
        },
        {
            "patterns": [r"\b(no|nahi|nope|wrong|galat)\b"],
            "en": "The ISL sign for 'NO' is made by extending index and middle fingers and snapping them onto the thumb, or wagging side to side.",
            "hi": "ISL में 'नहीं' का संकेत तर्जनी और मध्यमा उंगली को अंगूठे पर स्नैप करके, या दाएं-बाएं हिलाकर किया जाता है।",
            "bn": "'না'-এর ISL চিহ্ন হলো তর্জনী ও মধ্যমা আঙ্গুল বুড়ো আঙ্গুলের উপর স্ন্যাপ করা, বা দুপাশে নাড়ানো।"
        },
        {
            "patterns": [r"\b(sorry|apologize|maaf|kshama)\b"],
            "en": "The ISL sign for 'SORRY' is a closed fist rubbing in a circular motion on the center of your chest. It expresses sincere apology.",
            "hi": "ISL में 'माफ़ कीजिए' का संकेत बंद मुट्ठी को छाती के बीच में गोल घुमाकर किया जाता है।",
            "bn": "'দুঃখিত'-এর ISL চিহ্ন হলো বন্ধ মুষ্টি বুকের মাঝখানে গোল করে ঘোরানো।"
        },
        {
            "patterns": [r"\b(love|pyar|pyaar|bhalobashi)\b"],
            "en": "The ISL sign for 'I LOVE YOU' uses one hand with thumb, index finger, and pinky extended while middle and ring fingers are curled. It's a beautiful universal gesture!",
            "hi": "ISL में 'I LOVE YOU' का संकेत एक हाथ से अंगूठा, तर्जनी और कनिष्ठिका उंगली फैलाकर किया जाता है, जबकि मध्यमा और अनामिका मुड़ी होती हैं।",
            "bn": "'আমি তোমাকে ভালোবাসি'-এর ISL চিহ্ন এক হাতে বুড়ো আঙ্গুল, তর্জনী এবং কনিষ্ঠা আঙ্গুল ছড়িয়ে করা হয়, মধ্যমা ও অনামিকা ভাঁজ করে।"
        },
        {
            "patterns": [r"\b(stop|ruko|thamo)\b"],
            "en": "The ISL sign for 'STOP' uses two hands — one flat palm horizontal, and the other open hand descends perpendicularly onto it, like a chopping motion.",
            "hi": "ISL में 'रुकिए' का संकेत दो हाथों से किया जाता है — एक सपाट हथेली क्षैतिज, दूसरा खुला हाथ लंबवत नीचे उतरता है।",
            "bn": "'থামুন'-এর ISL চিহ্ন দুই হাতে করা হয় — এক সমতল হাতের তালু অনুভূমিক, অন্য খোলা হাত লম্বভাবে নামানো হয়।"
        },
        {
            "patterns": [r"\b(what is isl|indian sign language|about isl|isl meaning)\b"],
            "en": "Indian Sign Language (ISL) is the primary sign language used in India by the deaf community. It has its own grammar and vocabulary distinct from spoken Hindi or English. ISL was officially recognized by the Indian government in 2024.",
            "hi": "भारतीय सांकेतिक भाषा (ISL) भारत में बधिर समुदाय द्वारा उपयोग की जाने वाली प्राथमिक सांकेतिक भाषा है। इसका अपना व्याकरण और शब्दावली है जो बोली जाने वाली हिंदी या अंग्रेजी से अलग है।",
            "bn": "ভারতীয় সাংকেতিক ভাষা (ISL) ভারতে বধির সম্প্রদায়ের ব্যবহৃত প্রাথমিক সাংকেতিক ভাষা। এর নিজস্ব ব্যাকরণ ও শব্দভাণ্ডার রয়েছে যা কথ্য হিন্দি বা ইংরেজি থেকে আলাদা।"
        },
        {
            "patterns": [r"\b(deaf|hearing impaired|hard of hearing|disability)\b"],
            "en": "SignBridge AI is designed to bridge the communication gap between deaf/hard-of-hearing individuals and hearing people. Our platform supports bidirectional translation — sign-to-text and text-to-sign — in 3 languages.",
            "hi": "साइनब्रिज AI बधिर/श्रवण बाधित व्यक्तियों और सुनने वाले लोगों के बीच संचार की खाई को पाटने के लिए डिज़ाइन किया गया है।",
            "bn": "সাইনব্রীজ AI বধির/শ্রবণ প্রতিবন্ধী ব্যক্তি এবং শ্রবণশক্তিসম্পন্ন মানুষের মধ্যে যোগাযোগের ব্যবধান দূর করতে তৈরি।"
        },
        {
            "patterns": [r"\b(custom|my own|create gesture|new sign|add sign)\b"],
            "en": "You can create your own custom gestures! Go to 'Custom Gestures' in the sidebar, name your gesture, record samples via webcam, and train the model. Your custom sign will then be recognized automatically.",
            "hi": "आप अपने खुद के कस्टम संकेत बना सकते हैं! साइडबार में 'Custom Gestures' पर जाएँ, अपने संकेत का नाम दें, वेबकैम से सैंपल रिकॉर्ड करें और मॉडल को प्रशिक्षित करें।",
            "bn": "আপনি আপনার নিজের কাস্টম চিহ্ন তৈরি করতে পারেন! সাইডবারে 'Custom Gestures'-এ যান, আপনার চিহ্নের নাম দিন, ওয়েবক্যাম দিয়ে নমুনা রেকর্ড করুন এবং মডেল প্রশিক্ষণ দিন।"
        },
        {
            "patterns": [r"\b(speech|voice|speak|talk|microphone|mic)\b"],
            "en": "You can use voice input! Go to 'Speech to Sign' in the sidebar, click the microphone button, speak your message, and I'll convert your speech into ISL sign animations in real-time.",
            "hi": "आप वॉइस इनपुट का उपयोग कर सकते हैं! साइडबार में 'Speech to Sign' पर जाएँ, माइक्रोफ़ोन बटन दबाएँ, अपना संदेश बोलें और मैं आपकी आवाज़ को ISL एनीमेशन में बदल दूँगा।",
            "bn": "আপনি ভয়েস ইনপুট ব্যবহার করতে পারেন! সাইডবারে 'Speech to Sign'-এ যান, মাইক্রোফোন বাটনে ক্লিক করুন, আপনার বার্তা বলুন এবং আমি আপনার কথাকে ISL অ্যানিমেশনে রূপান্তর করব।"
        },
    ]

    @classmethod
    def generate_response(cls, message: str, language: str = "en") -> Dict[str, Any]:
        clean = message.strip().lower()

        # 1. Try external LLM if API key is configured
        if settings.OPENAI_API_KEY:
            try:
                llm_reply = cls._query_external_llm(message, language)
                if llm_reply:
                    tokens, gestures, seq_desc = translation_service.text_to_isl_tokens(llm_reply, language)
                    return {
                        "text": llm_reply,
                        "language": language,
                        "sign_tokens": tokens,
                        "sign_sequence": gestures,
                        "sign_description": seq_desc
                    }
            except Exception as e:
                print("External LLM query exception:", e)

        # 2. Intelligent pattern & intent matcher
        matched_reply = None
        for intent in cls.INTENT_RESPONSES:
            for pattern in intent["patterns"]:
                if re.search(pattern, clean):
                    matched_reply = intent.get(language, intent["en"])
                    break
            if matched_reply:
                break

        # 3. Keyword extraction fallback — try to match individual words
        if not matched_reply:
            words = re.findall(r'\b\w+\b', clean)
            for word in words:
                for intent in cls.INTENT_RESPONSES:
                    for pattern in intent["patterns"]:
                        if re.search(pattern, word):
                            matched_reply = intent.get(language, intent["en"])
                            break
                    if matched_reply:
                        break
                if matched_reply:
                    break

        # 4. Conversational context-aware fallback
        if not matched_reply:
            if language == "hi":
                matched_reply = (
                    f"मुझे आपका संदेश प्राप्त हुआ: '{message}'। "
                    f"मैं इसका भारतीय सांकेतिक भाषा (ISL) एनीमेशन तैयार कर रहा हूँ। "
                    f"आप 'Learn ISL' में संकेत सीख सकते हैं, 'Text to Sign' में अनुवाद कर सकते हैं, "
                    f"या कैमरे से अपने संकेत पहचानवा सकते हैं!"
                )
            elif language == "bn":
                matched_reply = (
                    f"আমি আপনার বার্তা পেয়েছি: '{message}'। "
                    f"আমি এর জন্য ভারতীয় সাংকেতিক ভাষা (ISL) অ্যানিমেশন প্রস্তুত করছি। "
                    f"আপনি 'Learn ISL'-এ চিহ্ন শিখতে পারেন, 'Text to Sign'-এ অনুবাদ করতে পারেন, "
                    f"বা ক্যামেরা দিয়ে আপনার চিহ্ন চিনতে পারেন!"
                )
            else:
                matched_reply = (
                    f"I received your message: '{message}'. "
                    f"I'm preparing the ISL sign animation for this. "
                    f"You can also explore: 'Learn ISL' for guided lessons, "
                    f"'Text to Sign' for word-by-word animations, "
                    f"or use the camera for real-time sign recognition!"
                )

        # Generate ISL sequence tokens for the assistant reply
        try:
            tokens, gestures, seq_desc = translation_service.text_to_isl_tokens(matched_reply, language)
        except Exception:
            tokens = []
            gestures = []
            seq_desc = ""

        return {
            "text": matched_reply,
            "language": language,
            "sign_tokens": tokens,
            "sign_sequence": gestures,
            "sign_description": seq_desc
        }

    @classmethod
    def _query_external_llm(cls, user_text: str, language: str) -> Optional[str]:
        prompt = (
            f"You are SignBridge AI, a compassionate assistive communication companion for Indian Sign Language (ISL) users. "
            f"Respond concisely in 1-2 friendly, clear sentences in {language} language. User says: {user_text}"
        )
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": 0.7
        }
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        return None

chat_service = ChatService()
