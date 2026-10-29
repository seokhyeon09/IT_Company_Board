import React from 'react';
import { AlertTriangle, Clock } from 'lucide-react';

interface TicketSlaBannerProps {
  deadline?: string | null;
  isOverdue?: boolean;
}

export const TicketSlaBanner: React.FC<TicketSlaBannerProps> = ({
  deadline,
  isOverdue,
}) => {
  if (!deadline) return null;

  return (
    <div
      className={`mt-3 flex items-center justify-between px-3.5 py-2 rounded-xl text-xs border ${
        isOverdue
          ? 'bg-rose-50 border-rose-200 text-rose-700'
          : 'bg-amber-50 border-amber-200 text-amber-800'
      }`}
    >
      <div className="flex items-center font-medium">
        {isOverdue ? (
          <AlertTriangle className="w-4 h-4 mr-1.5 text-rose-600" />
        ) : (
          <Clock className="w-4 h-4 mr-1.5 text-amber-600" />
        )}
        <span>SLA 조치 기한: {deadline.substring(0, 16).replace('T', ' ')}</span>
      </div>
      {isOverdue && (
        <span className="font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded">
          기한 초과
        </span>
      )}
    </div>
  );
};
