import React, { useState } from 'react';
import { Settings as SettingsIcon, Volume2, Camera, Globe, Moon, Key, CheckCircle2 } from 'lucide-react';
import { useLanguage } from '../store/LanguageContext';
import { useTheme } from '../store/ThemeContext';
import { Language } from '../types';

export const SettingsPage: React.FC = () => {
  const { language, setLanguage } = useLanguage();
  const { theme, toggleTheme } = useTheme();

  const [autoSpeak, setAutoSpeak] = useState(true);
  const [speechSpeed, setSpeechSpeed] = useState(1.0);
  const [savedNotice, setSavedNotice] = useState(false);

  const handleSave = () => {
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-slate-500/10 text-slate-600 dark:text-slate-300">
            <SettingsIcon className="w-5 h-5" />
          </span>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">
            System & Accessibility Settings
          </h1>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Customize speech synthesis rates, interface theme, native languages, and camera inputs.
        </p>
      </div>

      <div className="glass-card divide-y divide-slate-100 dark:divide-slate-800">
        {/* Language Preference */}
        <div className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Globe className="w-4 h-4 text-brand-500" />
              Interface & Translation Language
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Default language for captions, speech synthesis, and translations.
            </p>
          </div>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as Language)}
            className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-bold text-slate-800 dark:text-slate-200 cursor-pointer focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी (Hindi)</option>
            <option value="bn">বাংলা (Bengali)</option>
          </select>
        </div>

        {/* Theme Preference */}
        <div className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Moon className="w-4 h-4 text-primary-500" />
              Color Theme Mode
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Toggle between high-contrast dark mode and clean light mode.
            </p>
          </div>
          <button
            onClick={toggleTheme}
            className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs font-bold text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          >
            Active: {theme === 'dark' ? 'Dark Mode 🌙' : 'Light Mode ☀️'}
          </button>
        </div>

        {/* Speech Output Speed */}
        <div className="p-6 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-teal-500" />
              Speech Synthesis Speed ({speechSpeed}x)
            </h3>
            <span className="text-xs font-semibold text-slate-400">
              {speechSpeed === 1.0 ? 'Normal Rate' : speechSpeed < 1.0 ? 'Slower' : 'Faster'}
            </span>
          </div>
          <input
            type="range"
            min="0.5"
            max="1.5"
            step="0.1"
            value={speechSpeed}
            onChange={(e) => setSpeechSpeed(parseFloat(e.target.value))}
            className="w-full accent-teal-500 cursor-pointer"
          />
        </div>

        {/* Save Button */}
        <div className="p-6 flex items-center justify-between">
          {savedNotice && (
            <span className="text-xs font-bold text-emerald-500 flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4" /> Preferences saved!
            </span>
          )}
          <button
            onClick={handleSave}
            className="ml-auto px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-xs shadow-md transition-colors"
          >
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
};
