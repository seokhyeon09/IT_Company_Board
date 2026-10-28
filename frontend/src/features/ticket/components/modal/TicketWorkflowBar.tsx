import React from 'react';
import {
  ShieldCheck,
  UserCheck,
  Play,
  PauseCircle,
  Ban,
  Loader2,
} from 'lucide-react';

interface TicketWorkflowBarProps {
  status: string;
  isOfficer: boolean;
  transitioningStatus: string | null;
  onAssignToMe: () => void;
  onStartProgress: () => void;
  onOpenPending: () => void;
  onOpenClose: () => void;
}

export const TicketWorkflowBar: React.FC<TicketWorkflowBarProps> = ({
  status,
  isOfficer,
  transitioningStatus,
  onAssignToMe,
  onStartProgress,
  onOpenPending,
  onOpenClose,
}) => {
  if (!isOfficer || ['closed', 'canceled'].includes(status)) {
    return null;
  }

  const isAssigning = transitioningStatus === 'assign';
  const isStarting = transitioningStatus === 'start-progress';

  return (
    <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex flex-wrap items-center justify-between gap-2">
      <div className="flex items-center space-x-1.5">
        <ShieldCheck className="w-4 h-4 text-indigo-600" />
        <span className="text-xs font-bold text-slate-700">담당자 상태 제어:</span>
      </div>

      <div className="flex flex-wrap items-center gap-1.5">
        {status === 'submitted' && (
          <button
            type="button"
            onClick={onAssignToMe}
            disabled={transitioningStatus !== null}
            className="flex items-center px-2.5 py-1 text-xs font-semibold text-blue-700 bg-white border border-blue-300 rounded-lg hover:bg-blue-50 cursor-pointer shadow-2xs transition-all"
          >
            {isAssigning ? (
              <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
            ) : (
              <UserCheck className="w-3.5 h-3.5 mr-1" />
            )}
            내게 배정
          </button>
        )}

        {(status === 'assigned' || status === 'pending') && (
          <button
            type="button"
            onClick={onStartProgress}
            disabled={transitioningStatus !== null}
            className="flex items-center px-2.5 py-1 text-xs font-semibold text-indigo-700 bg-white border border-indigo-300 rounded-lg hover:bg-indigo-50 cursor-pointer shadow-2xs transition-all"
          >
            {isStarting ? (
              <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 mr-1" />
            )}
            처리 시작
          </button>
        )}

        {status === 'in_progress' && (
          <button
            type="button"
            onClick={onOpenPending}
            disabled={transitioningStatus !== null}
            className="flex items-center px-2.5 py-1 text-xs font-semibold text-purple-700 bg-white border border-purple-300 rounded-lg hover:bg-purple-50 cursor-pointer shadow-2xs transition-all"
          >
            <PauseCircle className="w-3.5 h-3.5 mr-1" />
            답변 대기 요청
          </button>
        )}

        <button
          type="button"
          onClick={onOpenClose}
          disabled={transitioningStatus !== null}
          className="flex items-center px-2.5 py-1 text-xs font-semibold text-rose-700 bg-white border border-rose-300 rounded-lg hover:bg-rose-50 cursor-pointer shadow-2xs transition-all"
        >
          <Ban className="w-3.5 h-3.5 mr-1" />
          직권 종결
        </button>
      </div>
    </div>
  );
};
