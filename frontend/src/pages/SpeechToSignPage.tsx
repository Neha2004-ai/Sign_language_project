import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Globe, Sparkles, RotateCcw, Volume2, AlertCircle } from 'lucide-react';
import { SignRenderer } from '../components/SignRenderer';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { api } from '../services/api';
import { Language, TextToSignResponse } from '../types';

export const SpeechToSignPage: React.FC = () => {
  const [selectedLanguage, setSelectedLanguage] = useState<Language>('en');
  const { isListening, transcript, error, startListening, stopListening, resetTranscript } = useSpeechRecognition(selectedLanguage);
  
  const [signData, setSignData] = useState<TextToSignResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (transcript.trim()) {
      handleSpeechToSign(transcript);
    }
  }, [transcript]);

  const handleSpeechToSign = async (text: string) => {
    setIsProcessing(true);
    try {
      const res = await api.speechToSign(text, selectedLanguage);
      setSignData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClear = () => {
    resetTranscript();
    setSignData(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-teal-500/10 text-teal-600 dark:text-teal-400">
              <Mic className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-black text-slate-900 dark:text-white">
              Speech → Sign Language
            </h1>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Speak naturally in English, Hindi, or Bengali to generate instant ISL gestures.
          </p>
        </div>

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

      {/* Main Two Column */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Microphone Controller & Transcript (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-card p-6 text-center space-y-6">
            {/* Microphone Button with Pulse */}
            <div className="relative inline-flex items-center justify-center">
              {isListening && (
                <div className="absolute w-28 h-28 rounded-full bg-teal-500/20 animate-ping pointer-events-none" />
              )}
              <button
                onClick={isListening ? stopListening : startListening}
                className={`w-20 h-20 rounded-full flex items-center justify-center shadow-xl transition-all transform hover:scale-105 ${
                  isListening
                    ? 'bg-rose-500 text-white shadow-rose-500/30'
                    : 'bg-gradient-to-r from-teal-500 to-brand-600 text-white shadow-brand-500/30'
                }`}
              >
                {isListening ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
              </button>
            </div>

            <div>
              <div className="text-base font-bold text-slate-900 dark:text-white">
                {isListening ? 'Listening to voice...' : 'Click Microphone to Speak'}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Supports English, Hindi, and Bengali natural speech
              </p>
            </div>

            {/* Live Transcript Display */}
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 min-h-[90px] flex flex-col justify-between text-left">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400">Live Transcript:</span>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-1">
                  {transcript || (
                    <span className="text-slate-400 italic">"Say something like 'Help me please'..."</span>
                  )}
                </p>
              </div>

              {transcript && (
                <div className="flex justify-end pt-2 border-t border-slate-200/60 dark:border-slate-700/60">
                  <button
                    onClick={handleClear}
                    className="text-xs font-semibold text-rose-500 hover:underline flex items-center gap-1"
                  >
                    <RotateCcw className="w-3 h-3" /> Clear
                  </button>
                </div>
              )}
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-400 text-xs flex items-center gap-2 border border-rose-200 dark:border-rose-900">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Right: SignRenderer (7 Cols) */}
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
