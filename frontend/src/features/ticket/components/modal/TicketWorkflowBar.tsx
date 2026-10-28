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
} from 'lucide-react';
import { OfficerSimpleItem } from '../../types/ticket';

interface TicketWorkflowBarProps {
  status: string;
  isOfficer: boolean;
  transitioningStatus: string | null;
  onAssignToMe: () => void;
  onStartProgress: () => void;
  // Designation
  officers?: OfficerSimpleItem[];
  showDesignateModal?: boolean;
  onToggleDesignate?: () => void;
  selectedAssignOfficerId?: number | '';
  onSelectAssignOfficer?: (id: number | '') => void;
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
  transitioningStatus,
  onAssignToMe,
  onStartProgress,
  officers = [],
  showDesignateModal = false,
  onToggleDesignate,
  selectedAssignOfficerId = '',
  onSelectAssignOfficer,
  submittingDesignate = false,
  designateError = '',
  onSubmitDesignate,
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

  return (
    <div className="p-3.5 bg-indigo-50/60 border border-indigo-200/80 rounded-xl space-y-2.5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center space-x-1.5 text-xs font-bold text-indigo-900">
          <ShieldCheck className="w-4 h-4 text-indigo-600" />
          <span>IT 담당자 상태 제어 액션</span>
        </div>

        <div className="flex items-center flex-wrap gap-1.5">
          {status === 'submitted' && (
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

          {['assigned', 'pending'].includes(status) && (
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
              처리 시작
            </button>
          )}

          {status === 'in_progress' && (
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

          {['in_progress', 'resolved'].includes(status) && (
            <button
              type="button"
              onClick={onOpenClose}
              disabled={transitioningStatus !== null}
              className="flex items-center px-2.5 py-1 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 cursor-pointer shadow-xs transition-all"
            >
              <CheckSquare className="w-3.5 h-3.5 mr-1" />
              직권 종결
            </button>
          )}
        </div>
      </div>

      {/* 담당자 지정 배정 인라인 폼 */}
      {showDesignateModal && status === 'submitted' && (
        <div className="mt-2 pt-2.5 border-t border-indigo-200/60 animate-in fade-in">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-bold text-slate-800">배정할 IT 담당자 선택</span>
            {onToggleDesignate && (
              <button
                type="button"
                onClick={onToggleDesignate}
                className="text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <div className="flex items-center gap-2">
            <select
              value={selectedAssignOfficerId}
              onChange={(e) => onSelectAssignOfficer?.(e.target.value ? Number(e.target.value) : '')}
              className="flex-1 px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500 bg-white text-slate-800"
            >
              <option value="">담당자를 선택하세요</option>
              {officers.map((officer) => (
                <option key={officer.id} value={officer.id}>
                  {officer.name} ({officer.login})
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={onSubmitDesignate}
              disabled={!selectedAssignOfficerId || submittingDesignate}
              className="flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 cursor-pointer disabled:opacity-50 transition-all shrink-0"
            >
              {submittingDesignate ? (
                <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
              ) : null}
              배정 완료
            </button>
          </div>
          {designateError && (
            <div className="mt-1 text-xs text-rose-600">{designateError}</div>
          )}
        </div>
      )}

      {/* 직권 종결 인라인 사유 폼 */}
      {showCloseModal && (
        <div className="mt-2 pt-2.5 border-t border-indigo-200/60 animate-in fade-in">
          <div className="text-xs font-bold text-slate-800 mb-1.5">직권 종결 처리 사유</div>
          <form onSubmit={onSubmitClose} className="space-y-2">
            <textarea
              rows={2}
              value={closeNote}
              onChange={(e) => setCloseNote(e.target.value)}
              placeholder="직권 종결 사유를 입력하세요 (미입력 시 기본 문구가 반영됩니다)..."
              className="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none text-slate-800"
            />
            {closeError && <p className="text-xs text-rose-600 font-medium">{closeError}</p>}
            <div className="flex justify-end space-x-1.5">
              <button
                type="button"
                onClick={onCloseCloseModal}
                className="px-2.5 py-1 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
              >
                취소
              </button>
              <button
                type="submit"
                disabled={submittingClose}
                className="px-3.5 py-1 text-xs font-semibold text-white bg-slate-700 rounded-lg hover:bg-slate-800 disabled:opacity-50 cursor-pointer"
              >
                {submittingClose ? '종결 중...' : '직권 종결 확정'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 답변 대기 요청 인라인 사유 폼 */}
      {showPendingModal && (
        <div className="mt-2 pt-2.5 border-t border-purple-200 animate-in fade-in">
          <div className="text-xs font-bold text-purple-900 mb-1.5">답변 대기 요청 사유 입력</div>
          <form onSubmit={onSubmitPending} className="space-y-2">
            <textarea
              rows={2}
              value={pendingReason}
              onChange={(e) => setPendingReason(e.target.value)}
              placeholder="요청 직원에게 전달할 답변 대기 사유를 입력하세요 (예: 재현 환경, 스크린샷, 오류 로그 요청 등)..."
              className="w-full px-3 py-2 text-xs border border-purple-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none text-slate-800"
            />
            {pendingError && <p className="text-xs text-rose-600 font-medium">{pendingError}</p>}
            <div className="flex justify-end space-x-1.5">
              <button
                type="button"
                onClick={onClosePendingModal}
                className="px-2.5 py-1 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
              >
                취소
              </button>
              <button
                type="submit"
                disabled={submittingPending}
                className="px-3.5 py-1 text-xs font-semibold text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 cursor-pointer shadow-xs"
              >
                {submittingPending ? '요청 처리 중...' : '답변 대기 전환 확정'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
