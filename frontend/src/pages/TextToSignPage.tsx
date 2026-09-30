import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Type, Sparkles, Send, Globe, Play, Layers, RotateCcw } from 'lucide-react';
import { SignRenderer } from '../components/SignRenderer';
import { api } from '../services/api';
import { useLanguage } from '../store/LanguageContext';
import { Language, TextToSignResponse } from '../types';

export const TextToSignPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('query') || 'Thank you for your help';

  const [inputText, setInputText] = useState(initialQuery);
  const [selectedLanguage, setSelectedLanguage] = useState<Language>('en');
  const [signData, setSignData] = useState<TextToSignResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleTranslate = async (textToProcess?: string) => {
    const text = textToProcess || inputText;
    if (!text.trim()) return;

    setIsLoading(true);
    try {
      const res = await api.textToSign(text, selectedLanguage);
      setSignData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleTranslate(initialQuery);
  }, []);

  const sampleSentences = [
    { text: 'Hello', lang: 'en' as const },
    { text: 'Thank you', lang: 'en' as const },
    { text: 'I need help', lang: 'en' as const },
    { text: 'नमस्ते (Hello)', lang: 'hi' as const },
    { text: 'আমাকে সাহায্য করুন (Help me)', lang: 'bn' as const },
    { text: 'Where is doctor', lang: 'en' as const },
    { text: 'I love you', lang: 'en' as const }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-primary-500/10 text-primary-600 dark:text-primary-400">
              <Type className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-black text-slate-900 dark:text-white">
              Text → Sign Language (ISL)
            </h1>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Convert sentences from English, Hindi, or Bengali into animated ISL gestures.
          </p>
        </div>

        {/* Language Selector */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
          <Globe className="w-4 h-4 text-slate-400" />
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value as Language)}
            className="bg-transparent text-xs font-bold text-slate-700 dark:text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value="en">English (EN)</option>
            <option value="hi">हिन्दी (HI)</option>
            <option value="bn">বাংলা (BN)</option>
          </select>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Text Input & Analysis (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-card p-5 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Input Sentence
            </h3>

            <div className="space-y-3">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                rows={4}
                placeholder="Type words or sentence to translate to sign language..."
                className="w-full p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-900 dark:text-slate-100 resize-none font-medium"
              />

              <button
                onClick={() => handleTranslate()}
                disabled={isLoading || !inputText.trim()}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-primary-600 to-brand-600 hover:from-primary-500 hover:to-brand-500 text-white font-bold text-sm shadow-md shadow-primary-500/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                {isLoading ? 'Translating to ISL...' : 'Generate ISL Animation'}
              </button>
            </div>

            {/* Quick Sample Presets */}
            <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
              <div className="text-[11px] font-bold text-slate-400 uppercase mb-2">Quick Presets</div>
              <div className="flex flex-wrap gap-1.5">
                {sampleSentences.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setInputText(s.text);
                      setSelectedLanguage(s.lang);
                      handleTranslate(s.text);
                    }}
                    className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-brand-500/15 hover:text-brand-600 text-[11px] font-medium text-slate-600 dark:text-slate-300 transition-colors"
                  >
                    {s.text}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Translation Analysis Details */}
          {signData && (
            <div className="glass-card p-5 space-y-3">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Linguistic & Gesture Breakdown
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Detected Script:</span>
                  <span className="font-bold text-slate-700 dark:text-slate-200 uppercase">{signData.detected_language}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400">Total Sign Tokens:</span>
                  <span className="font-bold text-brand-600 dark:text-brand-400">{signData.isl_tokens.length} Signs</span>
                </div>
                <div className="py-1.5">
                  <span className="text-slate-400 block mb-1">Sequence Pipeline:</span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">{signData.sign_sequence_description}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right: SignRenderer Visual Avatar (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <SignRenderer
            gestures={signData?.gestures || []}
            playbackSpeed={1.0}
            autoPlay={true}
          />
        </div>
      </div>
    </div>
  );
};
