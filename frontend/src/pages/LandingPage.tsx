import React from 'react';
import { Link } from 'react-router-dom';
import {
  Hand,
  Video,
  Type,
  Mic,
  Sparkles,
  BookOpen,
  ArrowRight,
  CheckCircle2,
  Globe2,
  Cpu,
  Layers,
  ShieldCheck,
  Zap,
  Users
} from 'lucide-react';
import { useAuth } from '../store/AuthContext';
import { useLanguage } from '../store/LanguageContext';

export const LandingPage: React.FC = () => {
  const { loginAsGuest, isAuthenticated } = useAuth();
  const { t } = useLanguage();

  return (
    <div className="space-y-24 pb-20">
      {/* 1. HERO SECTION */}
      <section className="relative pt-12 pb-20 overflow-hidden">
        {/* Background glow effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-brand-500/20 to-primary-500/20 rounded-full blur-3xl -z-10 pointer-events-none" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-50 dark:bg-brand-950/60 border border-brand-200 dark:border-brand-800 text-brand-700 dark:text-brand-300 text-xs font-bold tracking-wide animate-pulse-subtle">
            <Sparkles className="w-3.5 h-3.5" />
            AI-Powered Bidirectional Indian Sign Language Platform
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
            Breaking Communication Barriers with{' '}
            <span className="bg-gradient-to-r from-brand-600 via-teal-500 to-primary-600 bg-clip-text text-transparent">
              Assistive AI
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto font-normal leading-relaxed">
            Real-time, two-way translation between <strong>Indian Sign Language (ISL)</strong> and spoken/written language. Supporting English, Hindi, and Bengali with live computer vision and interactive avatars.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              to="/translator"
              className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-gradient-to-r from-brand-600 to-primary-600 hover:from-brand-500 hover:to-primary-500 text-white font-bold text-base shadow-lg shadow-brand-600/25 flex items-center justify-center gap-2 transition-all transform hover:-translate-y-0.5"
            >
              <Video className="w-5 h-5" />
              {t('start_translating')}
              <ArrowRight className="w-4 h-4 ml-1" />
            </Link>

            <Link
              to="/learn"
              className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 font-bold text-base border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/60 flex items-center justify-center gap-2 transition-all"
            >
              <BookOpen className="w-5 h-5 text-emerald-500" />
              {t('learn_isl')}
            </Link>

            {!isAuthenticated && (
              <button
                onClick={loginAsGuest}
                className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-600 dark:text-amber-400 font-semibold text-sm border border-amber-500/30 transition-all"
              >
                ⚡ 1-Click Guest Demo
              </button>
            )}
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-10 max-w-3xl mx-auto text-left">
            <div className="glass-card p-4">
              <div className="text-2xl font-black text-brand-600 dark:text-brand-400">21 Pts</div>
              <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-0.5">MediaPipe Landmarks</div>
            </div>
            <div className="glass-card p-4">
              <div className="text-2xl font-black text-primary-600 dark:text-primary-400">3 Langs</div>
              <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-0.5">English, Hindi, Bengali</div>
            </div>
            <div className="glass-card p-4">
              <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">&lt;15 ms</div>
              <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-0.5">Inference Latency</div>
            </div>
            <div className="glass-card p-4">
              <div className="text-2xl font-black text-amber-600 dark:text-amber-400">100%</div>
              <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-0.5">Standard Laptop Ready</div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. HOW IT WORKS SECTION */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-3 mb-12">
          <h2 className="text-xs font-extrabold uppercase tracking-widest text-brand-600 dark:text-brand-400">
            System Architecture
          </h2>
          <p className="text-3xl font-black text-slate-900 dark:text-white">
            How SignBridge AI Works Bidirectionally
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Step 1 */}
          <div className="glass-card p-6 relative overflow-hidden group hover:border-brand-500 transition-all">
            <div className="w-12 h-12 rounded-2xl bg-brand-500/10 text-brand-600 dark:text-brand-400 flex items-center justify-center font-black text-xl mb-4">
              1
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Vision & Landmark Extraction
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Captures live video through a standard laptop camera and extracts 21 3D hand keypoints, calculating joint angles and wrist-relative spatial invariants at 30 FPS.
            </p>
          </div>

          {/* Step 2 */}
          <div className="glass-card p-6 relative overflow-hidden group hover:border-primary-500 transition-all">
            <div className="w-12 h-12 rounded-2xl bg-primary-500/10 text-primary-600 dark:text-primary-400 flex items-center justify-center font-black text-xl mb-4">
              2
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Neural Gesture Classification
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Evaluates features via static geometric models and temporal sequence buffers, outputting verified ISL predictions with real-time confidence scores and debouncing.
            </p>
          </div>

          {/* Step 3 */}
          <div className="glass-card p-6 relative overflow-hidden group hover:border-teal-500 transition-all">
            <div className="w-12 h-12 rounded-2xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center font-black text-xl mb-4">
              3
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Bidirectional Avatar & Voice
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Speaks out recognized gestures in English, Hindi, or Bengali, and reverse-translates spoken words into animated ISL avatar movements and fingerspelling.
            </p>
          </div>
        </div>
      </section>

      {/* 3. CORE MODULE SHOWCASE */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-xs font-extrabold uppercase tracking-widest text-primary-600 dark:text-primary-400">
            Feature Modules
          </h2>
          <p className="text-3xl font-black text-slate-900 dark:text-white">
            Complete Assistive Communication Toolkit
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Module 1 & 2 */}
          <div className="glass-card p-8 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-brand-600 text-white flex items-center justify-center">
              <Video className="w-5 h-5" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">
              Sign Language → Text & Speech
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Live webcam recognition with hand landmark skeleton overlay, confidence meters, and instantaneous multi-voice audio output in English, Hindi, or Bengali.
            </p>
            <Link to="/translator" className="inline-flex items-center text-sm font-bold text-brand-600 dark:text-brand-400 hover:underline">
              Launch Live Translator <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>

          {/* Module 3 & 4 */}
          <div className="glass-card p-8 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-primary-600 text-white flex items-center justify-center">
              <Type className="w-5 h-5" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">
              Text & Speech → Sign Language
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Input natural speech or text in your native language to generate smooth Indian Sign Language animations, kinetic gestures, and step-by-step fingerspelling.
            </p>
            <Link to="/text-to-sign" className="inline-flex items-center text-sm font-bold text-primary-600 dark:text-primary-400 hover:underline">
              Try Text to Sign <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>

          {/* Module 5 */}
          <div className="glass-card p-8 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">
              AI Assistive Chatbot
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Specialized conversational communication assistant with sign-to-chat inputs and automated ISL gesture animation generation for all responses.
            </p>
            <Link to="/chat" className="inline-flex items-center text-sm font-bold text-amber-600 dark:text-amber-400 hover:underline">
              Open Chatbot <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>

          {/* Module 6 & 7 */}
          <div className="glass-card p-8 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center">
              <BookOpen className="w-5 h-5" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">
              Learn ISL & Custom Gesture Training
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Structured modules for Alphabets, Numbers, and Everyday Phrases with interactive quizzes, camera practice quizzes, streak tracking, and personalized gesture training.
            </p>
            <Link to="/learn" className="inline-flex items-center text-sm font-bold text-emerald-600 dark:text-emerald-400 hover:underline">
              Start Learning ISL <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>
        </div>
      </section>

      {/* 4. FOOTER CTA */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="glass-panel p-10 sm:p-12 bg-gradient-to-tr from-brand-600/10 via-primary-500/10 to-transparent border-brand-500/30 space-y-6">
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
            Ready to Bridge the Communication Gap?
          </h2>
          <p className="text-slate-600 dark:text-slate-300 text-base max-w-xl mx-auto">
            Experience real-time, low-latency Indian Sign Language translation on any standard laptop or mobile browser.
          </p>
          <div className="pt-2">
            <Link
              to="/dashboard"
              className="px-8 py-3.5 rounded-2xl bg-gradient-to-r from-brand-600 to-primary-600 hover:from-brand-500 hover:to-primary-500 text-white font-bold text-base shadow-lg transition-all"
            >
              Open Dashboard
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
