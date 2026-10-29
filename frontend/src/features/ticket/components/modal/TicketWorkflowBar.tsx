import React from 'react';
import {
  ShieldCheck,
  UserCheck,
  UserPlus,
  Play,
  PauseCircle,
  CheckSquare,
  Loader2,
  X,
  ArrowRightLeft,
  Lock,
} from 'lucide-react';
import { OfficerSimpleItem } from '../../types/ticket';
import { TicketWorkflowSubForms } from './actions/TicketWorkflowSubForms';
import { AssignedWorkflowButtons } from './actions/AssignedWorkflowButtons';

interface TicketWorkflowBarProps {
  status: string;
  isOfficer: boolean;
  isOwnerOrAdmin?: boolean;
  isAssignee?: boolean;
  isAdmin?: boolean;
  currentAssigneeName?: string;
  transitioningStatus: string | null;
  onAssignToMe: () => void;
  onStartProgress: () => void;
  officers?: OfficerSimpleItem[];
  showDesignateModal?: boolean;
  onToggleDesignate?: () => void;
  selectedAssignOfficerId?: number | '';
  onSelectAssignOfficer?: (id: number | '') => void;
  assignReason?: string;
  onSetAssignReason?: (val: string) => void;
  submittingDesignate?: boolean;
  designateError?: string;
  onSubmitDesignate?: () => void;
  showPendingModal: boolean;
  onTogglePending: () => void;
  onClosePendingModal: () => void;
  pendingReason: string;
  setPendingReason: (val: string) => void;
  submittingPending: boolean;
  pendingError: string;
  onSubmitPending: (e: React.FormEvent) => void;
  showCloseModal: boolean;
  onOpenClose: () => void;
  onCloseCloseModal: () => void;
  closeNote: string;
  setCloseNote: (val: string) => void;
  submittingClose: boolean;
  closeError: string;
  onSubmitClose: (e: React.FormEvent) => void;
}

