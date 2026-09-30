import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  GraduationCap,
  Flame,
  Award,
  BookOpen,
  ArrowRight,
  CheckCircle2,
  Lock,
  Sparkles,
  Zap,
  Layers
} from 'lucide-react';
import { api } from '../services/api';
import { Lesson, UserProgress } from '../types';

export const LearnPage: React.FC = () => {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    api.getLessons().then(setLessons).catch(console.error);
    api.getUserProgress().then(setProgress).catch(console.error);
  }, []);

  const categories = [
    { id: 'all', label: 'All Modules' },
    { id: 'words', label: 'Common Words' },
    { id: 'numbers', label: 'Numbers (0-9)' },
    { id: 'alphabet', label: 'Alphabets (A-Z)' },
  ];

  const filteredLessons = selectedCategory === 'all'
    ? lessons
    : lessons.filter((l) => l.category === selectedCategory);

  return (
    <div className="space-y-8">
      {/* Header with Gamification Banner */}
      <div className="glass-panel p-6 sm:p-8 bg-gradient-to-r from-emerald-600/15 via-brand-600/10 to-transparent border-emerald-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              <GraduationCap className="w-5 h-5" />
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
              Learn Indian Sign Language (ISL)
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 max-w-xl mt-1">
            Interactive visual lessons, live camera practice quizzes, and gamified streak progression.
          </p>
        </div>

        {/* Gamification Stats */}
        <div className="flex items-center gap-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md p-3 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm shrink-0">
          <div className="flex items-center gap-2 px-2">
            <Flame className="w-6 h-6 text-amber-500 animate-pulse" />
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase">Streak</div>
              <div className="text-base font-black text-slate-800 dark:text-white">
                {progress?.current_streak || 7} Days
              </div>
            </div>
          </div>
          <div className="h-8 w-px bg-slate-200 dark:bg-slate-800" />
          <div className="flex items-center gap-2 px-2">
            <Zap className="w-6 h-6 text-emerald-500" />
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase">Level {progress?.level || 3}</div>
              <div className="text-base font-black text-slate-800 dark:text-white">
                {progress?.total_xp || 1420} XP
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-colors shrink-0 ${
              selectedCategory === cat.id
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Lessons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredLessons.map((lesson) => (
          <div
            key={lesson.id}
            className="glass-card p-6 flex flex-col justify-between hover:border-emerald-500 transition-all group"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-[10px] font-bold uppercase tracking-wider">
                  {lesson.category}
                </span>
                <span className="flex items-center gap-1 text-xs font-bold text-amber-500">
                  <Sparkles className="w-3.5 h-3.5" /> +{lesson.xp_reward} XP
                </span>
              </div>

              <h3 className="text-lg font-bold text-slate-900 dark:text-white group-hover:text-emerald-500 transition-colors">
                {lesson.title}
              </h3>

              <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                {lesson.description}
              </p>

              {/* Signs Included Pills */}
              <div className="pt-2">
                <div className="text-[10px] font-bold text-slate-400 uppercase mb-1.5">Signs Included:</div>
                <div className="flex flex-wrap gap-1.5">
                  {lesson.signs_data.slice(0, 4).map((s, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] font-bold text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700"
                    >
                      {s.label}
                    </span>
                  ))}
                  {lesson.signs_data.length > 4 && (
                    <span className="px-1.5 py-0.5 text-[10px] text-slate-400 font-bold">
                      +{lesson.signs_data.length - 4} more
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="pt-6 mt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">
                {lesson.quizzes?.length || 2} Interactive Quizzes
              </span>
              <Link
                to={`/learn/${lesson.id}`}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-sm flex items-center gap-1.5 transition-colors"
              >
                Start Lesson <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
