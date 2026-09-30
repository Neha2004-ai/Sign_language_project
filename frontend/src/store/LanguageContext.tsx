import React, { createContext, useContext, useState, useEffect } from 'react';
import { Language } from '../types';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const translations: Record<Language, Record<string, string>> = {
  en: {
    brand_name: 'SignBridge AI',
    tagline: 'Breaking Communication Barriers with AI',
    start_translating: 'Start Translating',
    learn_isl: 'Learn ISL',
    sign_to_text: 'Sign → Text',
    text_to_sign: 'Text → Sign',
    speech_to_sign: 'Speech → Sign',
    chatbot: 'Assistive Chatbot',
    custom_gestures: 'Custom Gestures',
    analytics: 'Analytics & Insights',
    history: 'Translation History',
    settings: 'Settings',
    admin_model: 'Model Management',
    dashboard: 'Dashboard',
    streak: 'Day Streak',
    confidence: 'Confidence',
    high_confidence: 'High Confidence',
    medium_confidence: 'Medium Confidence',
    low_confidence: 'Low Confidence',
    reposition_hint: 'Please position your hand clearly within the camera frame.',
    webcam_start: 'Start Camera',
    webcam_pause: 'Pause',
    webcam_reset: 'Reset Stream',
    speak_audio: 'Play Voice',
    translating: 'Translating...',
  },
  hi: {
    brand_name: 'साइनब्रिज AI',
    tagline: 'AI के साथ संवाद की बाधाओं को तोड़ना',
    start_translating: 'अनुवाद शुरू करें',
    learn_isl: 'ISL सीखें',
    sign_to_text: 'सांकेतिक भाषा → पाठ',
    text_to_sign: 'पाठ → सांकेतिक भाषा',
    speech_to_sign: 'ध्वनि → सांकेतिक भाषा',
    chatbot: 'सहायक चैटबॉट',
    custom_gestures: 'कस्टम संकेत प्रशिक्षण',
    analytics: 'विश्लेषण और आँकड़े',
    history: 'अनुवाद इतिहास',
    settings: 'सेटिंग्स',
    admin_model: 'मॉडल प्रबंधन',
    dashboard: 'डैशबोर्ड',
    streak: 'दिनों का स्ट्रीक',
    confidence: 'सटीकता विश्वास',
    high_confidence: 'उच्च विश्वास',
    medium_confidence: 'मध्यम विश्वास',
    low_confidence: 'कम विश्वास',
    reposition_hint: 'कृपया अपने हाथ को कैमरे के सामने स्पष्ट रूप से रखें।',
    webcam_start: 'कैमरा चालू करें',
    webcam_pause: 'रोकें',
    webcam_reset: 'रीसेट करें',
    speak_audio: 'आवाज़ सुनें',
    translating: 'अनुवाद हो रहा है...',
  },
  bn: {
    brand_name: 'সাইনব্রীজ AI',
    tagline: 'AI এর সাহায্যে যোগাযোগের দূরত্ব দূরীকরণ',
    start_translating: 'অনুবাদ শুরু করুন',
    learn_isl: 'ISL শিখুন',
    sign_to_text: 'চিহ্ন ভাষা → টেক্সট',
    text_to_sign: 'টেক্সট → চিহ্ন ভাষা',
    speech_to_sign: 'কণ্ঠস্বর → চিহ্ন ভাষা',
    chatbot: 'সহায়ক চ্যাটবট',
    custom_gestures: 'কাস্টম অঙ্গভঙ্গি',
    analytics: 'বিশ্লেষণ ও পরিসংখ্যান',
    history: 'অনুবাদ ইতিহাস',
    settings: 'সেটিংস',
    admin_model: 'মডেল পরিচালনা',
    dashboard: 'ড্যাশবোর্ড',
    streak: 'দিনের ধারাবাহিকতা',
    confidence: 'নির্ভুলতা স্কোর',
    high_confidence: 'উচ্চ নির্ভরযোগ্যতা',
    medium_confidence: 'মাঝারি নির্ভরযোগ্যতা',
    low_confidence: 'কম নির্ভরযোগ্যতা',
    reposition_hint: 'দয়া করে ক্যামেরার ফ্রেমে হাতটি পরিষ্কারভাবে রাখুন।',
    webcam_start: 'ক্যামেরা চালু করুন',
    webcam_pause: 'থামান',
    webcam_reset: 'রিসেট করুন',
    speak_audio: 'শব্দ শুনুন',
    translating: 'অনুবাদ হচ্ছে...',
  }
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('signbridge_language');
    if (saved === 'en' || saved === 'hi' || saved === 'bn') return saved;
    return 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('signbridge_language', lang);
  };

  const t = (key: string): string => {
    return translations[language][key] || translations.en[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
