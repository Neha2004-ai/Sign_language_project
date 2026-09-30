import React from 'react';
import { Globe } from 'lucide-react';
import { useLanguage } from '../store/LanguageContext';
import { Language } from '../types';

export const LanguageSelector: React.FC<{ minimal?: boolean }> = ({ minimal = false }) => {
  const { language, setLanguage } = useLanguage();

  const options: Array<{ code: Language; label: string; native: string }> = [
    { code: 'en', label: 'English', native: 'English' },
    { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
    { code: 'bn', label: 'Bengali', native: 'বাংলা' },
  ];

  return (
    <div className="relative inline-flex items-center">
      {!minimal && <Globe className="w-4 h-4 text-slate-500 mr-2" />}
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value as Language)}
        aria-label="Select Language"
        className="bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 text-sm font-medium rounded-lg px-2.5 py-1.5 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500 cursor-pointer"
      >
        {options.map((opt) => (
          <option key={opt.code} value={opt.code}>
            {opt.native} ({opt.label})
          </option>
        ))}
      </select>
    </div>
  );
};
