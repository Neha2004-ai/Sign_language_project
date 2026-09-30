import React from 'react';
import { AlertCircle, CheckCircle2, AlertTriangle } from 'lucide-react';

interface ConfidenceMeterProps {
  confidence: number; // 0.0 to 1.0
  threshold?: number;
  showDetails?: boolean;
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({
  confidence,
  threshold = 0.65,
  showDetails = true,
}) => {
  const percentage = Math.min(Math.max(Math.round(confidence * 100), 0), 100);

  let status: 'high' | 'medium' | 'low' = 'low';
  let colorClass = 'bg-rose-500';
  let badgeClass = 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-900/50';
  let statusText = 'Low Confidence';
  let StatusIcon = AlertCircle;

  if (confidence >= 0.80) {
    status = 'high';
    colorClass = 'bg-emerald-500';
    badgeClass = 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50';
    statusText = 'High Confidence';
    StatusIcon = CheckCircle2;
  } else if (confidence >= threshold) {
    status = 'medium';
    colorClass = 'bg-amber-500';
    badgeClass = 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-900/50';
    statusText = 'Medium Confidence';
    StatusIcon = AlertTriangle;
  }

  return (
    <div className="space-y-1.5 w-full">
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-slate-500 dark:text-slate-400">
          Model Confidence
        </span>
        <div className="flex items-center space-x-1.5">
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${badgeClass}`}>
            <StatusIcon className="w-3 h-3" />
            {statusText}
          </span>
          <span className="font-bold text-slate-800 dark:text-slate-200 text-sm">
            {percentage}%
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-slate-200 dark:bg-slate-800 h-2.5 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-300 rounded-full ${colorClass}`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {showDetails && status === 'low' && (
        <p className="text-[11px] text-amber-600 dark:text-amber-400 flex items-center gap-1 mt-1">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          Low confidence – please reposition your hand clearly in frame.
        </p>
      )}
    </div>
  );
};
