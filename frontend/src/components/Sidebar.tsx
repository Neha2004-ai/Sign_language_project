import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Video,
  Type,
  Mic,
  MessageSquareText,
  GraduationCap,
  Sparkles,
  History,
  BarChart3,
  Settings,
  Cpu
} from 'lucide-react';
import { useLanguage } from '../store/LanguageContext';

export const Sidebar: React.FC = () => {
  const { t } = useLanguage();

  const navItems = [
    { to: '/dashboard', label: t('dashboard'), icon: LayoutDashboard },
    { to: '/translator', label: t('sign_to_text'), icon: Video },
    { to: '/text-to-sign', label: t('text_to_sign'), icon: Type },
    { to: '/speech-to-sign', label: t('speech_to_sign'), icon: Mic },
    { to: '/chat', label: t('chatbot'), icon: MessageSquareText },
    { to: '/learn', label: t('learn_isl'), icon: GraduationCap },
    { to: '/custom-gestures', label: t('custom_gestures'), icon: Sparkles },
    { to: '/history', label: t('history'), icon: History },
    { to: '/analytics', label: t('analytics'), icon: BarChart3 },
    { to: '/settings', label: t('settings'), icon: Settings },
    { to: '/admin', label: t('admin_model'), icon: Cpu },
  ];

  return (
    <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col shrink-0 h-[calc(100vh-4rem)] sticky top-16 select-none">
      <div className="p-4 flex-1 overflow-y-auto space-y-1">
        <div className="px-3 py-2 text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-brand-500/15 to-primary-500/15 text-brand-600 dark:text-brand-400 font-semibold border-l-4 border-brand-500'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/70 hover:text-slate-900 dark:hover:text-slate-100'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="truncate">{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      {/* Model & System Status Widget */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800">
        <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">AI Model Status</span>
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          </div>
          <div className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">
            ISL Baseline Engine
          </div>
          <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">
            21-Landmark Real-Time
          </div>
        </div>
      </div>
    </aside>
  );
};
