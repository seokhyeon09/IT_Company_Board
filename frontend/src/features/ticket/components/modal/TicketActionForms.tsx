import React from 'react';
import {
  Star,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Ban,
  PauseCircle,
  HelpCircle,
  MessageSquare,
} from 'lucide-react';
import { TicketDetail } from '../../types/ticket';
import { formatHtmlContent } from '../../../../shared/utils/htmlUtils';

interface TicketActionFormsProps {
  ticket: TicketDetail;
  isOfficer: boolean;
  isAuthor: boolean;

  // Edit resolution
  isEditingResolution: boolean;
  editResolutionNote: string;
  setEditResolutionNote: (val: string) => void;
  submittingEditResolution: boolean;
  editResolutionError: string;
  onCancelEditResolution: () => void;
  onSubmitEditResolution: (e: React.FormEvent) => void;

  // Resolve (new)
  resolutionNote: string;
  setResolutionNote: (val: string) => void;
  submittingResolve: boolean;
  resolveError: string;
  onSubmitResolve: (e: React.FormEvent) => void;

  // Restart inquiry
  showRestartForm: boolean;
  onOpenRestart: () => void;
  onCloseRestart: () => void;
  restartReason: string;
  setRestartReason: (val: string) => void;
  submittingRestart: boolean;
  restartError: string;
  onSubmitRestart: (e: React.FormEvent) => void;

  // Rating
  ratingScore: number;
  setRatingScore: (val: number) => void;
  ratingComment: string;
  setRatingComment: (val: string) => void;
  submittingRating: boolean;
  ratingError: string;
  onSubmitRating: (e: React.FormEvent) => void;

  // Cancel modal
  showCancelModal: boolean;
  onCloseCancelModal: () => void;
  cancelReason: string;
  setCancelReason: (val: string) => void;
  submittingCancel: boolean;
  cancelError: string;
  onSubmitCancel: (e: React.FormEvent) => void;

  // Close modal
  showCloseModal: boolean;
  onCloseCloseModal: () => void;
  closeNote: string;
  setCloseNote: (val: string) => void;
  submittingClose: boolean;
  closeError: string;
  onSubmitClose: (e: React.FormEvent) => void;

  // Pending modal
  showPendingModal: boolean;
  onClosePendingModal: () => void;
  pendingReason: string;
  setPendingReason: (val: string) => void;
  submittingPending: boolean;
  pendingError: string;
  onSubmitPending: (e: React.FormEvent) => void;
}

