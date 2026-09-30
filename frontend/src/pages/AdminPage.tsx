import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Sliders,
  Database,
  Layers,
  CheckCircle2,
  AlertTriangle,
  UploadCloud,
  FileCode2,
  HardDrive
} from 'lucide-react';
import { api } from '../services/api';
import { ModelStatus } from '../types';

export const AdminPage: React.FC = () => {
  const [status, setStatus] = useState<ModelStatus | null>(null);
  const [threshold, setThreshold] = useState<number>(0.65);
  const [activeModel, setActiveModel] = useState<string>('demo_baseline_v1');
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    api.getModelStatus().then((res) => {
      setStatus(res);
      setThreshold(res.confidence_threshold);
      setActiveModel(res.active_model);
    }).catch(console.error);
  }, []);

  const handleSaveConfig = async () => {
    setIsSaving(true);
    setSaveMessage(null);
    try {
      await api.updateModelConfig({
        active_model: activeModel,
        confidence_threshold: threshold,
      });
      setSaveMessage('Model configuration saved and active.');
    } catch (err) {
      console.error(err);
      setSaveMessage('Failed to update model settings.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!status) {
    return <div className="py-20 text-center text-slate-400">Loading AI Model Registry...</div>;
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
            <Cpu className="w-5 h-5" />
          </span>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">
            AI Model Management & Registry
          </h1>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Inspect inference pipeline status, confidence thresholds, and hot-swap active gesture classifiers.
        </p>
      </div>

      {/* Model Status Card */}
      <div className="glass-card p-6 space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="space-y-1">
            <div className="text-base font-bold text-slate-900 dark:text-white">
              Current Model: {status.active_model}
            </div>
            <div className="text-xs text-slate-400">
              Architecture: {status.model_type}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {status.is_demo_model ? (
              <span className="px-3 py-1 rounded-full bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30 text-xs font-bold flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" /> Demo / Baseline Model
              </span>
            ) : (
              <span className="px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" /> Production Model
              </span>
            )}
          </div>
        </div>

        {/* Status Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-400 font-bold block mb-1">Supported Signs</span>
            <span className="text-base font-black text-slate-800 dark:text-white">
              {status.supported_gestures_count} Gestures
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-400 font-bold block mb-1">Dataset Samples</span>
            <span className="text-base font-black text-slate-800 dark:text-white">
              {status.dataset_samples_count} Frames
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-400 font-bold block mb-1">Version</span>
            <span className="text-base font-black text-slate-800 dark:text-white">
              {status.model_version}
            </span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-400 font-bold block mb-1">Accelerator</span>
            <span className="text-base font-black text-slate-800 dark:text-white truncate">
              {status.hardware_accelerator}
            </span>
          </div>
        </div>

        {/* Configuration Controls */}
        <div className="space-y-5 pt-4 border-t border-slate-100 dark:border-slate-800">
          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 dark:text-slate-400 mb-2">
              Select Active Inference Model:
            </label>
            <select
              value={activeModel}
              onChange={(e) => setActiveModel(e.target.value)}
              className="w-full p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 cursor-pointer"
            >
              <option value="demo_baseline_v1">Demo Baseline Model (Geometric Ensemble & Random Forest)</option>
              <option value="pytorch_lstm_v1">PyTorch Temporal Sequence LSTM (Dynamic Trajectory)</option>
              <option value="custom_user_ensemble">User-Personalized Hybrid Ensemble</option>
            </select>
          </div>

          <div>
            <div className="flex items-center justify-between text-xs font-bold mb-2">
              <span className="uppercase text-slate-500 dark:text-slate-400">
                Confidence Acceptance Threshold:
              </span>
              <span className="text-brand-600 dark:text-brand-400 font-black text-sm">
                {Math.round(threshold * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.30"
              max="0.95"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full accent-brand-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>30% (High Sensitivity)</span>
              <span>65% (Recommended Default)</span>
              <span>95% (High Specificity)</span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            {saveMessage && (
              <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4" /> {saveMessage}
              </span>
            )}
            <button
              onClick={handleSaveConfig}
              disabled={isSaving}
              className="ml-auto px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-xs shadow-md transition-colors disabled:opacity-50"
            >
              {isSaving ? 'Updating...' : 'Save Configuration'}
            </button>
          </div>
        </div>
      </div>

      {/* Production Model Upgrade Guide */}
      <div className="glass-panel p-6 bg-slate-900 text-slate-200 space-y-4 border-slate-800">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <HardDrive className="w-4 h-4 text-teal-400" />
          Production ISL Model Deployment Guide
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          To upgrade this baseline system with a full 10,000+ sample continuous Indian Sign Language (ISL) dataset:
        </p>
        <ol className="list-decimal list-inside space-y-1.5 text-xs text-slate-300">
          <li>Place raw/processed landmark sequence files in <code className="text-teal-300">dataset/processed/</code></li>
          <li>Run <code className="text-teal-300">python ml/training/train_classifier.py</code> to regenerate model weights</li>
          <li>Serialized models will automatically load into <code className="text-teal-300">models/static_gesture_model.pkl</code></li>
        </ol>
      </div>
    </div>
  );
};
