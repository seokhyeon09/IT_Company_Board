import React from 'react';
import { Play, Loader2, ArrowRightLeft, UserCheck } from 'lucide-react';

interface AssignedWorkflowButtonsProps {
  isOwnerOrAdmin: boolean;
  isStarting: boolean;
  isAssigning: boolean;
  transitioningStatus: string | null;
  currentAssigneeName: string;
  onStartProgress: () => void;
  onToggleDesignate: () => void;
  onAssignToMe: () => void;
}

export const AssignedWorkflowButtons: React.FC<AssignedWorkflowButtonsProps> = ({
  isOwnerOrAdmin,
  isStarting,
  isAssigning,
  transitioningStatus,
  currentAssigneeName,
  onStartProgress,
  onToggleDesignate,
  onAssignToMe,
}) => {
  if (isOwnerOrAdmin) {
    return (
      <>
        <button
          type="button"
          onClick={onStartProgress}
          disabled={transitioningStatus !== null}
          className="flex items-center px-3 py-1 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 cursor-pointer shadow-xs transition-all disabled:opacity-50"
        >
          {isStarting ? (
            <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
          ) : (
            <Play className="w-3.5 h-3.5 mr-1" />
          )}
          처리 시작
        </button>
        <button
          type="button"
          onClick={onToggleDesignate}
          disabled={transitioningStatus !== null}
          className="flex items-center px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-white border border-emerald-300 rounded-lg hover:bg-emerald-50 cursor-pointer shadow-xs transition-all"
        >
          <ArrowRightLeft className="w-3.5 h-3.5 mr-1" />
          담당자 인계
        </button>
      </>
    );
  }

  return (
    <>
      <span className="text-xs text-slate-500 mr-1">
        담당자: <span className="font-semibold text-slate-700">{currentAssigneeName}</span>
      </span>
      <button
        type="button"
        onClick={onAssignToMe}
        disabled={transitioningStatus !== null}
        className="flex items-center px-2.5 py-1 text-xs font-semibold text-blue-700 bg-white border border-blue-300 rounded-lg hover:bg-blue-50 cursor-pointer shadow-xs transition-all"
      >
        {isAssigning ? (
          <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
        ) : (
          <UserCheck className="w-3.5 h-3.5 mr-1" />
        )}
        내가 대신 맡기
      </button>
      <button
        type="button"
        onClick={onToggleDesignate}
        disabled={transitioningStatus !== null}
        className="flex items-center px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-white border border-emerald-300 rounded-lg hover:bg-emerald-50 cursor-pointer shadow-xs transition-all"
      >
        <ArrowRightLeft className="w-3.5 h-3.5 mr-1" />
        다른 담당자로 변경
      </button>
    </>
  );
};
