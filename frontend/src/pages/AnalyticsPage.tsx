import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Activity,
  Cpu,
  Flame,
  Award,
  Zap,
  CheckCircle2
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { api } from '../services/api';
import { AnalyticsData } from '../types';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    api.getAnalytics().then(setData).catch(console.error);
  }, []);

  const COLORS = ['#14b8a6', '#6366f1', '#f59e0b', '#ec4899', '#8b5cf6'];

  if (!data) {
    return <div className="py-20 text-center text-slate-400">Loading analytics metrics...</div>;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-teal-500/10 text-teal-600 dark:text-teal-400">
            <BarChart3 className="w-5 h-5" />
          </span>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">
            Performance Analytics & Insights
          </h1>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Real-time recognition statistics, learning velocity, and neural model latency benchmarks.
        </p>
      </div>

      {/* 1. KEY METRIC CARDS */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase">
            <span>Translations</span>
            <Activity className="w-4 h-4 text-brand-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {data.total_translations}
          </div>
          <div className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1">
            <TrendingUp className="w-3 h-3" /> +18% this week
          </div>
        </div>

        <div className="glass-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase">
            <span>Accuracy</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {data.recognition_accuracy}%
          </div>
          <div className="text-[11px] text-slate-400">Top-1 Model Calibration</div>
        </div>

        <div className="glass-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase">
            <span>Signs Learned</span>
            <Award className="w-4 h-4 text-primary-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {data.signs_learned} Signs
          </div>
          <div className="text-[11px] text-primary-500 font-semibold">Level 3 Master</div>
        </div>

        <div className="glass-card p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase">
            <span>Streak</span>
            <Flame className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            {data.current_streak} Days
          </div>
          <div className="text-[11px] text-amber-500 font-semibold">Active Daily Goal</div>
        </div>
      </div>

      {/* 2. CHARTS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Daily Translations Activity (7 Cols) */}
        <div className="lg:col-span-7 glass-card p-6 space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            Daily Translation Volume & Practice Time
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.daily_activity}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.75rem',
                    color: '#fff',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="translations" fill="#14b8a6" radius={[6, 6, 0, 0]} />
                <Bar dataKey="practice_mins" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Most Used Signs Distribution (5 Cols) */}
        <div className="lg:col-span-5 glass-card p-6 space-y-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            Most Frequent ISL Signs
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.sign_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="count"
                >
                  {data.sign_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.75rem',
                    color: '#fff',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap justify-center gap-3 text-xs">
            {data.sign_distribution.map((item, idx) => (
              <span key={idx} className="flex items-center gap-1.5 font-medium text-slate-600 dark:text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                {item.name} ({item.percentage}%)
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* 3. HARDWARE & LATENCY BENCHMARKS */}
      <div className="glass-card p-6 space-y-4">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-brand-500" />
          Model Engineering & Real-Time Profiling
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-400 font-semibold block">Inference Latency</span>
            <span className="text-lg font-black text-slate-900 dark:text-white">{data.model_metrics.avg_latency_ms} ms</span>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-400 font-semibold block">Operating FPS</span>
            <span className="text-lg font-black text-emerald-500">{data.model_metrics.avg_fps} FPS</span>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-400 font-semibold block">Top-3 Candidate Accuracy</span>
            <span className="text-lg font-black text-slate-900 dark:text-white">{data.model_metrics.top_3_accuracy}%</span>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-400 font-semibold block">Hardware Target</span>
            <span className="text-sm font-bold text-slate-700 dark:text-slate-300">{data.model_metrics.device}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
