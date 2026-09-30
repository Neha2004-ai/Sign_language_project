import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  Video,
  Volume2,
  VolumeX,
  RotateCcw,
  Sparkles,
  Layers,
  Globe,
  Settings2,
  CheckCircle2,
  AlertTriangle,
  Terminal,
  Activity,
  Cpu,
  FlipHorizontal
} from 'lucide-react';
import { LandmarkCanvas } from '../components/LandmarkCanvas';
import { ConfidenceMeter } from '../components/ConfidenceMeter';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';
import { useWebSocketSign } from '../hooks/useWebSocketSign';
import { useAuth } from '../store/AuthContext';
import { api } from '../services/api';
import { LandmarkPoint, DualHandData, PredictionResult, Language } from '../types';

export const TranslatorPage: React.FC = () => {
  const { user } = useAuth();
  const [isCameraActive, setIsCameraActive] = useState(true);
  const [mirroredCamera, setMirroredCamera] = useState(true);
  const [debugMode, setDebugMode] = useState(true);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<Language>('en');
  const [currentPrediction, setCurrentPrediction] = useState<PredictionResult>({
    gesture: 'NAMASTE',
    confidence: 0.96,
    text_en: 'Namaste / Greetings',
    text_hi: 'नमस्ते / नमस्कार',
    text_bn: 'নমস্কার / প্রণতি',
    status: 'success',
    category: 'greeting',
    is_dynamic: false,
    num_hands: 2,
    left_detected: true,
    right_detected: true,
    recognition_mode: 'STATIC',
    sequence_len: 20,
    state_machine_state: 'OUTPUT',
    model_status: 'ML Ensemble (Dual-Hand RF + LSTM)',
    fps: 30.0,
    latency_ms: 6.2
  });
  const [predictionHistory, setPredictionHistory] = useState<string[]>(['NAMASTE', 'HELLO']);

  const { speak, isSpeaking } = useSpeechSynthesis();
  const lastSpokenGestureRef = useRef<string | null>(null);
  const lastInferenceTimeRef = useRef<number>(0);

  // WebSocket real-time client with dual-hand streaming
  const { isConnected: isWsConnected, latestPrediction, sendDualHands } = useWebSocketSign(isCameraActive);

  // Sync latest prediction from WebSocket into UI state & handle State Machine debouncing
  useEffect(() => {
    if (latestPrediction && latestPrediction.gesture && latestPrediction.gesture !== 'NO_HAND') {
      setCurrentPrediction(latestPrediction);

      // State machine debouncing: only commit to history and speech on CONFIRMED output
      const isConfirmed = latestPrediction.is_new_confirmed_output || 
        (latestPrediction.state_machine_state === 'OUTPUT' && latestPrediction.confidence >= 0.70);

      if (isConfirmed && latestPrediction.status === 'success' && latestPrediction.gesture !== 'UNKNOWN_GESTURE') {
        setPredictionHistory((prev) => {
          if (prev[0] === latestPrediction.gesture) return prev;
          return [latestPrediction.gesture, ...prev.slice(0, 4)];
        });

        if (autoSpeak && lastSpokenGestureRef.current !== latestPrediction.gesture) {
          lastSpokenGestureRef.current = latestPrediction.gesture;
          const textToSpeak = selectedLanguage === 'hi' 
            ? latestPrediction.text_hi 
            : selectedLanguage === 'bn' 
            ? latestPrediction.text_bn 
            : latestPrediction.text_en;
          speak(textToSpeak, selectedLanguage);
        }
      }
    }
  }, [latestPrediction, autoSpeak, selectedLanguage, speak]);

  // Process dual-hand landmarks from camera
  const handleDualHandsDetected = useCallback(async (data: DualHandData) => {
    const now = Date.now();
    // Throttle inference requests to ~20-25 FPS
    if (now - lastInferenceTimeRef.current < 45) return;
    lastInferenceTimeRef.current = now;

    if (isWsConnected) {
      sendDualHands(data, mirroredCamera, user?.id);
    } else {
      // REST endpoint fallback
      try {
        const result = await api.predictDualHands(data.left_hand, data.right_hand, mirroredCamera, user?.id);
        if (result && result.gesture && result.gesture !== 'NO_HAND') {
          setCurrentPrediction(result);

          if (result.status === 'success' && result.confidence >= 0.70 && result.gesture !== 'UNKNOWN_GESTURE') {
            setPredictionHistory((prev) => {
              if (prev[0] === result.gesture) return prev;
              return [result.gesture, ...prev.slice(0, 4)];
            });

            if (autoSpeak && lastSpokenGestureRef.current !== result.gesture) {
              lastSpokenGestureRef.current = result.gesture;
              const textToSpeak = selectedLanguage === 'hi' ? result.text_hi : selectedLanguage === 'bn' ? result.text_bn : result.text_en;
              speak(textToSpeak, selectedLanguage);
            }
          }
        }
      } catch (err) {
        console.warn('REST inference fallback error:', err);
      }
    }
  }, [isWsConnected, sendDualHands, mirroredCamera, user?.id, autoSpeak, selectedLanguage, speak]);

  const handleResetStream = () => {
    setPredictionHistory([]);
    lastSpokenGestureRef.current = null;
  };

  const getDisplayText = () => {
    if (currentPrediction.status === 'low_confidence' || currentPrediction.gesture === 'UNKNOWN_GESTURE') {
      return selectedLanguage === 'hi' ? 'संकेत पहचाना नहीं गया' : selectedLanguage === 'bn' ? 'চিহ্নটি শনাক্ত করা যায়নি' : 'Sign not confidently recognized';
    }
    if (selectedLanguage === 'hi') return currentPrediction.text_hi;
    if (selectedLanguage === 'bn') return currentPrediction.text_bn;
    return currentPrediction.text_en;
  };

  const handleManualSpeak = () => {
    speak(getDisplayText(), selectedLanguage);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400">
              <Video className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-black text-slate-900 dark:text-white">
              Live ISL Translator
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/20">
              1-Hand & 2-Hand ISL
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time Indian Sign Language recognition with MediaPipe dual-hand pose tracking, static & dynamic LSTM sequence analysis.
          </p>
        </div>

        {/* Global Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
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

          <button
            onClick={() => setDebugMode(!debugMode)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 border transition-all ${
              debugMode
                ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border-brand-500/30 shadow-sm'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            Debug HUD {debugMode ? 'ON' : 'OFF'}
          </button>

          <label className="flex items-center space-x-2 text-xs font-semibold text-slate-600 dark:text-slate-300 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={autoSpeak}
              onChange={(e) => setAutoSpeak(e.target.checked)}
              className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500"
            />
            <span>Auto-Speak</span>
          </label>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Webcam Stream & Landmark Canvas (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <LandmarkCanvas
            isActive={isCameraActive}
            mirrored={mirroredCamera}
            onToggleMirrored={() => setMirroredCamera(!mirroredCamera)}
            onToggleActive={() => setIsCameraActive(!isCameraActive)}
            onDualHandsDetected={handleDualHandsDetected}
          />

          {/* Stream Quick Info */}
          <div className="flex items-center justify-between p-3 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm text-xs">
            <div className="flex items-center space-x-3">
              <span className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400 font-medium">
                <span className={`w-2 h-2 rounded-full ${isWsConnected ? 'bg-emerald-500 animate-pulse' : 'bg-brand-500'}`} />
                {isWsConnected ? 'WebSocket Dual-Stream 30 FPS' : 'REST Engine Ready'}
              </span>
              <span className="text-slate-400">|</span>
              <span className="font-semibold text-slate-600 dark:text-slate-300">
                Latency: ~{currentPrediction.latency_ms || 8}ms
              </span>
            </div>

            <button
              onClick={handleResetStream}
              className="px-3 py-1 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold flex items-center gap-1.5 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset
            </button>
          </div>

          {/* Developer / Debug HUD (Requirement 9) */}
          {debugMode && (
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-white font-mono text-xs shadow-xl space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-teal-400 font-bold flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
                  <Cpu className="w-3.5 h-3.5" />
                  ISL Diagnostic HUD (Telemetry)
                </span>
                <span className="text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                  {currentPrediction.model_status || 'ML Ensemble (Dual-Hand RF + LSTM)'}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
                {/* Left Hand Status */}
                <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Left Hand:</div>
                  <div className={`font-bold flex items-center gap-1 mt-0.5 ${currentPrediction.left_detected ? 'text-cyan-400' : 'text-slate-500'}`}>
                    <span className={`w-2 h-2 rounded-full ${currentPrediction.left_detected ? 'bg-cyan-400' : 'bg-slate-600'}`} />
                    {currentPrediction.left_detected ? 'DETECTED' : 'NO'}
                  </div>
                </div>

                {/* Right Hand Status */}
                <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Right Hand:</div>
                  <div className={`font-bold flex items-center gap-1 mt-0.5 ${currentPrediction.right_detected ? 'text-purple-400' : 'text-slate-500'}`}>
                    <span className={`w-2 h-2 rounded-full ${currentPrediction.right_detected ? 'bg-purple-400' : 'bg-slate-600'}`} />
                    {currentPrediction.right_detected ? 'DETECTED' : 'NO'}
                  </div>
                </div>

                {/* Detected Hands Count */}
                <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Total Hands:</div>
                  <div className="font-bold text-white mt-0.5">
                    {currentPrediction.num_hands ?? (currentPrediction.left_detected && currentPrediction.right_detected ? 2 : currentPrediction.left_detected || currentPrediction.right_detected ? 1 : 0)} Hand(s)
                  </div>
                </div>

                {/* Recognition Mode */}
                <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Mode:</div>
                  <div className={`font-bold mt-0.5 ${currentPrediction.recognition_mode === 'DYNAMIC' ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {currentPrediction.recognition_mode || 'STATIC'}
                  </div>
                </div>

                {/* Sequence Buffer */}
                <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Sequence Length:</div>
                  <div className="font-bold text-slate-200 mt-0.5">
                    {currentPrediction.sequence_len ?? 20} / 20 frames
                  </div>
                </div>

                {/* State Machine State */}
                <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">State Machine:</div>
                  <div className="font-bold text-brand-400 mt-0.5">
                    {currentPrediction.state_machine_state || 'IDLE'}
                  </div>
                </div>

                {/* FPS & Calibrated Latency */}
                <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Live FPS:</div>
                  <div className="font-bold text-emerald-400 mt-0.5">
                    {currentPrediction.fps || 30.0} FPS
                  </div>
                </div>

                {/* Camera Mirror State */}
                <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Mirrored Camera:</div>
                  <div className="font-bold text-sky-400 mt-0.5">
                    {mirroredCamera ? 'TRUE (Selfie)' : 'FALSE'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right: Live Prediction & Speech Output (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Main Prediction Card */}
          <div className="glass-card p-6 space-y-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                Recognized ISL Gesture
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                {currentPrediction.num_hands === 2 ? '2-Hand ISL' : '1-Hand ISL'}
              </span>
            </div>

            {/* Gesture Text Highlight */}
            <div className="text-center py-5 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
              <div className="text-4xl font-black text-slate-900 dark:text-white tracking-tight mb-1">
                {currentPrediction.status === 'low_confidence' || currentPrediction.gesture === 'UNKNOWN_GESTURE'
                  ? 'UNKNOWN SIGN'
                  : currentPrediction.gesture}
              </div>
              <div className="text-base font-bold text-brand-600 dark:text-brand-400">
                {getDisplayText()}
              </div>
              {currentPrediction.message && (
                <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 max-w-xs mx-auto">
                  {currentPrediction.message}
                </div>
              )}
            </div>

            {/* Confidence Score Meter */}
            <ConfidenceMeter
              confidence={currentPrediction.confidence}
              threshold={0.70}
              showDetails={true}
            />

            {/* Audio Speech Controls */}
            <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div className="text-xs font-medium text-slate-500 dark:text-slate-400">
                Speech Output ({selectedLanguage.toUpperCase()})
              </div>
              <button
                onClick={handleManualSpeak}
                disabled={currentPrediction.status === 'low_confidence'}
                className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-xs font-bold shadow-md shadow-brand-500/20 flex items-center gap-2 transition-all"
              >
                <Volume2 className="w-4 h-4" />
                Play Voice
              </button>
            </div>
          </div>

          {/* Recent Predictions Timeline */}
          <div className="glass-card p-5 space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Confirmed Signs Sequence
            </div>
            <div className="flex flex-wrap gap-2">
              {predictionHistory.length === 0 ? (
                <span className="text-xs text-slate-400 italic">Perform a sign to begin recording sequence.</span>
              ) : (
                predictionHistory.map((sign, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 text-xs font-bold border border-slate-200 dark:border-slate-700"
                  >
                    {sign}
                    {idx < predictionHistory.length - 1 && (
                      <span className="text-slate-400 font-normal">→</span>
                    )}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* Alternative Candidates */}
          {currentPrediction.alternatives && currentPrediction.alternatives.length > 0 && (
            <div className="glass-card p-4 space-y-2">
              <div className="text-[11px] font-bold text-slate-400 uppercase">Top ML Candidates</div>
              <div className="grid grid-cols-3 gap-2">
                {currentPrediction.alternatives.map((alt, idx) => (
                  <div key={idx} className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40 text-center">
                    <div className="text-xs font-bold text-slate-700 dark:text-slate-300">{alt.gesture}</div>
                    <div className="text-[10px] text-slate-400">{Math.round(alt.confidence * 100)}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
