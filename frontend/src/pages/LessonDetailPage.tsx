import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Sparkles,
  Camera,
  Play,
  RotateCcw,
  Award,
  Zap,
  HelpCircle
} from 'lucide-react';
import { api } from '../services/api';
import { Lesson, Quiz, LandmarkPoint } from '../types';
import { LandmarkCanvas } from '../components/LandmarkCanvas';

export const LessonDetailPage: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [activeTab, setActiveTab] = useState<'study' | 'quiz'>('study');
  
  // Quiz states
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [quizFeedback, setQuizFeedback] = useState<any>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraMatchMessage, setCameraMatchMessage] = useState<string | null>(null);

  useEffect(() => {
    if (lessonId) {
      api.getLessonDetail(parseInt(lessonId)).then(setLesson).catch(console.error);
    }
  }, [lessonId]);

  if (!lesson) {
    return (
      <div className="py-20 text-center text-slate-400">
        Loading lesson content...
      </div>
    );
  }

  const currentQuiz = lesson.quizzes && lesson.quizzes.length > 0 ? lesson.quizzes[currentQuizIndex] : null;

  const handleOptionSubmit = async (answer: string) => {
    if (!currentQuiz) return;
    setSelectedOption(answer);
    try {
      const res = await api.submitQuiz(currentQuiz.id, answer);
      setQuizFeedback(res);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCameraPoseDetected = async (landmarks: LandmarkPoint[]) => {
    if (!currentQuiz || currentQuiz.quiz_type !== 'camera_practice' || !landmarks.length) return;

    // Evaluate pose with inference endpoint
    try {
      const res = await api.predictLandmarks(landmarks);
      if (res.gesture.toUpperCase() === currentQuiz.target_gesture.toUpperCase() && res.confidence >= 0.70) {
        setCameraMatchMessage(`✅ Excellent! Perfect ${currentQuiz.target_gesture} gesture detected!`);
        if (!quizFeedback) {
          const submitRes = await api.submitQuiz(currentQuiz.id, currentQuiz.target_gesture);
          setQuizFeedback(submitRes);
        }
      }
    } catch (err) {
      console.warn(err);
    }
  };

  const nextQuiz = () => {
    setSelectedOption(null);
    setQuizFeedback(null);
    setCameraMatchMessage(null);
    if (lesson.quizzes && currentQuizIndex < lesson.quizzes.length - 1) {
      setCurrentQuizIndex((prev) => prev + 1);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Back button & Title */}
      <div>
        <Link
          to="/learn"
          className="inline-flex items-center text-xs font-semibold text-slate-500 hover:text-emerald-600 transition-colors mb-2"
        >
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back to Lessons
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-slate-900 dark:text-white">
              {lesson.title}
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {lesson.description}
            </p>
          </div>

          {/* Mode Switcher */}
          <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => setActiveTab('study')}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'study'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Study Signs
            </button>
            <button
              onClick={() => setActiveTab('quiz')}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'quiz'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Practice Quizzes ({lesson.quizzes?.length || 0})
            </button>
          </div>
        </div>
      </div>

      {/* TAB 1: STUDY SIGNS */}
      {activeTab === 'study' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {lesson.signs_data.map((sign, idx) => (
            <div key={idx} className="glass-card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-3xl font-black text-emerald-600 dark:text-emerald-400">
                  {sign.name}
                </span>
                <span className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-600 text-xs font-bold">
                  {sign.label}
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <span className="font-bold text-slate-400 uppercase">Meaning:</span>
                  <p className="text-slate-700 dark:text-slate-300 font-medium mt-0.5">{sign.meaning}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-400 uppercase">Performance Tips:</span>
                  <p className="text-slate-600 dark:text-slate-400 mt-0.5">{sign.tips}</p>
                </div>
              </div>

              <div className="pt-2">
                <Link
                  to={`/text-to-sign?query=${encodeURIComponent(sign.name)}`}
                  className="w-full py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-emerald-500/15 hover:text-emerald-600 text-xs font-bold flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Play className="w-3.5 h-3.5" /> Watch Avatar Animation
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 2: INTERACTIVE QUIZZES */}
      {activeTab === 'quiz' && currentQuiz && (
        <div className="glass-card p-6 sm:p-8 space-y-6">
          {/* Quiz Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
              Quiz {currentQuizIndex + 1} of {lesson.quizzes?.length}
            </span>
            <span className="flex items-center gap-1 text-xs font-bold text-amber-500">
              <Sparkles className="w-3.5 h-3.5" /> +{currentQuiz.points} Points
            </span>
          </div>

          {/* Prompt */}
          <div className="text-center py-2 space-y-2">
            <h3 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white">
              {currentQuiz.prompt_text}
            </h3>
          </div>

          {/* Quiz Body based on Type */}
          {currentQuiz.quiz_type === 'camera_practice' ? (
            <div className="space-y-4">
              <LandmarkCanvas
                isActive={isCameraActive}
                onToggleActive={() => setIsCameraActive(!isCameraActive)}
                onLandmarksDetected={handleCameraPoseDetected}
              />
              {cameraMatchMessage && (
                <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 text-xs font-bold border border-emerald-300 dark:border-emerald-800 text-center">
                  {cameraMatchMessage}
                </div>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {currentQuiz.options?.map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => handleOptionSubmit(opt.label)}
                  disabled={!!quizFeedback}
                  className={`p-4 rounded-xl text-left font-bold text-sm transition-all border ${
                    selectedOption === opt.label
                      ? quizFeedback?.is_correct
                        ? 'bg-emerald-50 dark:bg-emerald-950/50 border-emerald-500 text-emerald-700 dark:text-emerald-300 ring-2 ring-emerald-400'
                        : 'bg-rose-50 dark:bg-rose-950/50 border-rose-500 text-rose-700 dark:text-rose-300 ring-2 ring-rose-400'
                      : 'bg-slate-50 dark:bg-slate-800/80 border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 hover:border-emerald-500'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}

          {/* Result Feedback Banner */}
          {quizFeedback && (
            <div className={`p-4 rounded-2xl border ${
              quizFeedback.is_correct
                ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300'
                : 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300'
            }`}>
              <div className="flex items-center gap-2 font-bold text-sm mb-1">
                {quizFeedback.is_correct ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-500" />
                )}
                {quizFeedback.is_correct ? 'Correct! Well Done!' : 'Not Quite Right'}
              </div>
              {quizFeedback.explanation && (
                <p className="text-xs mt-1 leading-relaxed opacity-90">
                  {quizFeedback.explanation}
                </p>
              )}
            </div>
          )}

          {/* Navigation / Next Quiz */}
          {quizFeedback && (
            <div className="flex justify-end pt-4 border-t border-slate-100 dark:border-slate-800">
              {lesson.quizzes && currentQuizIndex < lesson.quizzes.length - 1 ? (
                <button
                  onClick={nextQuiz}
                  className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md transition-colors"
                >
                  Next Question →
                </button>
              ) : (
                <Link
                  to="/learn"
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold text-xs shadow-md"
                >
                  🎉 Complete Module
                </Link>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
