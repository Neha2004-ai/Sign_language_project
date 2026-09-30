import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Hand, User as UserIcon, LogOut, Sparkles, BookOpen } from 'lucide-react';
import { useAuth } from '../store/AuthContext';
import { ThemeToggle } from './ThemeToggle';
import { LanguageSelector } from './LanguageSelector';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-primary-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform">
              <Hand className="w-5 h-5" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-brand-600 via-primary-500 to-indigo-600 bg-clip-text text-transparent">
                SignBridge<span className="text-brand-500 font-bold">.AI</span>
              </span>
              <span className="hidden sm:block text-[10px] uppercase font-semibold tracking-wider text-slate-500 dark:text-slate-400">
                Bidirectional ISL Platform
              </span>
            </div>
          </Link>

          {/* Center navigation links */}
          <div className="hidden md:flex items-center space-x-6 text-sm font-medium text-slate-600 dark:text-slate-300">
            <Link to="/translator" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">
              Sign Translator
            </Link>
            <Link to="/text-to-sign" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">
              Text → Sign
            </Link>
            <Link to="/learn" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-emerald-500" />
              Learn ISL
            </Link>
            <Link to="/chat" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-500" />
              AI Chatbot
            </Link>
          </div>

          {/* Right controls */}
          <div className="flex items-center space-x-3">
            <LanguageSelector />
            <ThemeToggle />

            {isAuthenticated ? (
              <div className="flex items-center space-x-2 pl-2 border-l border-slate-200 dark:border-slate-800">
                <Link
                  to="/dashboard"
                  className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-brand-50 dark:bg-brand-950/50 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-800/60 hover:bg-brand-100 transition-colors text-xs font-semibold"
                >
                  <UserIcon className="w-3.5 h-3.5" />
                  <span className="max-w-[100px] truncate">{user?.full_name || user?.email}</span>
                  {user?.is_guest && (
                    <span className="px-1.5 py-0.2 bg-amber-500/20 text-amber-600 dark:text-amber-400 rounded text-[9px] font-bold">
                      GUEST
                    </span>
                  )}
                </Link>
                <button
                  onClick={logout}
                  title="Log out"
                  className="p-1.5 text-slate-500 hover:text-rose-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/login"
                  className="px-3.5 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-200 hover:text-brand-600 dark:hover:text-brand-400 transition-colors"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-1.5 text-sm font-semibold text-white bg-gradient-to-r from-brand-600 to-primary-600 hover:from-brand-500 hover:to-primary-500 rounded-xl shadow-sm transition-all"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