export const TicketWorkflowBar: React.FC<TicketWorkflowBarProps> = ({
  status,
  isOfficer,
  isOwnerOrAdmin = true,
  isAssignee = false,
  isAdmin = false,
  currentAssigneeName = '지정 담당자',
  transitioningStatus,
  onAssignToMe,
  onStartProgress,
  officers = [],
  showDesignateModal = false,
  onToggleDesignate = () => {},
  selectedAssignOfficerId = '',
  onSelectAssignOfficer = () => {},
  assignReason = '',
  onSetAssignReason = () => {},
  submittingDesignate = false,
  designateError = '',
  onSubmitDesignate = () => {},
  showPendingModal,
  onTogglePending,
  onClosePendingModal,
  pendingReason,
  setPendingReason,
  submittingPending,
  pendingError,
  onSubmitPending,
  showCloseModal,
  onOpenClose,
  onCloseCloseModal,
  closeNote,
  setCloseNote,
  submittingClose,
  closeError,
  onSubmitClose,
}) => {
  if (!isOfficer || ['closed', 'canceled'].includes(status)) {
    return null;
  }

  const isAssigning = transitioningStatus === 'assign';
  const isStarting = transitioningStatus === 'start-progress';
  const isSubmitted = status === 'submitted';
  const isAssigned = status === 'assigned';
  const isProcessing = ['in_progress', 'pending'].includes(status);

  return (
    <div className="p-3.5 bg-indigo-50/60 border border-indigo-200/80 rounded-xl space-y-2.5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center space-x-1.5 text-xs font-bold text-indigo-900">
          <ShieldCheck className="w-4 h-4 text-indigo-600" />
          <span>IT 담당자 상태 제어 액션</span>
        </div>

        <div className="flex items-center flex-wrap gap-1.5">
          {/* 1. 미배정 접수 상태 */}
          {isSubmitted && (
            <>
              <button
                type="button"
                onClick={onAssignToMe}
                disabled={transitioningStatus !== null || submittingDesignate}
                className="flex items-center px-2.5 py-1 text-xs font-semibold text-blue-700 bg-white border border-blue-300 rounded-lg hover:bg-blue-50 cursor-pointer shadow-xs transition-all disabled:opacity-50"
              >
                {isAssigning ? (
                  <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                ) : (
                  <UserCheck className="w-3.5 h-3.5 mr-1" />
                )}
                내게 배정
              </button>

              <button
                type="button"
                onClick={onToggleDesignate}
                disabled={transitioningStatus !== null || submittingDesignate}
                className="flex items-center px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-white border border-emerald-300 rounded-lg hover:bg-emerald-50 cursor-pointer shadow-xs transition-all disabled:opacity-50"
              >
                <UserPlus className="w-3.5 h-3.5 mr-1" />
                담당자 지정
              </button>
            </>
          )}

          {/* 2. 시작 전 (assigned) */}
          {isAssigned && (
            <AssignedWorkflowButtons
              isOwnerOrAdmin={isOwnerOrAdmin}
              isStarting={isStarting}
              isAssigning={isAssigning}
              transitioningStatus={transitioningStatus}
              currentAssigneeName={currentAssigneeName}
              onStartProgress={onStartProgress}
              onToggleDesignate={onToggleDesignate}
              onAssignToMe={onAssignToMe}
            />
          )}

          {/* 3. 처리 중 (in_progress, pending) */}
          {isProcessing && (
            <>
              {status === 'in_progress' && isOwnerOrAdmin && (
                <button
                  type="button"
                  onClick={onTogglePending}
                  disabled={transitioningStatus !== null}
                  className="flex items-center px-2.5 py-1 text-xs font-semibold text-purple-700 bg-white border border-purple-300 rounded-lg hover:bg-purple-50 cursor-pointer shadow-xs transition-all"
                >
                  <PauseCircle className="w-3.5 h-3.5 mr-1" />
                  답변 대기 요청
                </button>
              )}

              {status === 'pending' && isOwnerOrAdmin && (
                <button
                  type="button"
                  onClick={onStartProgress}
                  disabled={transitioningStatus !== null}
                  className="flex items-center px-2.5 py-1 text-xs font-semibold text-indigo-700 bg-white border border-indigo-300 rounded-lg hover:bg-indigo-50 cursor-pointer shadow-xs transition-all"
                >
                  {isStarting ? (
                    <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                  ) : (
                    <Play className="w-3.5 h-3.5 mr-1" />
                  )}
                  처리 재개 (진행중)
                </button>
              )}

              {isOwnerOrAdmin && (
                <button
                  type="button"
                  onClick={onToggleDesignate}
                  disabled={transitioningStatus !== null}
                  className="flex items-center px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-white border border-emerald-300 rounded-lg hover:bg-emerald-50 cursor-pointer shadow-xs transition-all"
                >
                  <ArrowRightLeft className="w-3.5 h-3.5 mr-1" />
                  담당자 인계
                </button>
              )}
            </>
          )}

          {/* 4. 직권 종결 버튼 */}
          {isOwnerOrAdmin && (
            <button
              type="button"
              onClick={onOpenClose}
              disabled={transitioningStatus !== null}
              className="flex items-center px-2 py-1 text-xs text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-all cursor-pointer"
              title="추가 조치 없이 티켓 직권 종결"
            >
              <Lock className="w-3 h-3 mr-1" />
              직권 종결
            </button>
          )}
        </div>
      </div>

      {/* Sub-Forms */}
      <TicketWorkflowSubForms
        showDesignateModal={showDesignateModal}
        isSubmitted={isSubmitted}
        officers={officers}
        selectedAssignOfficerId={selectedAssignOfficerId}
        onSelectAssignOfficer={onSelectAssignOfficer}
        assignReason={assignReason}
        onSetAssignReason={onSetAssignReason}
        submittingDesignate={submittingDesignate}
        designateError={designateError}
        onToggleDesignate={onToggleDesignate}
        onSubmitDesignate={onSubmitDesignate}
        showPendingModal={showPendingModal}
        pendingReason={pendingReason}
        setPendingReason={setPendingReason}
        submittingPending={submittingPending}
        pendingError={pendingError}
        onClosePendingModal={onClosePendingModal}
        onSubmitPending={onSubmitPending}
        showCloseModal={showCloseModal}
        closeNote={closeNote}
        setCloseNote={setCloseNote}
        submittingClose={submittingClose}
        closeError={closeError}
        onCloseCloseModal={onCloseCloseModal}
        onSubmitClose={onSubmitClose}
      />
    </div>
  );
};
