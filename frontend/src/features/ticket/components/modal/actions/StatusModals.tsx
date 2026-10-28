import React from 'react';
import { Ban, PauseCircle, Loader2 } from 'lucide-react';

interface StatusModalsProps {
  // Cancel
  showCancelModal: boolean;
  onCloseCancelModal: () => void;
  cancelReason: string;
  setCancelReason: (val: string) => void;
  submittingCancel: boolean;
  cancelError: string;
  onSubmitCancel: (e: React.FormEvent) => void;

  // Close
  showCloseModal: boolean;
  onCloseCloseModal: () => void;
  closeNote: string;
  setCloseNote: (val: string) => void;
  submittingClose: boolean;
  closeError: string;
  onSubmitClose: (e: React.FormEvent) => void;

  // Pending
  showPendingModal: boolean;
  onClosePendingModal: () => void;
  pendingReason: string;
  setPendingReason: (val: string) => void;
  submittingPending: boolean;
  pendingError: string;
  onSubmitPending: (e: React.FormEvent) => void;
}

export const StatusModals: React.FC<StatusModalsProps> = ({
  showCancelModal,
  onCloseCancelModal,
  cancelReason,
  setCancelReason,
  submittingCancel,
  cancelError,
  onSubmitCancel,
  showCloseModal,
  onCloseCloseModal,
  closeNote,
  setCloseNote,
  submittingClose,
  closeError,
  onSubmitClose,
  showPendingModal,
  onClosePendingModal,
  pendingReason,
  setPendingReason,
  submittingPending,
  pendingError,
  onSubmitPending,
}) => {
  return (
    <>
      {/* 1. Cancel Confirmation Modal */}
      {showCancelModal && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl space-y-3">
          <div className="flex items-center space-x-1.5 text-rose-800 font-bold text-xs">
            <Ban className="w-4 h-4 text-rose-600" />
            <span>정말 본 문의를 취소하시겠습니까?</span>
          </div>
          <form onSubmit={onSubmitCancel} className="space-y-2">
            <textarea
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              placeholder="문의 취소 사유를 입력해 주세요 (선택)..."
              rows={2}
              className="w-full text-xs p-2 bg-white border border-rose-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-400 resize-none"
            />
            {cancelError && <p className="text-xs text-rose-600">{cancelError}</p>}
            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={onCloseCancelModal}
                className="px-2.5 py-1 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
              >
                닫기
              </button>
              <button
                type="submit"
                disabled={submittingCancel}
                className="flex items-center px-3 py-1 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 rounded-lg cursor-pointer"
              >
                {submittingCancel && <Loader2 className="w-3 h-3 mr-1 animate-spin" />}
                취소 확정
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 2. Force Close Modal (Officer) */}
      {showCloseModal && (
        <div className="p-4 bg-slate-100 border border-slate-300 rounded-xl space-y-3">
          <div className="flex items-center space-x-1.5 text-slate-800 font-bold text-xs">
            <Ban className="w-4 h-4 text-slate-600" />
            <span>문의 직권 종결 처리</span>
          </div>
          <form onSubmit={onSubmitClose} className="space-y-2">
            <textarea
              value={closeNote}
              onChange={(e) => setCloseNote(e.target.value)}
              placeholder="직권 종결 사유를 입력해 주세요..."
              rows={2}
              className="w-full text-xs p-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-400 resize-none"
            />
            {closeError && <p className="text-xs text-rose-600">{closeError}</p>}
            <div className="flex justify-end space-x-2">
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
                className="flex items-center px-3 py-1 text-xs font-semibold text-white bg-slate-700 hover:bg-slate-800 rounded-lg cursor-pointer"
              >
                {submittingClose && <Loader2 className="w-3 h-3 mr-1 animate-spin" />}
                종결 확정
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 3. Pending Modal (Officer) */}
      {showPendingModal && (
        <div className="p-4 bg-purple-50 border border-purple-200 rounded-xl space-y-3">
          <div className="flex items-center space-x-1.5 text-purple-900 font-bold text-xs">
            <PauseCircle className="w-4 h-4 text-purple-600" />
            <span>답변 대기 요청 사유 입력</span>
          </div>
          <form onSubmit={onSubmitPending} className="space-y-2">
            <textarea
              value={pendingReason}
              onChange={(e) => setPendingReason(e.target.value)}
              placeholder="사원에게 요청할 추가 정보나 확인 사항을 입력해 주세요..."
              rows={2}
              required
              className="w-full text-xs p-2 bg-white border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none"
            />
            {pendingError && <p className="text-xs text-rose-600">{pendingError}</p>}
            <div className="flex justify-end space-x-2">
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
                className="flex items-center px-3 py-1 text-xs font-semibold text-white bg-purple-600 hover:bg-purple-700 rounded-lg cursor-pointer"
              >
                {submittingPending && <Loader2 className="w-3 h-3 mr-1 animate-spin" />}
                대기 요청 확정
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
};
