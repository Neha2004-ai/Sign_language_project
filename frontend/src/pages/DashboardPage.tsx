import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Video,
  Type,
  Mic,
  Flame,
  Award,
  Zap,
  BookOpen,
  ArrowRight,
  Sparkles,
  Volume2,
  Clock,
  Bookmark,
  CheckCircle2
} from 'lucide-react';
import { useAuth } from '../store/AuthContext';
import { useLanguage } from '../store/LanguageContext';
import { api } from '../services/api';
import { UserProgress, TranslationRecord } from '../types';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const { speak } = useSpeechSynthesis();

  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [history, setHistory] = useState<TranslationRecord[]>([]);
  const [quickText, setQuickText] = useState('');
  const [quickResult, setQuickResult] = useState<string | null>(null);
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    api.getUserProgress().then(setProgress).catch(console.error);
    api.getHistory(5).then(setHistory).catch(console.error);
  }, []);

  const handleQuickTranslate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickText.trim()) return;
    setIsTranslating(true);
    try {
      const res = await api.textToSign(quickText);
      setQuickResult(res.isl_tokens.join(' → '));
    } catch (err) {
      console.error(err);
    } finally {
      setIsTranslating(false);
    }
  };

  const savedPhrases = [
    { title: 'Emergency Help', text: 'I need help right now', isl: 'HELP', lang: 'en' as const },
    { title: 'Where is Doctor', text: 'Where is the doctor?', isl: 'DOCTOR → WHERE', lang: 'en' as const },
    { title: 'Thank You', text: 'Thank you very much', isl: 'THANK YOU', lang: 'en' as const },
    { title: 'Water Please', text: 'Water please', isl: 'WATER → PLEASE', lang: 'en' as const }
  ];

  return (
    <div className="space-y-8">
      {/* 1. WELCOME BANNER */}
      <div className="glass-panel p-6 sm:p-8 bg-gradient-to-r from-brand-600/15 via-primary-600/10 to-transparent border-brand-500/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
              Welcome back, {user?.full_name || 'Alex'}! 👋
            </h1>
            {user?.is_guest && (
              <span className="px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-600 dark:text-amber-400 font-bold text-xs">
                Demo Mode
              </span>
            )}
          </div>
          <p className="text-sm text-slate-600 dark:text-slate-400 max-w-xl">
            SignBridge AI is active and ready for real-time bidirectional ISL communication, audio translation, and gesture learning.
          </p>
        </div>

        {/* Gamified Streak & XP Widget */}
        <div className="flex items-center gap-4 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm shrink-0">
          <div className="flex items-center gap-2 pr-3 border-r border-slate-200 dark:border-slate-800">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-500">
              <Flame className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase">Streak</div>
              <div className="text-lg font-black text-slate-900 dark:text-white">{progress?.current_streak || 7} Days</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-brand-500/10 flex items-center justify-center text-brand-500">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase">Total XP</div>
              <div className="text-lg font-black text-slate-900 dark:text-white">{progress?.total_xp || 1420}</div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. CORE ACTION SHORTCUTS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Sign Translator */}
        <Link
          to="/translator"
          className="glass-card p-6 group hover:border-brand-500 transition-all space-y-3 relative overflow-hidden"
        >
          <div className="w-12 h-12 rounded-2xl bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center justify-center group-hover:scale-110 transition-transform">
            <Video className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center justify-between">
            Sign → Text & Speech
            <ArrowRight className="w-4 h-4 text-brand-500 opacity-0 group-hover:opacity-100 transition-opacity" />
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            Live webcam ISL gesture recognition with 21 MediaPipe skeletal overlay and instant audio playback.
          </p>
        </Link>

        {/* Text to Sign */}
        <Link
          to="/text-to-sign"
          className="glass-card p-6 group hover:border-primary-500 transition-all space-y-3 relative overflow-hidden"
        >
          <div className="w-12 h-12 rounded-2xl bg-primary-500/10 text-primary-600 dark:text-primary-400 flex items-center justify-center group-hover:scale-110 transition-transform">
            <Type className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center justify-between">
            Text → Sign Language
            <ArrowRight className="w-4 h-4 text-primary-500 opacity-0 group-hover:opacity-100 transition-opacity" />
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            Translate English, Hindi, or Bengali text into animated ISL avatar gestures and fingerspelling.
          </p>
        </Link>

        {/* Speech to Sign */}
        <Link
          to="/speech-to-sign"
          className="glass-card p-6 group hover:border-teal-500 transition-all space-y-3 relative overflow-hidden"
        >
          <div className="w-12 h-12 rounded-2xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center group-hover:scale-110 transition-transform">
            <Mic className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center justify-between">
            Speech → Sign Language
            <ArrowRight className="w-4 h-4 text-teal-500 opacity-0 group-hover:opacity-100 transition-opacity" />
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            Speak into the microphone in real-time to generate instant sign sequences and visual glosses.
          </p>
        </Link>
      </div>

      {/* 3. QUICK TRANSLATOR & SAVED PHRASES ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Quick Text-to-Sign Converter */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-500" />
              Quick ISL Tokenizer
            </h3>
            <span className="text-xs text-slate-400">EN / HI / BN</span>
          </div>

          <form onSubmit={handleQuickTranslate} className="space-y-3">
            <div className="relative">
              <input
                type="text"
                value={quickText}
                onChange={(e) => setQuickText(e.target.value)}
                placeholder="Type a sentence (e.g. 'Thank you' or 'नमस्ते')..."
                className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-900 dark:text-slate-100"
              />
              <button
                type="submit"
                disabled={isTranslating || !quickText.trim()}
                className="absolute right-2 top-2 px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold transition-colors disabled:opacity-50"
              >
                {isTranslating ? 'Mapping...' : 'Convert'}
              </button>
            </div>
          </form>

          {quickResult && (
            <div className="p-3.5 rounded-xl bg-brand-50 dark:bg-brand-950/40 border border-brand-200 dark:border-brand-800/60 flex items-center justify-between">
              <div>
                <span className="text-[10px] uppercase font-bold text-brand-600 dark:text-brand-400">Mapped ISL Signs:</span>
                <div className="text-sm font-black text-slate-800 dark:text-slate-100">{quickResult}</div>
              </div>
              <Link
                to={`/text-to-sign?query=${encodeURIComponent(quickText)}`}
                className="px-3 py-1 bg-brand-600 text-white rounded-lg text-xs font-semibold hover:bg-brand-500 transition-colors"
              >
                View Avatar
              </Link>
            </div>
          )}
        </div>

        {/* Quick Saved Phrases */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Bookmark className="w-4 h-4 text-primary-500" />
              Quick Assistive Phrases
            </h3>
            <span className="text-xs text-slate-400">1-Click Voice / Sign</span>
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            {savedPhrases.map((phrase, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60 flex flex-col justify-between hover:border-brand-500 transition-colors"
              >
                <div>
                  <div className="text-xs font-bold text-slate-800 dark:text-slate-200">{phrase.title}</div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">{phrase.text}</div>
                </div>
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-200/60 dark:border-slate-700/40">
                  <span className="text-[10px] font-bold text-brand-600 dark:text-brand-400">{phrase.isl}</span>
                  <button
                    onClick={() => speak(phrase.text, phrase.lang)}
                    className="p-1 text-slate-400 hover:text-brand-500 transition-colors"
                    title="Speak text"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 4. RECENT TRANSLATIONS FEED */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-500" />
            Recent Activity & Translations
          </h3>
          <Link to="/history" className="text-xs font-bold text-brand-600 dark:text-brand-400 hover:underline">
            View All History →
          </Link>
        </div>

        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {history.length === 0 ? (
            <div className="py-6 text-center text-xs text-slate-400">
              No recent translations recorded yet.
            </div>
          ) : (
            history.map((rec, i) => (
              <div key={i} className="py-3 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-[10px] font-bold uppercase text-slate-600 dark:text-slate-400">
                    {rec.source_type} → {rec.target_type}
                  </span>
                  <div>
                    <div className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                      {rec.source_content}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">
                      → {rec.target_content}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => speak(rec.target_content, 'en')}
                  className="p-2 text-slate-400 hover:text-brand-500 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <Volume2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
