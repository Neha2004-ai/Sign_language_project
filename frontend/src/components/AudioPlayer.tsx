import React, { useState } from 'react';
import { Volume2, VolumeX, Play, Pause, RotateCcw, Globe } from 'lucide-react';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';
import { Language } from '../types';

interface AudioPlayerProps {
  text: string;
  defaultLanguage?: Language;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  text,
  defaultLanguage = 'en',
}) => {
  const [lang, setLang] = useState<Language>(defaultLanguage);
  const { speak, pause, resume, stop, isSpeaking, isPaused } = useSpeechSynthesis();

  const handlePlay = () => {
    if (isPaused) {
      resume();
    } else {
      speak(text, lang);
    }
  };

  return (
    <div className="flex items-center space-x-2 p-2 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/60 w-fit">
      {/* Play/Pause Button */}
      <button
        onClick={isSpeaking && !isPaused ? pause : handlePlay}
        disabled={!text}
        className="p-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white shadow-sm transition-colors disabled:opacity-50"
        title={isSpeaking && !isPaused ? 'Pause Voice' : 'Play Voice'}
      >
        {isSpeaking && !isPaused ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
      </button>

      {/* Replay */}
      <button
        onClick={() => speak(text, lang)}
        disabled={!text}
        className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
        title="Replay from start"
      >
        <RotateCcw className="w-3.5 h-3.5" />
      </button>

      {/* Language Selector */}
      <div className="flex items-center pl-2 border-l border-slate-300 dark:border-slate-700">
        <Globe className="w-3.5 h-3.5 text-slate-400 mr-1.5" />
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value as Language)}
          className="bg-transparent text-xs font-semibold text-slate-700 dark:text-slate-300 focus:outline-none cursor-pointer"
        >
          <option value="en">EN</option>
          <option value="hi">HI</option>
          <option value="bn">BN</option>
        </select>
      </div>

      {isSpeaking && (
        <span className="flex items-center gap-1 text-[11px] font-bold text-brand-600 dark:text-brand-400 pl-2">
          <Volume2 className="w-3.5 h-3.5 animate-bounce" />
          Speaking...
        </span>
      )}
    </div>
  );
};
