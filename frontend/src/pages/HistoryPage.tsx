import React, { useState, useEffect } from 'react';
import { History, Search, Volume2, Filter, Trash2, Globe, Calendar } from 'lucide-react';
import { api } from '../services/api';
import { TranslationRecord } from '../types';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<TranslationRecord[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const { speak } = useSpeechSynthesis();

  useEffect(() => {
    api.getHistory(100).then(setHistory).catch(console.error);
  }, []);

  const filteredHistory = history.filter((item) => {
    const matchesSearch =
      item.source_content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.target_content.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || item.source_type === filterType;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
            <History className="w-5 h-5" />
          </span>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">
            Translation History & Logs
          </h1>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Search, filter, and replay past voice, text, and sign translations.
        </p>
      </div>

      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search translated words or phrases..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-900 dark:text-slate-100"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 focus:outline-none cursor-pointer"
          >
            <option value="all">All Modes</option>
            <option value="sign">Sign → Text/Speech</option>
            <option value="text">Text → Sign</option>
            <option value="speech">Speech → Sign</option>
          </select>
        </div>
      </div>

      {/* History Table / Cards */}
      <div className="glass-card overflow-hidden">
        {filteredHistory.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400">
            No translation records found matching your filter.
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {filteredHistory.map((item, idx) => (
              <div
                key={idx}
                className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-600 dark:text-brand-400 text-[10px] font-bold uppercase">
                      {item.source_type} → {item.target_type}
                    </span>
                    <span className="text-[11px] text-slate-400 flex items-center gap-1">
                      <Globe className="w-3 h-3" />
                      {item.source_language.toUpperCase()} → {item.target_language.toUpperCase()}
                    </span>
                  </div>

                  <div className="text-sm font-bold text-slate-900 dark:text-white">
                    {item.source_content}
                  </div>
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400">
                    → {item.target_content}
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    onClick={() => speak(item.target_content, 'en')}
                    className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-brand-500 hover:text-white text-slate-600 dark:text-slate-300 transition-colors"
                    title="Play Speech"
                  >
                    <Volume2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