export const TicketActionForms: React.FC<TicketActionFormsProps> = ({
  ticket,
  isOfficer,
  isAuthor,
  isEditingResolution,
  editResolutionNote,
  setEditResolutionNote,
  submittingEditResolution,
  editResolutionError,
  onCancelEditResolution,
  onSubmitEditResolution,
  resolutionNote,
  setResolutionNote,
  submittingResolve,
  resolveError,
  onSubmitResolve,
  showRestartForm,
  onOpenRestart,
  onCloseRestart,
  restartReason,
  setRestartReason,
  submittingRestart,
  restartError,
  onSubmitRestart,
  ratingScore,
  setRatingScore,
  ratingComment,
  setRatingComment,
  submittingRating,
  ratingError,
  onSubmitRating,
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
  const isResolved = ticket.status === 'resolved';
  const isClosed = ticket.status === 'closed';
  const canResolve =
    isOfficer && ['submitted', 'assigned', 'in_progress'].includes(ticket.status);

  return (
    <div className="space-y-4">
      {/* 1. Edit Resolution Form */}
      {isEditingResolution && (
        <div className="p-4 bg-emerald-50/90 border border-emerald-300 rounded-xl shadow-2xs">
          <div className="text-xs font-bold text-emerald-900 mb-2">최신 조치 내용 수정</div>
          <form onSubmit={onSubmitEditResolution} className="space-y-3">
            <textarea
              value={editResolutionNote}
              onChange={(e) => setEditResolutionNote(e.target.value)}
              placeholder="수정할 조치 내용을 구체적으로 입력해 주세요 (최소 5자 이상)..."
              rows={4}
              required
              className="w-full text-xs p-3 bg-white border border-emerald-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none leading-relaxed"
            />
            {editResolutionError && (
              <p className="text-xs text-rose-600 font-medium">{editResolutionError}</p>
            )}
            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={onCancelEditResolution}
                className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
              >
                취소
              </button>
              <button
                type="submit"
                disabled={submittingEditResolution}
                className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-2xs cursor-pointer"
              >
                {submittingEditResolution && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
                수정 저장
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 2. New Resolution Form (IT Officer) */}
      {canResolve && !isEditingResolution && (
        <div className="p-4 bg-emerald-50/60 border border-emerald-200 rounded-xl space-y-3">
          <div className="flex items-center space-x-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-900">
              IT 담당자 조치 답변 작성
            </h4>
          </div>
          <form onSubmit={onSubmitResolve} className="space-y-3">
            <textarea
              value={resolutionNote}
              onChange={(e) => setResolutionNote(e.target.value)}
              placeholder="요청 사항에 대한 해결 조치 결과 및 안내 사항을 자세히 작성해 주세요..."
              rows={4}
              required
              className="w-full text-xs p-3 bg-white border border-emerald-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none leading-relaxed"
            />
            {resolveError && (
              <p className="text-xs text-rose-600 font-medium">{resolveError}</p>
            )}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={submittingResolve}
                className="flex items-center px-4 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-2xs cursor-pointer transition-colors"
              >
                {submittingResolve && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
                조치 완료 처리
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 3. Employee Follow-up Inquiry Form */}
      {isAuthor && isResolved && (
        <div className="p-4 bg-purple-50/70 border border-purple-200 rounded-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1.5">
              <RotateCcw className="w-4 h-4 text-purple-600" />
              <span className="text-xs font-bold text-purple-900 uppercase tracking-wider">
                추가 재문의가 필요하신가요?
              </span>
            </div>
            {!showRestartForm && (
              <button
                type="button"
                onClick={onOpenRestart}
                className="flex items-center text-xs font-semibold text-purple-700 bg-white border border-purple-300 hover:bg-purple-100/70 px-2.5 py-1 rounded-lg transition-all cursor-pointer shadow-2xs"
              >
                추가 재문의 작성
              </button>
            )}
          </div>

          {showRestartForm && (
            <form onSubmit={onSubmitRestart} className="space-y-3 mt-3">
              <p className="text-xs text-purple-800">
                조치 내용에 미흡한 점이 있거나 추가 문의사항이 있으시면 입력해 주세요. 담당자에게 알림이 전달되며 처리가 다시 시작됩니다.
              </p>
              <textarea
                value={restartReason}
                onChange={(e) => setRestartReason(e.target.value)}
                placeholder="재문의할 내용을 구체적으로 작성해 주세요..."
                rows={3}
                required
                className="w-full text-xs p-2.5 bg-white border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none"
              />
              {restartError && (
                <p className="text-xs text-rose-600 font-medium">{restartError}</p>
              )}
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={onCloseRestart}
                  className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
                >
                  취소
                </button>
                <button
                  type="submit"
                  disabled={submittingRestart}
                  className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-purple-600 hover:bg-purple-700 rounded-lg shadow-2xs cursor-pointer"
                >
                  {submittingRestart && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
                  재문의 등록
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* Closed Ticket Notice */}
      {isClosed && (
        <div className="p-3 bg-slate-100 border border-slate-200 rounded-xl text-center text-xs text-slate-500 font-medium">
          본 문의는 최종 종결 처리되어 추가 재문의가 불가합니다.
        </div>
      )}

      {/* 4. Rating Form */}
      {isResolved && isAuthor && (!ticket.rating || ticket.rating === '0') && (
        <div className="p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl">
          <div className="flex items-center space-x-1.5 mb-2">
            <Star className="w-4 h-4 text-indigo-600 fill-indigo-500" />
            <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
              조치 만족도 평가 (평가 시 최종 종결)
            </h4>
          </div>
          <form onSubmit={onSubmitRating} className="space-y-3">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-medium text-slate-600">만족도 점수:</span>
              <div className="flex space-x-1">
                {[1, 2, 3, 4, 5].map((score) => (
                  <button
                    key={score}
                    type="button"
                    onClick={() => setRatingScore(score)}
                    className="p-1 text-amber-400 hover:scale-110 transition-transform cursor-pointer"
                  >
                    <Star
                      className={`w-5 h-5 ${
                        score <= ratingScore ? 'fill-amber-400 text-amber-400' : 'text-slate-300'
                      }`}
                    />
                  </button>
                ))}
              </div>
              <span className="text-xs font-bold text-indigo-700 ml-1">{ratingScore}점</span>
            </div>

            <textarea
              value={ratingComment}
              onChange={(e) => setRatingComment(e.target.value)}
              placeholder="처리 과정에 대한 소감이나 의견을 남겨주세요 (선택사항)..."
              rows={2}
              className="w-full text-xs p-2.5 bg-white border border-indigo-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
            />
            {ratingError && (
              <p className="text-xs text-rose-600 font-medium">{ratingError}</p>
            )}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={submittingRating}
                className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-2xs cursor-pointer"
              >
                {submittingRating && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
                평가 제출 및 문의 종결
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Existing Rating Display */}
      {ticket.rating && ticket.rating !== '0' && (
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-700">사원 만족도 평가:</span>
            <div className="flex text-amber-400">
              {Array.from({ length: Number(ticket.rating) || 5 }).map((_, i) => (
                <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
              ))}
            </div>
            <span className="font-bold text-slate-800">{ticket.rating}점</span>
          </div>
          {ticket.rating_comment && (
            <span className="text-slate-500 italic max-w-xs truncate" title={ticket.rating_comment}>
              &quot;{ticket.rating_comment}&quot;
            </span>
          )}
        </div>
      )}

      {/* Cancel Confirmation Modal */}
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

      {/* Force Close Modal (Officer) */}
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

      {/* Pending Modal (Officer) */}
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
    </div>
  );
};
