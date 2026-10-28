import React from 'react';
import { RotateCcw, MessageSquare, CheckCircle2, Loader2 } from 'lucide-react';
import { ThreadItem } from '../../../types/ticket';

interface RestartInquiryFormProps {
  isAuthor: boolean;
  isResolved: boolean;
  isClosed: boolean;
  timeline?: ThreadItem[];
  showRestartForm: boolean;
  onOpenRestart: () => void;
  onCloseRestart: () => void;
  restartReason: string;
  setRestartReason: (val: string) => void;
  submittingRestart: boolean;
  restartError: string;
  onSubmitRestart: (e: React.FormEvent) => void;
}

export const RestartInquiryForm: React.FC<RestartInquiryFormProps> = ({
  isAuthor,
  isResolved,
  isClosed,
  timeline,
  showRestartForm,
  onOpenRestart,
  onCloseRestart,
  restartReason,
  setRestartReason,
  submittingRestart,
  restartError,
  onSubmitRestart,
}) => {
  const nextInquiryRound =
    (timeline?.filter((t) => t.type === 'inquiry').length || 1) + 1;

  return (
    <>
      {isAuthor && isResolved && (
        <div className="p-4 bg-purple-50/70 border border-purple-200 rounded-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1.5">
              <RotateCcw className="w-4 h-4 text-purple-600" />
              <span className="text-xs font-bold text-purple-900 uppercase tracking-wider">
                추가 문의하기 (문의 {nextInquiryRound}차)
              </span>
            </div>
            {!showRestartForm && (
              <button
                type="button"
                onClick={onOpenRestart}
                className="flex items-center px-3 py-1.5 text-xs font-semibold text-purple-700 bg-white border border-purple-300 rounded-lg hover:bg-purple-100/50 transition-all cursor-pointer shadow-xs"
              >
                <MessageSquare className="w-3.5 h-3.5 mr-1" />
                추가 문의하기 (문의 {nextInquiryRound}차)
              </button>
            )}
          </div>

          {showRestartForm ? (
            <form onSubmit={onSubmitRestart} className="space-y-3 mt-3">
              <p className="text-xs text-purple-800">
                조치 내용에 대해 미해결된 사항이나 추가 문의사항을 남겨주시면 담당자에게 재배정되어 처리가 다시 시작됩니다.
              </p>
              <textarea
                rows={3}
                value={restartReason}
                onChange={(e) => setRestartReason(e.target.value)}
                placeholder="추가 문의하실 상세 내용을 입력하세요 (최소 5자)..."
                className="w-full px-3.5 py-2.5 text-xs border border-purple-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none text-slate-800"
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
                  className="flex items-center px-4 py-1.5 text-xs font-semibold text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-all cursor-pointer"
                >
                  {submittingRestart ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                      등록 중...
                    </>
                  ) : (
                    '재문의 등록'
                  )}
                </button>
              </div>
            </form>
          ) : (
            <p className="text-xs text-purple-700 mt-1">
              조치 결과에 대해 추가 확인이 필요한 경우 재문의를 통해 다시 처리를 요청하실 수 있습니다.
            </p>
          )}
        </div>
      )}

      {isClosed && (
        <div className="p-3.5 bg-slate-100 border border-slate-200 rounded-xl text-slate-600 text-xs flex items-center">
          <CheckCircle2 className="w-4 h-4 mr-2 text-slate-500 shrink-0" />
          <span>본 문의는 최종 종결 처리되어 추가 재문의가 불가합니다.</span>
        </div>
      )}
    </>
  );
};
