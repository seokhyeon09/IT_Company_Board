import React from 'react';
import { AlertTriangle, Clock, PauseCircle } from 'lucide-react';
import { formatPausedDuration } from '../../../../../shared/utils/slaUtils';

interface TicketSlaBannerProps {
  deadline?: string | null;
  isOverdue?: boolean;
  slaState?: string;
  pausedSeconds?: number;
  pausedAt?: string | null;
}

export const TicketSlaBanner: React.FC<TicketSlaBannerProps> = ({
  deadline,
  isOverdue,
  slaState,
  pausedSeconds,
  pausedAt,
}) => {
  if (!deadline) return null;

  const isPaused = slaState === 'paused' || Boolean(pausedAt);
  const effectiveOverdue = Boolean(isOverdue) && !isPaused;
  const pausedText =
    pausedSeconds && pausedSeconds >= 60 ? formatPausedDuration(pausedSeconds) : '';

  const containerClass = isPaused
    ? 'bg-slate-50 border-slate-200 text-slate-700'
    : effectiveOverdue
      ? 'bg-rose-50 border-rose-200 text-rose-700'
      : 'bg-amber-50 border-amber-200 text-amber-800';

  return (
    <div
      className={`mt-3 flex items-center justify-between px-3.5 py-2 rounded-xl text-xs border ${containerClass}`}
    >
      <div className="flex items-center font-medium">
        {isPaused ? (
          <>
            <PauseCircle className="w-4 h-4 mr-1.5 text-slate-500" />
            <span>SLA 일시정지 중 (답변 대기)</span>
          </>
        ) : effectiveOverdue ? (
          <>
            <AlertTriangle className="w-4 h-4 mr-1.5 text-rose-600" />
            <span>SLA 조치 기한: {deadline.substring(0, 16).replace('T', ' ')}</span>
          </>
        ) : (
          <>
            <Clock className="w-4 h-4 mr-1.5 text-amber-600" />
            <span>SLA 조치 기한: {deadline.substring(0, 16).replace('T', ' ')}</span>
          </>
        )}
      </div>
      <div className="flex items-center gap-2">
        {pausedText && (
          <span className="text-[11px] font-medium text-slate-600">
            일시정지 누적 {pausedText}
          </span>
        )}
        {effectiveOverdue && (
          <span className="font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded">
            기한 초과
          </span>
        )}
      </div>
    </div>
  );
};
