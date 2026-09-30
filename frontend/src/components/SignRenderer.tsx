import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, FastForward, User, Sparkles, Layers } from 'lucide-react';
import { ISLTokenGesture } from '../types';

interface SignRendererProps {
  gestures: ISLTokenGesture[];
  playbackSpeed?: number;
  autoPlay?: boolean;
  onSequenceComplete?: () => void;
}

export const SignRenderer: React.FC<SignRendererProps> = ({
  gestures,
  playbackSpeed: initialSpeed = 1.0,
  autoPlay = true,
  onSequenceComplete,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [speed, setSpeed] = useState(initialSpeed);
  const [renderMode, setRenderMode] = useState<'avatar' | 'landmarks' | 'card'>('avatar');
  const timerRef = useRef<any>(null);

  const activeGesture = gestures && gestures.length > 0 ? gestures[currentIndex] : null;

  useEffect(() => {
    setCurrentIndex(0);
    setIsPlaying(autoPlay && gestures.length > 0);
  }, [gestures, autoPlay]);

  useEffect(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    if (isPlaying && gestures.length > 0) {
      const currentDuration = (activeGesture?.duration_ms || 1200) / speed;
      timerRef.current = setTimeout(() => {
        if (currentIndex < gestures.length - 1) {
          setCurrentIndex((prev) => prev + 1);
        } else {
          setIsPlaying(false);
          if (onSequenceComplete) onSequenceComplete();
        }
      }, currentDuration);
    }

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isPlaying, currentIndex, gestures, speed, activeGesture, onSequenceComplete]);

  const togglePlay = () => {
    if (!isPlaying && currentIndex >= gestures.length - 1) {
      setCurrentIndex(0);
      setIsPlaying(true);
    } else {
      setIsPlaying(!isPlaying);
    }
  };

  const handleReplay = () => {
    setCurrentIndex(0);
    setIsPlaying(true);
  };

  if (!gestures || gestures.length === 0) {
    return (
      <div className="w-full aspect-video bg-gradient-to-b from-slate-900 to-slate-950 rounded-2xl flex flex-col items-center justify-center text-center p-6 border border-slate-800">
        <User className="w-12 h-12 text-slate-600 mb-3 animate-pulse" />
        <h4 className="text-slate-300 font-bold text-base">ISL Avatar Renderer Ready</h4>
        <p className="text-slate-500 text-xs max-w-xs mt-1">
          Type text or use voice input to generate real-time Indian Sign Language animations.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full bg-slate-950 rounded-2xl overflow-hidden shadow-xl border border-slate-800 flex flex-col">
      {/* Central Visual Display */}
      <div className="relative w-full aspect-video bg-gradient-to-b from-slate-900 via-slate-950 to-slate-900 flex flex-col items-center justify-center p-6">
        {/* Mode Switcher */}
        <div className="absolute top-3 right-3 flex items-center bg-slate-900/80 backdrop-blur-md rounded-xl p-1 border border-slate-800 z-10">
          <button
            onClick={() => setRenderMode('avatar')}
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors ${
              renderMode === 'avatar' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            3D Avatar
          </button>
          <button
            onClick={() => setRenderMode('landmarks')}
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors ${
              renderMode === 'landmarks' ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            Keypoints
          </button>
        </div>

        {/* Animated Visual Sign Avatar */}
        <div className="relative flex flex-col items-center justify-center">
          {/* Avatar Graphic / SVG Kinetic Model */}
          <div className="w-48 h-48 rounded-full bg-gradient-to-tr from-brand-950/80 via-slate-900 to-primary-950/80 border border-brand-500/40 flex flex-col items-center justify-center relative shadow-2xl shadow-brand-500/20 overflow-hidden">
            {/* Pulsing ring */}
            <div className={`absolute inset-0 rounded-full border-2 border-brand-400/20 ${isPlaying ? 'animate-ping' : ''}`} />

            {/* Kinetic ISL Hand Skeleton / Avatar SVG */}
            <div className="relative z-10 flex flex-col items-center justify-center">
              {renderMode === 'avatar' ? (
                <svg
                  viewBox="0 0 100 100"
                  className={`w-24 h-24 text-teal-400 transform transition-transform duration-300 ${
                    isPlaying ? 'animate-float' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  {/* Palm base */}
                  <path d="M 35 75 Q 50 82 65 75 L 65 55 Q 50 50 35 55 Z" fill="rgba(20, 184, 166, 0.15)" stroke="#14b8a6" />
                  {/* Thumb */}
                  <path
                    d={
                      ['HELLO', 'YES', 'HELP', 'I LOVE YOU', '5', '3', 'GOODBYE'].includes(activeGesture?.token || '')
                        ? "M 35 62 Q 22 55 20 42"
                        : "M 35 62 Q 30 60 32 50"
                    }
                    stroke={['HELLO', 'YES', 'HELP', 'I LOVE YOU', '5'].includes(activeGesture?.token || '') ? '#2dd4bf' : '#64748b'}
                  />
                  {/* Index */}
                  <path
                    d={
                      ['HELLO', 'THANK YOU', 'NO', 'HELP', 'I LOVE YOU', '1', '2', '3', '4', '5', 'GOODBYE'].includes(activeGesture?.token || '')
                        ? "M 42 52 L 40 22"
                        : "M 42 52 Q 41 42 43 45"
                    }
                    stroke={['HELLO', 'THANK YOU', 'NO', 'HELP', '1', '2', '5'].includes(activeGesture?.token || '') ? '#2dd4bf' : '#64748b'}
                  />
                  {/* Middle */}
                  <path
                    d={
                      ['HELLO', 'THANK YOU', 'NO', '2', '3', '4', '5', 'GOODBYE'].includes(activeGesture?.token || '')
                        ? "M 50 50 L 50 18"
                        : "M 50 50 Q 50 40 50 44"
                    }
                    stroke={['HELLO', 'THANK YOU', 'NO', '2', '3', '5'].includes(activeGesture?.token || '') ? '#2dd4bf' : '#64748b'}
                  />
                  {/* Ring */}
                  <path
                    d={
                      ['HELLO', 'THANK YOU', '4', '5', 'GOODBYE'].includes(activeGesture?.token || '')
                        ? "M 58 52 L 60 22"
                        : "M 58 52 Q 58 42 56 45"
                    }
                    stroke={['HELLO', 'THANK YOU', '4', '5'].includes(activeGesture?.token || '') ? '#2dd4bf' : '#64748b'}
                  />
                  {/* Pinky */}
                  <path
                    d={
                      ['HELLO', 'THANK YOU', 'I LOVE YOU', '4', '5', 'GOODBYE'].includes(activeGesture?.token || '')
                        ? "M 65 55 L 72 30"
                        : "M 65 55 Q 64 45 62 48"
                    }
                    stroke={['HELLO', 'I LOVE YOU', '5'].includes(activeGesture?.token || '') ? '#2dd4bf' : '#64748b'}
                  />
                  {/* Wrist joint */}
                  <circle cx="50" cy="78" r="3" fill="#6366f1" stroke="#fff" strokeWidth="1" />
                </svg>
              ) : (
                /* Keypoints Wireframe View */
                <svg viewBox="0 0 100 100" className="w-24 h-24" fill="none">
                  <circle cx="50" cy="80" r="4" fill="#6366f1" />
                  <circle cx="30" cy="55" r="3" fill="#2dd4bf" />
                  <circle cx="42" cy="35" r="3" fill="#2dd4bf" />
                  <circle cx="50" cy="30" r="3" fill="#2dd4bf" />
                  <circle cx="58" cy="35" r="3" fill="#2dd4bf" />
                  <circle cx="70" cy="50" r="3" fill="#2dd4bf" />
                  <line x1="50" y1="80" x2="30" y2="55" stroke="#14b8a6" strokeWidth="1.5" />
                  <line x1="50" y1="80" x2="42" y2="35" stroke="#14b8a6" strokeWidth="1.5" />
                  <line x1="50" y1="80" x2="50" y2="30" stroke="#14b8a6" strokeWidth="1.5" />
                  <line x1="50" y1="80" x2="58" y2="35" stroke="#14b8a6" strokeWidth="1.5" />
                  <line x1="50" y1="80" x2="70" y2="50" stroke="#14b8a6" strokeWidth="1.5" />
                </svg>
              )}

              {/* Token Title */}
              <div className="text-xl font-black text-white mt-1 tracking-tight">
                {activeGesture?.token}
              </div>
            </div>
          </div>

          <div className="mt-4 text-center">
            <h3 className="text-white text-lg font-bold">
              {activeGesture?.label}
            </h3>
            <p className="text-slate-400 text-xs mt-0.5">
              {activeGesture?.description}
            </p>
          </div>
        </div>

        {/* Token Progress Pills */}
        <div className="absolute bottom-3 left-4 right-4 flex items-center justify-center gap-1.5 overflow-x-auto py-1">
          {gestures.map((g, idx) => (
            <button
              key={idx}
              onClick={() => {
                setCurrentIndex(idx);
                setIsPlaying(false);
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all shrink-0 ${
                idx === currentIndex
                  ? 'bg-brand-500 text-white ring-2 ring-brand-400 shadow-md scale-105'
                  : idx < currentIndex
                  ? 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  : 'bg-slate-900/60 text-slate-500 border border-slate-800'
              }`}
            >
              {g.token}
            </button>
          ))}
        </div>
      </div>

      {/* Playback Controls Bar */}
      <div className="p-4 bg-slate-900/90 border-t border-slate-800 flex flex-wrap items-center justify-between gap-4">
        {/* Left Play Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={togglePlay}
            className="p-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-primary-600 hover:from-brand-500 hover:to-primary-500 text-white shadow-md transition-all"
            title={isPlaying ? 'Pause' : 'Play Sign Sequence'}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
          </button>
          <button
            onClick={handleReplay}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Replay from Beginning"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <span className="text-xs text-slate-400 font-medium ml-2">
            Step {currentIndex + 1} of {gestures.length}
          </span>
        </div>

        {/* Right Speed Controls */}
        <div className="flex items-center space-x-3">
          <span className="text-xs font-semibold text-slate-400">Speed:</span>
          {[0.5, 1.0, 1.5, 2.0].map((s) => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              className={`px-2 py-1 rounded-lg text-xs font-bold transition-colors ${
                speed === s
                  ? 'bg-brand-500/20 text-brand-400 border border-brand-500/40'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
